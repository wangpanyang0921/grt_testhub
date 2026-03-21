"""
UI自动化测试执行服务
支持 Playwright 和 Selenium 测试引擎
"""
import time
import json
from datetime import datetime
from django.utils import timezone
from django.db import connection

from .models import (
    TestSuite, TestExecution, TestCase, TestCaseStep,
    TestCaseExecution, Element, TestScript, ScriptStep
)
from .variable_resolver import resolve_variables

# 延迟导入浏览器驱动，避免在模块加载时就导入
def _import_playwright():
    """延迟导入 Playwright"""
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError as e:
        raise ImportError(
            "Playwright 模块未正确安装。请运行: pip install playwright && playwright install"
        ) from e

def _import_selenium():
    """延迟导入 Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.safari.options import Options as SafariOptions
        from selenium.webdriver.edge.options import Options as EdgeOptions
        return {
            'webdriver': webdriver,
            'By': By,
            'WebDriverWait': WebDriverWait,
            'EC': EC,
            'ChromeOptions': ChromeOptions,
            'FirefoxOptions': FirefoxOptions,
            'SafariOptions': SafariOptions,
            'EdgeOptions': EdgeOptions
        }
    except ImportError as e:
        raise ImportError(
            "Selenium 模块未正确安装。请运行: pip install selenium"
        ) from e



class TestExecutor:
    """测试执行器基类"""

    def __init__(self, test_suite, engine='playwright', browser='chrome', headless=False, executed_by=None):
        self.test_suite = test_suite
        self.engine = engine
        self.browser = browser
        self.headless = headless
        self.executed_by = executed_by
        self.execution = None
        self.test_cases = []
        self.scripts = []
        self.results = []

    def create_execution_record(self):
        """创建测试执行记录"""
        self.execution = TestExecution.objects.create(
            project=self.test_suite.project,
            test_suite=self.test_suite,
            status='RUNNING',
            engine=self.engine,
            browser=self.browser,
            headless=self.headless,
            executed_by=self.executed_by,
            started_at=timezone.now()
        )
        return self.execution

    def update_execution_result(self, status, passed=0, failed=0, skipped=0, duration=0, error_msg=''):
        """更新执行结果"""
        self.execution.status = status
        self.execution.passed_cases = passed
        self.execution.failed_cases = failed
        self.execution.skipped_cases = skipped
        self.execution.total_cases = passed + failed + skipped
        self.execution.duration = duration
        self.execution.finished_at = timezone.now()
        self.execution.error_message = error_msg
        self.execution.result_data = {
            'test_cases': self.results,
            'summary': {
                'total': self.execution.total_cases,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'pass_rate': round((passed / self.execution.total_cases * 100) if self.execution.total_cases > 0 else 0, 2)
            }
        }
        self.execution.save()

        # 更新套件统计
        self.test_suite.passed_count = passed
        self.test_suite.failed_count = failed
        self.test_suite.execution_status = 'passed' if failed == 0 and passed > 0 else 'failed'
        self.test_suite.save()

    def get_test_cases(self):
        """获取测试套件中的所有测试用例"""
        suite_test_cases = self.test_suite.suite_test_cases.select_related('test_case').order_by('order')
        self.test_cases = [stc.test_case for stc in suite_test_cases]
        print(f"从套件 '{self.test_suite.name}' 获取到 {len(self.test_cases)} 个测试用例")
        for i, tc in enumerate(self.test_cases, 1):
            print(f"  {i}. {tc.name} (ID: {tc.id})")
        return self.test_cases

    def get_scripts(self):
        """获取测试套件中的所有脚本"""
        suite_scripts = self.test_suite.suite_scripts.select_related('test_script').order_by('order')
        self.scripts = [ss.test_script for ss in suite_scripts]
        print(f"从套件 '{self.test_suite.name}' 获取到 {len(self.scripts)} 个脚本")
        for i, script in enumerate(self.scripts, 1):
            print(f"  {i}. {script.name} (ID: {script.id}, 类型：{script.script_type}, 语言：{script.language})")
        return self.scripts

    def run(self):
        """执行测试套件"""
        try:
            # 设置环境变量，允许在后台线程中使用同步 ORM
            # 这对于 Playwright 执行是必需的
            import os
            os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
            
            # 关闭当前线程的数据库连接，避免线程间共享
            connection.close()

            # 创建执行记录
            self.create_execution_record()

            # 获取测试用例和脚本
            self.get_test_cases()
            self.get_scripts()

            # 根据引擎选择执行方式
            if self.engine == 'playwright':
                self.run_with_playwright()
            else:
                self.run_with_selenium()

        except Exception as e:
            print(f"测试执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            if self.execution:
                self.update_execution_result(
                    status='FAILED',
                    error_msg=f"执行失败: {str(e)}"
                )
        finally:
            # 确保关闭数据库连接
            connection.close()

    def run_with_playwright(self):
        """使用 Playwright 执行测试（同步版本）"""
        start_time = time.time()
        passed = 0
        failed = 0
        skipped = 0
        
        # 检查 Playwright 是否可用（使用延迟导入）
        try:
            sync_playwright = _import_playwright()
        except ImportError as e:
            error_msg = (
                f"Playwright 模块未正确安装或 Django 服务器未在虚拟环境中运行。\n\n"
                f"请确保：\n"
                f"1. 已在虚拟环境中安装: pip install playwright\n"
                f"2. 已安装浏览器: playwright install\n"
                f"3. Django 服务器在虚拟环境中运行\n\n"
                f"详细错误: {str(e)}"
            )
            print(f"❌ {error_msg}")
            
            # 更新套件执行状态
            if self.execution:
                self.update_execution_result(
                    status='FAILED',
                    failed=len(self.test_cases),
                    error_msg=error_msg
                )
            
            # 更新所有用例状态为失败
            for test_case in self.test_cases:
                TestCaseExecution.objects.filter(
                    test_case=test_case,
                    test_suite=self.test_suite,
                    status='pending'
                ).update(
                    status='failed',
                    error_message=error_msg,
                    finished_at=timezone.now()
                )
            
            return

        # 预先获取所有脚本数据，避免在 Playwright 上下文中访问 ORM
        scripts_data = []
        for test_script in self.scripts:
            script_data = {
                'id': test_script.id,
                'name': test_script.name,
                'project_id': self.test_suite.project.id,
                'script_type': test_script.script_type,
                'language': test_script.language,
                'framework': test_script.framework,
                'content': test_script.content,
                'steps': []
            }
            
            # 如果是低代码脚本，获取步骤数据
            if test_script.script_type in ['LOW_CODE', '低代码']:
                steps = test_script.steps.select_related('target_element', 'target_element__locator_strategy').order_by('step_order')
                for step in steps:
                    step_data = {
                        'id': step.id,
                        'step_order': step.step_order,
                        'action_type': step.action_type,
                        'description': step.description,
                        'expected_result': step.expected_result,
                        'action_params': step.action_params,
                        'wait_before': step.wait_before,
                        'wait_after': step.wait_after,
                        'element': None
                    }
                    
                    # 如果有目标元素，预先获取元素数据
                    if step.target_element:
                        step_data['element'] = {
                            'id': step.target_element.id,
                            'name': step.target_element.name,
                            'locator_value': step.target_element.locator_value,
                            'locator_strategy': step.target_element.locator_strategy.name if step.target_element.locator_strategy else 'css'
                        }
                    
                    script_data['steps'].append(step_data)
            
            scripts_data.append(script_data)
        
        # 预先获取所有测试用例的步骤数据，避免在 Playwright 上下文中访问 ORM
        test_cases_data = []
        for test_case in self.test_cases:
            case_data = {
                'id': test_case.id,
                'name': test_case.name,
                'project_id': self.test_suite.project.id,
                'steps': []
            }

            # 获取步骤并预先加载所有相关数据
            steps = test_case.steps.select_related('element', 'element__locator_strategy').order_by('step_number')
            for step in steps:
                step_data = {
                    'id': step.id,
                    'step_number': step.step_number,
                    'action_type': step.action_type,
                    'description': step.description,
                    'input_value': step.input_value,
                    'wait_time': step.wait_time,
                    'assert_type': step.assert_type,
                    'assert_value': step.assert_value,
                    'element': None
                }

                # 如果有元素，预先获取元素数据
                if step.element:
                    step_data['element'] = {
                        'id': step.element.id,
                        'name': step.element.name,
                        'locator_value': step.element.locator_value,
                        'locator_strategy': step.element.locator_strategy.name if step.element.locator_strategy else 'css'
                    }

                case_data['steps'].append(step_data)

            test_cases_data.append(case_data)

        # 预先创建所有测试用例执行记录（不设置 started_at，等实际执行时再设置）
        case_executions = {}
        for case_data in test_cases_data:
            case_execution = TestCaseExecution.objects.create(
                test_case_id=case_data['id'],
                project_id=case_data['project_id'],
                test_suite=self.test_suite,
                execution_source='suite',
                status='pending',  # 初始状态为 pending
                engine=self.engine,
                browser=self.browser,
                headless=self.headless,
                created_by=self.executed_by
                # 注意：不设置 started_at，等用例实际开始执行时再设置
            )
            case_executions[case_data['id']] = case_execution

        # 执行测试用例，复用浏览器实例和页面
        total_items = len(scripts_data) + len(test_cases_data)
        print(f"准备执行 {total_items} 个项目（{len(scripts_data)} 个脚本，{len(test_cases_data)} 个测试用例）")

        with sync_playwright() as p:
            browser = None
            context = None
            page = None
            
            try:
                # 尝试使用系统已安装的Chrome浏览器，避免权限问题
                import subprocess
                import os
                chrome_path = None
                
                # 查找系统中已安装的Chrome浏览器
                if self.browser != 'firefox' and self.browser != 'safari':
                    try:
                        # 在macOS上查找Chrome
                        chrome_path = subprocess.check_output(['which', 'google-chrome']).decode('utf-8').strip()
                    except:
                        try:
                            # 查找Chrome的另一个常见路径
                            chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                            if not os.path.exists(chrome_path):
                                chrome_path = None
                        except:
                            pass
                
                # 选择浏览器
                if self.browser == 'firefox':
                    browser = p.firefox.launch(
                        headless=self.headless,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-gpu',
                            '--disable-dev-shm-usage',
                            '--disable-background-networking'
                        ]
                    )
                elif self.browser == 'safari':
                    browser = p.webkit.launch(
                        headless=self.headless,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-gpu',
                            '--disable-dev-shm-usage'
                        ]
                    )
                else:  # chrome or edge
                    # 添加防检测和稳定性参数
                    launch_options = {
                        'headless': self.headless,
                        'args': [
                            '--disable-blink-features=AutomationControlled',  # 避免被检测
                            '--no-crashpad',  # 禁用Crashpad，避免权限问题
                            '--disable-gpu',  # 禁用GPU加速
                            '--disable-dev-shm-usage',  # 禁用/dev/shm使用，避免内存问题
                            '--disable-background-networking',  # 禁用后台网络
                            '--disable-component-update',  # 禁用组件更新
                            '--disable-default-apps',  # 禁用默认应用
                            '--disable-extensions',  # 禁用扩展
                            '--disable-notifications',  # 禁用通知
                            '--no-first-run',  # 不运行首次启动
                            '--no-service-autorun',  # 不自动运行服务
                        ]
                    }
                    
                    # 如果找到系统Chrome，使用它
                    if chrome_path:
                        launch_options['executable_path'] = chrome_path
                    
                    browser = p.chromium.launch(**launch_options)

                print(f"✓ 浏览器已启动")

                # 配置上下文（User Agent 和 Viewport）
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                )
                
                # 创建单个页面用于所有测试用例
                page = context.new_page()
                
                # 导航到项目基础URL（只在开始时执行一次）
                if self.test_suite.project.base_url:
                    try:
                        print(f"正在导航到: {self.test_suite.project.base_url}")

                        # 检测是否在Linux服务器环境
                        import platform
                        is_linux = platform.system() == 'Linux'

                        # 使用 networkidle 等待页面加载完成
                        page.goto(self.test_suite.project.base_url, wait_until='networkidle', timeout=30000)

                        # 额外等待，确保动态内容加载（Vue/React等SPA应用）
                        # 服务器无头模式需要更长的等待时间
                        extra_wait = 3 if is_linux else 2
                        time.sleep(extra_wait)

                        print(f"✓ 成功导航到: {self.test_suite.project.base_url} (已等待页面加载完成，额外{extra_wait}秒)")
                    except Exception as e:
                        print(f"✗ 导航失败: {str(e)}")
                        # 导航失败，记录所有用例为失败
                        for case_data in test_cases_data:
                            self.results.append({
                                'test_case_id': case_data['id'],
                                'test_case_name': case_data['name'],
                                'status': 'failed',
                                'steps': [],
                                'error': f"导航到基础URL失败: {str(e)}",
                                'start_time': datetime.now().isoformat(),
                                'end_time': datetime.now().isoformat(),
                                'screenshots': []
                            })
                            failed += 1
                            
                            # 更新执行记录
                            case_execution = case_executions[case_data['id']]
                            case_execution.status = 'failed'
                            case_execution.finished_at = timezone.now()
                            case_execution.execution_time = 0
                            case_execution.error_message = f"导航到基础URL失败: {str(e)}"
                            case_execution.save()
                        
                        print(f"✓ 所有用例执行记录已更新")
                        return
                
                # 先执行所有脚本
                for i, script_data in enumerate(scripts_data, 1):
                    print(f"\n{'='*60}")
                    print(f"正在执行第 {i}/{total_items} 个项目：脚本 - {script_data['name']}")
                    print(f"{'='*60}")
                    
                    try:
                        # 执行脚本
                        script_result = self.execute_script_playwright(script_data, page)
                        self.results.append(script_result)
                        print(f"✓ 脚本执行完成，状态：{script_result['status']}")
                        
                        if script_result['status'] == 'passed':
                            passed += 1
                        elif script_result['status'] == 'failed':
                            failed += 1
                        else:
                            skipped += 1
                            
                    except Exception as e:
                        print(f"✗ 脚本执行出现异常：{str(e)}")
                        self.results.append({
                            'type': 'script',
                            'script_id': script_data['id'],
                            'script_name': script_data['name'],
                            'status': 'failed',
                            'steps': [],
                            'error': f"脚本执行异常：{str(e)}",
                            'start_time': datetime.now().isoformat(),
                            'end_time': datetime.now().isoformat(),
                            'screenshots': []
                        })
                        failed += 1
                
                # 然后执行所有测试用例，使用同一个页面
                for i, case_data in enumerate(test_cases_data, 1):
                    print(f"\n{'='*60}")
                    print(f"正在执行第 {len(scripts_data) + i}/{total_items} 个项目：用例 - {case_data['name']}")
                    print(f"{'='*60}")
                    
                    # 记录用例实际开始执行时间
                    case_execution = case_executions[case_data['id']]
                    case_execution.started_at = timezone.now()
                    case_execution.status = 'running'
                    case_execution.save()

                    try:
                        # 执行测试用例，使用同一个页面
                        case_result = self.execute_test_case_playwright_no_db(case_data, page)
                        self.results.append(case_result)
                        print(f"✓ 用例执行完成，状态: {case_result['status']}")

                        # 立即更新该用例的执行记录（包含准确的执行时间）
                        case_execution = case_executions[case_data['id']]
                        case_execution.status = case_result['status']
                        case_execution.finished_at = timezone.now()
                        case_execution.execution_time = (case_execution.finished_at - case_execution.started_at).total_seconds()
                        case_execution.execution_logs = json.dumps(case_result['steps'], ensure_ascii=False)
                        if case_result['error']:
                            case_execution.error_message = case_result['error']
                        if case_result.get('screenshots'):
                            case_execution.screenshots = case_result['screenshots']
                        case_execution.save()
                        
                        print(f"⏱️  执行时长: {case_execution.execution_time:.2f}秒")

                        if case_result['status'] == 'passed':
                            passed += 1
                        elif case_result['status'] == 'failed':
                            failed += 1
                        else:
                            skipped += 1

                    except Exception as e:
                        print(f"✗ 用例执行出现异常: {str(e)}")
                        # 记录异常
                        self.results.append({
                            'test_case_id': case_data['id'],
                            'test_case_name': case_data['name'],
                            'status': 'failed',
                            'steps': [],
                            'error': f"用例执行异常: {str(e)}",
                            'start_time': datetime.now().isoformat(),
                            'end_time': datetime.now().isoformat(),
                            'screenshots': []
                        })
                        failed += 1
                        
                        # 更新执行记录
                        case_execution = case_executions[case_data['id']]
                        case_execution.status = 'failed'
                        case_execution.finished_at = timezone.now()
                        case_execution.execution_time = (case_execution.finished_at - case_execution.started_at).total_seconds()
                        case_execution.error_message = f"用例执行异常: {str(e)}"
                        case_execution.save()
            
            finally:
                # 确保所有用例执行完成后关闭上下文和浏览器
                try:
                    if context:
                        context.close()
                    if browser:
                        browser.close()
                        print(f"✓ 浏览器已关闭\n")
                except:
                    pass

        # 注意：每个用例的执行记录已在执行过程中实时更新，不需要在这里统一更新

        duration = time.time() - start_time
        status = 'SUCCESS' if failed == 0 else 'FAILED'
        self.update_execution_result(status, passed, failed, skipped, duration)

    def execute_script_selenium(self, driver, script_data):
        """使用 Selenium 执行单个脚本

        Args:
            driver: Selenium WebDriver 对象
            script_data: 预先准备的脚本数据字典
        """
        result = {
            'type': 'script',
            'script_id': script_data['id'],
            'script_name': script_data['name'],
            'status': 'passed',
            'steps': [],
            'error': None,
            'start_time': datetime.now().isoformat(),
            'screenshots': []
        }
        
        try:
            # 根据脚本类型执行
            if script_data['script_type'] == 'CODE':
                # 代码脚本：直接执行 Python 代码
                result = self.execute_code_script_selenium(script_data, driver, result)
            elif script_data['script_type'] in ['LOW_CODE', '低代码']:
                # 低代码脚本：执行步骤
                result = self.execute_lowcode_script_selenium(script_data, driver, result)
            else:
                # 其他类型脚本暂不支持
                result['status'] = 'skipped'
                result['error'] = f"不支持的脚本类型：{script_data['script_type']}"
            
            result['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = f"脚本执行失败：{str(e)}"
            result['end_time'] = datetime.now().isoformat()
            
            # 失败截图
            if driver:
                try:
                    screenshot_bytes = driver.get_screenshot_as_png()
                    screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
                    result['screenshots'].append({
                        'url': f'data:image/png;base64,{screenshot_base64}',
                        'description': f'脚本失败截图：{script_data["name"]}',
                        'timestamp': datetime.now().isoformat()
                    })
                except:
                    pass
        
        return result
    
    def execute_code_script_selenium(self, script_data, driver, result):
        """执行代码脚本（Selenium）
        
        Args:
            script_data: 脚本数据
            driver: Selenium WebDriver 对象
            result: 结果字典
        """
        try:
            # 创建执行上下文
            exec_context = {
                'driver': driver,
                'page': driver,  # 兼容 playwright 的 page 命名
                'result': result
            }
            
            # 执行 Python 代码
            code_content = script_data['content']
            
            # 添加安全检查和日志
            print(f"📝 开始执行代码脚本：{script_data['name']}")
            
            # 执行代码
            exec(code_content, exec_context)
            
            print(f"✓ 代码脚本执行成功")
            result['status'] = 'passed'
            
        except Exception as e:
            print(f"✗ 代码脚本执行失败：{str(e)}")
            result['status'] = 'failed'
            result['error'] = f"代码执行错误：{str(e)}"
            
            import traceback
            traceback.print_exc()
        
        return result
    
    def execute_lowcode_script_selenium(self, script_data, driver, result):
        """执行低代码脚本（Selenium）
        
        Args:
            script_data: 脚本数据
            driver: Selenium WebDriver 对象
            result: 结果字典
        """
        try:
            steps = script_data.get('steps', [])
            
            if not steps:
                result['status'] = 'skipped'
                result['error'] = '脚本没有步骤'
                return result
            
            print(f"📝 开始执行低代码脚本：{script_data['name']}，共{len(steps)}个步骤")
            
            # 执行每个步骤
            for step_data in steps:
                step_result = self.execute_step_selenium(step_data, driver)
                result['steps'].append(step_result)
                
                if not step_result['success']:
                    result['status'] = 'failed'
                    result['error'] = f"步骤 {step_data['step_order']} 执行失败：{step_result.get('error', '')}"
                    break
            
            if result['status'] == 'passed':
                print(f"✓ 低代码脚本执行成功")
            else:
                print(f"✗ 低代码脚本执行失败：{result['error']}")
            
        except Exception as e:
            print(f"✗ 低代码脚本执行失败：{str(e)}")
            result['status'] = 'failed'
            result['error'] = f"脚本执行错误：{str(e)}"
        
        return result

    def execute_script_playwright(self, script_data, page):
        """使用 Playwright 执行单个脚本

        Args:
            script_data: 预先准备的脚本数据字典
            page: Playwright Page 对象
        """
        result = {
            'type': 'script',
            'script_id': script_data['id'],
            'script_name': script_data['name'],
            'status': 'passed',
            'steps': [],
            'error': None,
            'start_time': datetime.now().isoformat(),
            'screenshots': []
        }
        
        try:
            # 根据脚本类型执行
            if script_data['script_type'] == 'CODE':
                # 代码脚本：直接执行 Python 代码
                result = self.execute_code_script(script_data, page, result)
            elif script_data['script_type'] in ['LOW_CODE', '低代码']:
                # 低代码脚本：执行步骤
                result = self.execute_lowcode_script(script_data, page, result)
            else:
                # 其他类型脚本暂不支持
                result['status'] = 'skipped'
                result['error'] = f"不支持的脚本类型：{script_data['script_type']}"
            
            result['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = f"脚本执行失败：{str(e)}"
            result['end_time'] = datetime.now().isoformat()
            
            # 失败截图
            try:
                screenshot_bytes = page.screenshot()
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
                result['screenshots'].append({
                    'url': f'data:image/png;base64,{screenshot_base64}',
                    'description': f'脚本失败截图：{script_data["name"]}',
                    'timestamp': datetime.now().isoformat()
                })
            except:
                pass
        
        return result
    
    def execute_code_script(self, script_data, page, result):
        """执行代码脚本
        
        Args:
            script_data: 脚本数据
            page: Playwright Page 对象
            result: 结果字典
        """
        try:
            # 创建执行上下文
            exec_context = {
                'page': page,
                'result': result
            }
            
            # 执行 Python 代码
            code_content = script_data['content']
            
            # 添加安全检查和日志
            print(f"📝 开始执行代码脚本：{script_data['name']}")
            
            # 执行代码
            exec(code_content, exec_context)
            
            print(f"✓ 代码脚本执行成功")
            result['status'] = 'passed'
            
        except Exception as e:
            print(f"✗ 代码脚本执行失败：{str(e)}")
            result['status'] = 'failed'
            result['error'] = f"代码执行错误：{str(e)}"
            
            import traceback
            traceback.print_exc()
        
        return result
    
    def execute_lowcode_script(self, script_data, page, result):
        """执行低代码脚本
        
        Args:
            script_data: 脚本数据
            page: Playwright Page 对象
            result: 结果字典
        """
        try:
            steps = script_data.get('steps', [])
            
            if not steps:
                result['status'] = 'skipped'
                result['error'] = '脚本没有步骤'
                return result
            
            print(f"📝 开始执行低代码脚本：{script_data['name']}，共{len(steps)}个步骤")
            
            # 执行每个步骤
            for step_data in steps:
                step_result = self.execute_step_playwright(step_data, page)
                result['steps'].append(step_result)
                
                if not step_result['success']:
                    result['status'] = 'failed'
                    result['error'] = f"步骤 {step_data['step_order']} 执行失败：{step_result.get('error', '')}"
                    break
            
            if result['status'] == 'passed':
                print(f"✓ 低代码脚本执行成功")
            else:
                print(f"✗ 低代码脚本执行失败：{result['error']}")
            
        except Exception as e:
            print(f"✗ 低代码脚本执行失败：{str(e)}")
            result['status'] = 'failed'
            result['error'] = f"脚本执行错误：{str(e)}"
        
        return result

    def execute_test_case_playwright_no_db(self, case_data, page):
        """使用 Playwright 执行单个测试用例（不访问数据库）

        Args:
            case_data: 预先准备的用例数据字典，包含id, name, project_id, steps等
            page: Playwright Page对象
        """
        result = {
            'test_case_id': case_data['id'],
            'test_case_name': case_data['name'],
            'status': 'passed',
            'steps': [],
            'error': None,
            'start_time': datetime.now().isoformat(),
            'screenshots': []
        }

        try:
            # 遍历预先准备好的步骤数据
            just_switched_tab = False  # 跟踪是否刚切换了标签页
            for step_data in case_data['steps']:
                # 如果刚切换了标签页，传递这个信息
                step_data['_just_switched_tab'] = just_switched_tab
                just_switched_tab = False  # 重置标志
                
                step_result = self.execute_step_playwright(step_data, page)
                
                # Debug: Log which page we're using
                print(f"📄 步骤 {step_data['step_number']} 执行完成")
                print(f"   使用的page URL: {page.url}")
                print(f"   使用的page 标题: {page.title()}")
                
                result['steps'].append(step_result)
                
                # 显式更新page，确保引用正确
                if step_result.get('switched_page'):
                    page = step_result['switched_page']
                    print(f"🔄 页面切换确认: {page.title()}")
                    print(f"   当前页面URL: {page.url}")
                    print(f"   Page ID: {id(page)}")
                    del step_result['switched_page']
                    just_switched_tab = True
                
                # 步骤执行完后添加短暂延迟，确保页面状态稳定
                # 特别是点击操作后，可能触发动画、下拉框展开等
                if step_result['success'] and step_data['action_type'] in ['click', 'fill', 'hover']:
                    import asyncio
                    import time as sync_time
                    # 点击操作后等待更长时间（下拉框展开动画）
                    if step_data['action_type'] == 'click':
                        page.wait_for_timeout(800)  # 等待800ms，确保下拉框完全展开
                    else:
                        page.wait_for_timeout(300)  # 其他操作等待300ms

                # 如果步骤失败，捕获失败截图
                if not step_result['success']:
                    result['status'] = 'failed'
                    # 使用step的error信息作为case的error
                    result['error'] = step_result.get('error', f"步骤 {step_data['step_number']} 执行失败")

                    # 捕获失败截图（改进版）
                    try:
                        import base64
                        # 增加超时设置，避免截图等待时间过长
                        print(f"🔍 开始捕获失败截图 (步骤 {step_data['step_number']})...")
                        print(f"   当前page对象URL: {page.url}")
                        print(f"   当前page对象标题: {page.title()}")
                        screenshot_bytes = page.screenshot(timeout=5000)  # 5秒超时
                        print(f"   截图字节大小: {len(screenshot_bytes)} bytes")

                        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                        print(f"   Base64 编码大小: {len(screenshot_base64)} characters")

                        # 验证 base64 编码是否有效
                        if len(screenshot_base64) < 100:
                            raise Exception(f"Base64 编码异常短 ({len(screenshot_base64)} chars)，可能截图失败")

                        screenshot_url = f'data:image/png;base64,{screenshot_base64}'
                        result['screenshots'].append({
                            'url': screenshot_url,
                            'description': f'步骤 {step_data["step_number"]} 失败截图: {step_data.get("description", "")}',
                            'step_number': step_data['step_number'],
                            'timestamp': datetime.now().isoformat()
                        })
                        print(f"✓ 失败截图已捕获 (步骤 {step_data['step_number']})")
                        print(f"   截图 URL 长度: {len(screenshot_url)} characters")
                    except Exception as screenshot_error:
                        error_msg = f"捕获失败截图失败: {str(screenshot_error)}"
                        print(f"⚠️  {error_msg}")
                        import traceback
                        print(f"   详细错误:\n{traceback.format_exc()}")
                        # 记录截图失败的详细信息到结果中
                        result['screenshots'].append({
                            'url': None,
                            'description': f'步骤 {step_data["step_number"]} 截图失败: {str(screenshot_error)}',
                            'step_number': step_data['step_number'],
                            'timestamp': datetime.now().isoformat(),
                            'error': str(screenshot_error)
                        })


                    break

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)

            # 捕获异常截图（改进版）
            try:
                import base64
                # 增加超时设置，避免截图等待时间过长
                print(f"🔍 开始捕获异常截图...")
                screenshot_bytes = page.screenshot(timeout=5000)  # 5秒超时
                print(f"   截图字节大小: {len(screenshot_bytes)} bytes")

                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                print(f"   Base64 编码大小: {len(screenshot_base64)} characters")

                # 验证 base64 编码是否有效
                if len(screenshot_base64) < 100:
                    raise Exception(f"Base64 编码异常短 ({len(screenshot_base64)} chars)，可能截图失败")

                screenshot_url = f'data:image/png;base64,{screenshot_base64}'
                result['screenshots'].append({
                    'url': screenshot_url,
                    'description': f'异常截图: {str(e)}',
                    'step_number': None,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✓ 异常截图已捕获")
                print(f"   截图 URL 长度: {len(screenshot_url)} characters")
            except Exception as screenshot_error:
                error_msg = f"捕获异常截图失败: {str(screenshot_error)}"
                print(f"⚠️  {error_msg}")
                import traceback
                print(f"   详细错误:\n{traceback.format_exc()}")
                # 记录截图失败的详细信息到结果中
                result['screenshots'].append({
                    'url': None,
                    'description': f'异常截图失败: {str(screenshot_error)}',
                    'step_number': None,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(screenshot_error)
                })

        result['end_time'] = datetime.now().isoformat()
        return result

    def execute_test_case_playwright(self, page, case_data):
        self.current_page = page
        """使用 Playwright 执行单个测试用例（同步版本） - 已弃用，保留用于向后兼容

        Args:
            page: Playwright page对象
            case_data: 预先准备的用例数据字典，包含id, name, project_id, steps等
        """
        result = {
            'test_case_id': case_data['id'],
            'test_case_name': case_data['name'],
            'status': 'passed',
            'steps': [],
            'error': None,
            'start_time': datetime.now().isoformat(),
            'screenshots': []
        }

        # 创建用例执行记录
        case_execution = TestCaseExecution.objects.create(
            test_case_id=case_data['id'],
            project_id=case_data['project_id'],
            status='running',
            browser=self.browser,
            created_by=self.executed_by,
            started_at=timezone.now()
        )

        try:
            # 遍历预先准备好的步骤数据
            for step_data in case_data['steps']:
                step_result = self.execute_step_playwright(step_data)
                result['steps'].append(step_result)

                if not step_result['success']:
                    result['status'] = 'failed'
                    # 使用step的error信息作为case的error
                    result['error'] = step_result.get('error', f"步骤 {step_data['step_number']} 执行失败")
                    break

            # 更新用例执行记录
            case_execution.status = result['status']
            case_execution.finished_at = timezone.now()
            case_execution.execution_time = (case_execution.finished_at - case_execution.started_at).total_seconds()
            case_execution.execution_logs = json.dumps(result['steps'], ensure_ascii=False)
            if result['error']:
                case_execution.error_message = result['error']
            case_execution.save()

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)

            case_execution.status = 'error'
            case_execution.error_message = str(e)
            case_execution.finished_at = timezone.now()
            case_execution.save()

        result['end_time'] = datetime.now().isoformat()
        return result

    def execute_step_playwright(self, step_data, page):
        """使用 Playwright 执行单个步骤（同步版本）

        Args:
            step_data: 预先准备的步骤数据字典
            page: Playwright Page对象
        """
        import time
        start_time = time.time()

        step_result = {
            'step_number': step_data['step_number'],
            'action_type': step_data['action_type'],
            'description': step_data['description'],
            'success': False,
            'error': None
        }

        try:
            # 获取元素定位器
            if step_data['element']:
                element = step_data['element']
                locator_value = element['locator_value']
                locator_strategy = element['locator_strategy'].lower()
                element_name = element.get('name', '未知元素')

                # 根据定位策略构造 Playwright 选择器
                if locator_strategy in ['css', 'css selector']:
                    selector = locator_value
                elif locator_strategy == 'xpath':
                    selector = f'xpath={locator_value}'
                elif locator_strategy == 'id':
                    selector = f'#{locator_value}'
                elif locator_strategy == 'name':
                    selector = f'[name="{locator_value}"]'
                elif locator_strategy == 'text':
                    selector = f'text={locator_value}'
                elif locator_strategy == 'placeholder':
                    selector = f'[placeholder="{locator_value}"]'
                elif locator_strategy in ['class', 'class name']:
                    selector = f'.{locator_value}'
                elif locator_strategy in ['tag', 'tag name']:
                    selector = locator_value
                elif locator_strategy == 'link text':
                    selector = f'text={locator_value}'
                elif locator_strategy == 'partial link text':
                    selector = f'text={locator_value}'
                else:
                    selector = locator_value
                
                # 调试信息：打印当前页面状态
                print(f"🔍 [调试] 当前页面: {page.url}")
                print(f"🔍 [调试] 页面标题: {page.title()}")
                print(f"🔍 [调试] 定位策略: {locator_strategy}")
                print(f"🔍 [调试] 定位值: {locator_value}")
                print(f"🔍 [调试] 构造的选择器: {selector}")

                # 根据操作类型执行动作
                if step_data['action_type'] == 'click':
                    # 检测是否是下拉框选项（需要特殊处理）
                    # 简化逻辑：只要是 XPath 的 //li 元素，或包含特定关键词，就认为是下拉框选项
                    is_dropdown_option = (
                        # 条件1: XPath 定位的 li 元素（最常见的下拉框选项）
                        (locator_strategy.lower() == 'xpath' and '//li' in locator_value) or
                        # 条件2: CSS 或 XPath 包含 el-select-dropdown
                        'el-select-dropdown' in locator_value.lower() or
                        # 条件3: 包含 role="option"
                        'role="option"' in locator_value.lower() or
                        # 条件4: 包含 li 标签且看起来像列表项
                        ('li' in locator_value.lower() and ('ul' in locator_value.lower() or 'ol' in locator_value.lower()))
                    )
                    
                    # 检测是否是 el-select 容器（下拉框触发器）
                    is_select_trigger = (
                        'el-select' in locator_value.lower() and 
                        'ancestor::' in locator_value and 
                        '//li' not in locator_value
                    )
                    
                    if is_select_trigger:
                        # el-select 容器：需要点击内部的真正触发器
                        import time as sync_time
                        
                        # 使用 JavaScript 查找并点击内部的可点击元素
                        if locator_strategy.lower() == 'xpath':
                            js_code = f"""
                                (() => {{
                                    const xpath = {repr(locator_value)};
                                    const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                                    const selectEl = result.singleNodeValue;
                                    
                                    if (!selectEl) return {{ success: false, error: '未找到 el-select 容器' }};
                                    
                                    // 查找内部的触发器（按优先级）
                                    let trigger = selectEl.querySelector('.el-select__wrapper') ||
                                                 selectEl.querySelector('input') ||
                                                 selectEl.querySelector('.el-input__inner');
                                    
                                    if (trigger) {{
                                        trigger.click();
                                        return {{ success: true, method: 'inner-trigger', element: trigger.className }};
                                    }} else {{
                                        // 如果找不到内部触发器，直接点击容器
                                        selectEl.click();
                                        return {{ success: true, method: 'container', element: selectEl.className }};
                                    }}
                                }})()
                            """
                        else:
                            js_code = f"""
                                (() => {{
                                    const selectEl = document.querySelector({repr(locator_value)});
                                    
                                    if (!selectEl) return {{ success: false, error: '未找到 el-select 容器' }};
                                    
                                    let trigger = selectEl.querySelector('.el-select__wrapper') ||
                                                 selectEl.querySelector('input') ||
                                                 selectEl.querySelector('.el-input__inner');
                                    
                                    if (trigger) {{
                                        trigger.click();
                                        return {{ success: true, method: 'inner-trigger', element: trigger.className }};
                                    }} else {{
                                        selectEl.click();
                                        return {{ success: true, method: 'container', element: selectEl.className }};
                                    }}
                                }})()
                            """
                        
                        js_result = page.evaluate(js_code)
                        
                        if js_result.get('success'):
                            page.wait_for_timeout(800)  # 等待下拉框展开
                            step_result['success'] = True
                        else:
                            step_result['error'] = f"✗ 下拉框触发器点击失败: {js_result.get('error')}"
                    
                    elif is_dropdown_option:
                        # 下拉框选项：使用 Playwright 原生方法（更可靠）
                        # 之前使用 JS click() 可能无法触发 Element Plus 的事件监听
                        page.wait_for_timeout(800)  # 等待下拉框展开
                        
                        print(f"[Playwright-调试] 下拉框选项处理: {locator_strategy}={locator_value}")
                        
                        # 构造基础定位器（移除 Playwright 特有的伪类，因为我们要手动遍历）
                        base_locator_value = locator_value.replace(' >> visible=true', '')
                        
                        try:
                            if locator_strategy.lower() == 'xpath':
                                if not base_locator_value.startswith('xpath='):
                                    candidates = page.locator(f"xpath={base_locator_value}")
                                else:
                                    candidates = page.locator(base_locator_value)
                            elif locator_strategy.lower() in ['css', 'css selector']:
                                candidates = page.locator(base_locator_value)
                            else:
                                # 其他策略暂按 CSS 处理
                                candidates = page.locator(base_locator_value)
                            
                            # 获取匹配元素数量
                            count = candidates.count()
                            print(f"[Playwright-调试] 找到 {count} 个匹配元素")
                            
                            found_visible = False
                            last_error = None
                            
                            for i in range(count):
                                try:
                                    candidate = candidates.nth(i)
                                    if candidate.is_visible():
                                        print(f"[Playwright-调试] 第 {i} 个元素可见，尝试点击...")
                                        # 使用 Playwright 的 click，它会触发完整的鼠标事件链
                                        candidate.click(timeout=2000)
                                        found_visible = True
                                        step_result['success'] = True
                                        print(f"[Playwright-调试] 点击成功")
                                        break
                                except Exception as e:
                                    print(f"[Playwright-调试] 点击第 {i} 个元素失败: {e}")
                                    last_error = e
                            
                            if not found_visible:
                                error_msg = f"未找到可见的下拉框选项 (匹配到 {count} 个元素)"
                                if last_error:
                                    error_msg += f", 最后一次错误: {str(last_error)}"
                                step_result['error'] = error_msg
                                step_result['success'] = False
                                
                        except Exception as e:
                            step_result['error'] = f"下拉框选项处理异常: {str(e)}"
                            step_result['success'] = False
                        
                        # 检查并关闭多选下拉框（如果还在显示）
                        if step_result['success']:
                            try:
                                if page.locator('.el-select-dropdown').first.is_visible():
                                    # 点击空白处关闭
                                    page.click('body', position={'x': 10, 'y': 10}, timeout=3000)
                                    page.wait_for_timeout(500)
                            except:
                                pass
                        
                        # 已移除调试面板代码
                    else:
                        # 普通元素：正常点击
                        # 如果刚切换了标签页，增加超时时间并滚动到元素
                        if step_data.get('_just_switched_tab'):
                            print(f"  ⚠️  刚切换标签页，增加元素等待时间和滚动")
                            
                            # 关键修复：确保页面保持在前台！
                            page.bring_to_front()
                            print(f"  ✓ 页面已置于前台")
                            
                            # 先尝试滚动到元素（确保元素在视口内）
                            try:
                                page.locator(selector).scroll_into_view_if_needed(timeout=5000)
                                print(f"  ✓ 元素已滚动到视口")
                            except Exception as e:
                                print(f"  ⚠️  滚动失败: {str(e)[:50]}")
                            
                            # 使用更长的超时时间（至少10秒）
                            extended_timeout = max(step_data['wait_time'], 10000)
                            page.click(selector, timeout=extended_timeout)
                            print(f"  ✓ 点击成功（超时: {extended_timeout}ms）")
                        else:
                            page.click(selector, timeout=step_data['wait_time'])
                        step_result['success'] = True

                elif step_data['action_type'] == 'fill':
                    # 解析输入值中的变量表达式
                    resolved_value = resolve_variables(step_data['input_value'])
                    
                    # 确保页面保持在前台
                    page.bring_to_front()
                    
                    # 用 JavaScript 检查元素是否存在（避免字符串转义问题，使用参数传递）
                    print(f"🔍 [调试-fill] 正在用 JavaScript 检查元素是否存在...")
                    
                    try:
                        js_result = page.evaluate("""
                            (strategy, value) => {
                                let el = null;
                                if (strategy === 'placeholder') {
                                    el = document.querySelector('[placeholder="' + value + '"]');
                                } else if (strategy === 'xpath') {
                                    const result = document.evaluate(value, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                                    el = result.singleNodeValue;
                                } else if (strategy === 'css' || strategy === 'css selector') {
                                    el = document.querySelector(value);
                                } else if (strategy === 'id') {
                                    el = document.getElementById(value);
                                } else if (strategy === 'name') {
                                    el = document.querySelector('[name="' + value + '"]');
                                } else if (strategy === 'class' || strategy === 'class name') {
                                    el = document.querySelector('.' + value);
                                } else if (strategy === 'tag' || strategy === 'tag name') {
                                    el = document.querySelector(value);
                                } else if (strategy === 'link text') {
                                    // 查找包含精确文本的链接
                                    const links = document.querySelectorAll('a');
                                    for (let i = 0; i < links.length; i++) {
                                        if (links[i].textContent.trim() === value) {
                                            el = links[i];
                                            break;
                                        }
                                    }
                                } else if (strategy === 'partial link text') {
                                    // 查找包含部分文本的链接
                                    const links = document.querySelectorAll('a');
                                    for (let i = 0; i < links.length; i++) {
                                        if (links[i].textContent.includes(value)) {
                                            el = links[i];
                                            break;
                                        }
                                    }
                                }
                                
                                if (el) {
                                    return { 
                                        exists: true, 
                                        tagName: el.tagName, 
                                        id: el.id, 
                                        visible: !el.hidden && el.offsetParent !== null,
                                        disabled: el.disabled
                                    };
                                }
                                return { exists: false };
                            }
                        """, locator_strategy, locator_value)
                        print(f"🔍 [调试-fill] JavaScript 检查结果: {js_result}")
                    except Exception as js_err:
                        print(f"⚠️  [调试-fill] JavaScript 检查出错: {str(js_err)}")
                    
                    # 使用更长的超时时间（至少10秒），确保元素有足够时间加载
                    # 特别是在套件执行中，第二个用例可能需要等待页面状态稳定
                    extended_timeout = max(step_data['wait_time'], 10000)
                    print(f"🔍 [调试-fill] 准备填充元素，超时: {extended_timeout}ms")
                    page.fill(selector, resolved_value, timeout=extended_timeout)
                    
                    step_result['success'] = True
                    # 记录解析后的值（用于调试）
                    if resolved_value != step_data['input_value']:
                        step_result['resolved_value'] = resolved_value
                        print(f"  ✓ 变量解析: {step_data['input_value']} -> {resolved_value}")


                elif step_data['action_type'] == 'getText':
                    text = page.text_content(selector, timeout=step_data['wait_time'])
                    step_result['result'] = text
                    step_result['success'] = True

                elif step_data['action_type'] == 'waitFor':
                    # 检测是否是下拉框选项（下拉框选项可能是隐藏的）
                    is_dropdown_option_wait = (
                        (locator_strategy.lower() == 'xpath' and '//li' in locator_value) or
                        'el-select-dropdown' in locator_value.lower() or
                        'role="option"' in locator_value.lower() or
                        ('li' in locator_value.lower() and ('ul' in locator_value.lower() or 'ol' in locator_value.lower()))
                    )
                    
                    if is_dropdown_option_wait:
                        # 对于下拉框选项，只等待元素在DOM中（attached），不要求可见
                        page.wait_for_selector(selector, state='attached', timeout=step_data['wait_time'])
                    else:
                        # 普通元素：等待可见
                        page.wait_for_selector(selector, timeout=step_data['wait_time'])
                    
                    step_result['success'] = True

                elif step_data['action_type'] == 'hover':
                    page.hover(selector, timeout=step_data['wait_time'])
                    step_result['success'] = True

                elif step_data['action_type'] == 'scroll':
                    page.locator(selector).scroll_into_view_if_needed()
                    step_result['success'] = True

                elif step_data['action_type'] == 'screenshot':
                    screenshot_path = f'screenshots/step_{step_data["step_number"]}.png'
                    page.screenshot(path=screenshot_path)
                    step_result['screenshot'] = screenshot_path
                    step_result['success'] = True

                elif step_data['action_type'] == 'assert':
                    # 解析断言值中的变量
                    resolved_assert_value = resolve_variables(step_data['assert_value'])
                    if resolved_assert_value != step_data['assert_value']:
                         print(f"  ✓ 断言变量解析: {step_data['assert_value']} -> {resolved_assert_value}")

                    # 执行断言
                    if step_data['assert_type'] == 'textContains':
                        text = page.text_content(selector, timeout=step_data['wait_time'])
                        if resolved_assert_value in text:
                            step_result['success'] = True
                        else:
                            # 格式化为详细的错误信息，与playwright_engine.py保持一致
                            log = f"✗ 断言失败: 文本不包含 '{resolved_assert_value}'\n"
                            log += f"  - 实际文本: '{text}'"
                            step_result['error'] = log
                    elif step_data['assert_type'] == 'textEquals':
                        text = page.text_content(selector, timeout=step_data['wait_time'])
                        if text == resolved_assert_value:
                            step_result['success'] = True
                        else:
                            # 格式化为详细的错误信息
                            log = f"✗ 断言失败: 文本不等于 '{resolved_assert_value}'\n"
                            log += f"  - 期望: '{resolved_assert_value}'\n"
                            log += f"  - 实际: '{text}'"
                            step_result['error'] = log
                    elif step_data['assert_type'] == 'isVisible':
                        is_visible = page.is_visible(selector)
                        step_result['success'] = is_visible
                        if not is_visible:
                            step_result['error'] = f"✗ 断言失败: 元素 '{element_name}' 不可见"
                    elif step_data['assert_type'] == 'exists':
                        count = page.locator(selector).count()
                        step_result['success'] = count > 0
                        if count == 0:
                            step_result['error'] = f"✗ 断言失败: 元素 '{element_name}' 不存在"

                elif step_data['action_type'] == 'wait':
                    page.wait_for_timeout(step_data['wait_time'])
                    step_result['success'] = True

                elif step_data['action_type'] == 'switchTab':
                    # 切换标签页 - 同步版本
                    import time as sync_time
                    
                    # 获取超时时间
                    # 强制使用至少5秒的超时时间，确保有足够时间等待新标签页打开
                    user_wait = step_data.get('wait_time', 0) or 0
                    if user_wait > 0:
                        timeout = max(user_wait / 1000, 5.0)
                    else:
                        timeout = 5.0
                    
                    print(f"🔄 开始执行切换标签页 (超时: {timeout}s)...")
                    start_wait = sync_time.time()
                    current_page = page
                    target_index = -1
                    
                    # 轮询等待新标签页
                    # 轮询等待新标签页
                    while True:
                        pages = page.context.pages
                        target_index = -1  # 默认切换到最新标签页
                        should_switch = False
                        
                        # 调试日志：打印当前页面状态
                        print(f"  [Debug] 当前页面列表 (数量: {len(pages)}):")
                        for idx, p in enumerate(pages):
                            is_current = " (Current)" if p == current_page else ""
                            try:
                                print(f"    {idx}: {p.url} - {p.title()}{is_current}")
                            except Exception as e:
                                print(f"    {idx}: [Error getting info] {str(e)}")
                        
                        if step_data['input_value'] and str(step_data['input_value']).isdigit():
                            # 指定索引的情况
                            idx = int(step_data['input_value'])
                            if 0 <= idx < len(pages):
                                target_index = idx
                                should_switch = True
                        else:
                            # 自动模式：寻找一个不是当前页面的新页面
                            # 优先找列表末尾的（通常是新的）
                            candidates = [p for p in pages if p != current_page]
                            if candidates:
                                should_switch = True
                            elif len(pages) > 1:
                                # 如果有多个页面但都是 current_page (理论上不可能)，或者 current_page 不在 pages 里
                                # 只要页面数量增加，就应该切换
                                should_switch = True

                        if should_switch:
                            break
                        
                        if sync_time.time() - start_wait > timeout:
                            # 超时了
                            break
                        
                        # 关键修改：使用 wait_for_timeout 代替 time.sleep
                        # time.sleep 会阻塞线程，导致 Playwright 无法接收新页面事件
                        page.wait_for_timeout(500)
                    
                    # 获取目标页面
                    pages = page.context.pages
                    if target_index == -1:
                        # 自动模式
                        candidates = [p for p in pages if p != current_page]
                        if candidates:
                            # 切换到最新的一个非当前页面
                            target_page = candidates[-1]
                            final_target_index = pages.index(target_page)
                        else:
                            # 如果没有找到新页面
                            if len(pages) > 1:
                                # 备选：如果有多个页面，切换到最后一个
                                target_page = pages[-1]
                                final_target_index = len(pages) - 1
                            else:
                                raise Exception(f"切换标签页失败: 在 {timeout} 秒内未检测到新标签页打开 (当前页面数: {len(pages)})")
                    else:
                        target_page = pages[target_index]
                        final_target_index = target_index

                    # 将目标页面设为当前活动页面
                    target_page.bring_to_front()
                    
                    # 等待页面稳定
                    # 新标签页可能需要时间加载和渲染
                    try:
                        # 等待网络空闲状态（页面加载完成）
                        target_page.wait_for_load_state('networkidle', timeout=10000)  # 增加到10秒
                        print(f"  - 页面加载状态: networkidle")
                    except Exception as e:
                        # 如果networkidle超时，至少等待domcontentloaded
                        try:
                            target_page.wait_for_load_state('domcontentloaded', timeout=5000)  # 增加到5秒
                            print(f"  - 页面加载状态: domcontentloaded")
                        except Exception as e2:
                            print(f"  - 页面加载状态: 超时，继续执行 ({str(e2)[:50]})")
                    
                    # 额外等待一小段时间，确保页面完全稳定
                    target_page.wait_for_timeout(1500)  # 使用 wait_for_timeout 代替 sleep
                    
                    # 验证页面确实已切换
                    print(f"  - 当前活动页面URL: {target_page.url}")
                    print(f"  - 页面是否可见: {target_page.is_visible('body') if target_page else 'Unknown'}")
                    
                    # 设置切换后的页面
                    step_result['switched_page'] = target_page
                    step_result['success'] = True
                    
                    print(f"✓ 切换标签页成功")
                    print(f"  - 目标索引: {final_target_index}")
                    print(f"  - 页面标题: {target_page.title()}")
                    print(f"  - 已返回新页面引用")

                else:
                    step_result['error'] = f'⚠ 未知的操作类型: {step_data["action_type"]}'

            else:
                # 没有元素的步骤（如等待、切换标签页）
                if step_data['action_type'] == 'wait':
                    page.wait_for_timeout(step_data['wait_time'])
                    step_result['success'] = True
                
                elif step_data['action_type'] == 'switchTab':
                    # 切换标签页 - 同步版本（无需元素）
                    import time as sync_time
                    
                    # 获取超时时间
                    # 强制使用至少5秒的超时时间，确保有足够时间等待新标签页打开
                    user_wait = step_data.get('wait_time', 0) or 0
                    if user_wait > 0:
                        timeout = max(user_wait / 1000, 5.0)
                    else:
                        timeout = 5.0
                    
                    print(f"🔄 开始执行切换标签页 (超时: {timeout}s)...")
                    start_wait = sync_time.time()
                    current_page = self.current_page
                    target_index = -1
                    
                    # 轮询等待新标签页
                    # 轮询等待新标签页
                    while True:
                        pages = page.context.pages
                        target_index = -1  # 默认切换到最新标签页
                        should_switch = False
                        
                        # 调试日志：打印当前页面状态
                        print(f"  [Debug] 当前页面列表 (数量: {len(pages)}):")
                        for idx, p in enumerate(pages):
                            is_current = " (Current)" if p == current_page else ""
                            try:
                                print(f"    {idx}: {p.url} - {p.title()}{is_current}")
                            except Exception as e:
                                print(f"    {idx}: [Error getting info] {str(e)}")
                        
                        if step_data['input_value'] and str(step_data['input_value']).isdigit():
                            # 指定索引的情况
                            idx = int(step_data['input_value'])
                            if 0 <= idx < len(pages):
                                target_index = idx
                                should_switch = True
                        else:
                            # 自动模式：寻找一个不是当前页面的新页面
                            # 优先找列表末尾的（通常是新的）
                            candidates = [p for p in pages if p != current_page]
                            if candidates:
                                should_switch = True
                            elif len(pages) > 1:
                                # 如果有多个页面但都是 current_page (理论上不可能)，或者 current_page 不在 pages 里
                                # 只要页面数量增加，就应该切换
                                should_switch = True

                        if should_switch:
                            break
                        
                        if sync_time.time() - start_wait > timeout:
                            # 超时了
                            break
                        
                        # 关键修改：使用 wait_for_timeout 代替 time.sleep
                        self.current_page.wait_for_timeout(500)
                    
                    # 获取目标页面
                    pages = page.context.pages
                    if target_index == -1:
                        # 自动模式
                        candidates = [p for p in pages if p != current_page]
                        if candidates:
                            # 切换到最新的一个非当前页面
                            target_page = candidates[-1]
                            final_target_index = pages.index(target_page)
                        else:
                            # 如果没有找到新页面
                            if len(pages) > 1:
                                # 备选：如果有多个页面，切换到最后一个
                                target_page = pages[-1]
                                final_target_index = len(pages) - 1
                            else:
                                raise Exception(f"切换标签页失败: 在 {timeout} 秒内未检测到新标签页打开 (当前页面数: {len(pages)})")
                    else:
                        target_page = pages[target_index]
                        final_target_index = target_index

                    # 将目标页面设为当前活动页面
                    target_page.bring_to_front()
                    
                    # 等待页面稳定
                    try:
                        # 等待网络空闲状态（页面加载完成）
                        target_page.wait_for_load_state('networkidle', timeout=10000)  # 增加到10秒
                        print(f"  - 页面加载状态: networkidle")
                    except Exception as e:
                        # 如果networkidle超时，至少等待domcontentloaded
                        try:
                            target_page.wait_for_load_state('domcontentloaded', timeout=5000)  # 增加到5秒
                            print(f"  - 页面加载状态: domcontentloaded")
                        except Exception as e2:
                            print(f"  - 页面加载状态: 超时，继续执行 ({str(e2)[:50]})")
                    
                    # 额外等待一小段时间，确保页面完全稳定
                    target_page.wait_for_timeout(1500)  # 使用 wait_for_timeout 代替 sleep
                    
                    # 验证页面确实已切换
                    print(f"  - 当前活动页面URL: {target_page.url}")
                    print(f"  - 页面是否可见: {target_page.is_visible('body') if target_page else 'Unknown'}")
                    
                    # 设置切换后的页面
                    step_result['switched_page'] = target_page
                    step_result['success'] = True
                    
                    print(f"✓ 切换标签页成功")
                    print(f"  - 目标索引: {final_target_index}")
                    print(f"  - 页面标题: {target_page.title()}")
                    print(f"  - 已返回新页面引用")

        except Exception as e:
            # 格式化为详细的错误信息，与playwright_engine.py保持一致
            execution_time = round(time.time() - start_time, 2)

            # 提取详细的错误信息（改进版）
            error_str = str(e)
            error_type = type(e).__name__

            # 尝试提取更详细的 Playwright 异常信息
            try:
                # Playwright 异常可能包含更详细的信息
                if hasattr(e, 'message') and e.message:
                    error_str = e.message
                # TimeoutError 通常有更详细的描述
                elif hasattr(e, 'args') and e.args:
                    error_str = str(e.args[0]) if len(e.args) > 0 else error_str
            except:
                pass  # 如果提取失败，使用原始 error_str

            # 添加异常类型信息（如果还没有）
            if error_type not in error_str and error_type != 'Exception':
                error_str = f"{error_type}: {error_str}"

            # 判断是否是超时错误
            if 'Timeout' in error_str or 'timeout' in error_str:
                element_name = step_data['element'].get('name', '未知元素') if step_data.get('element') else '页面'
                locator_info = f"{step_data['element']['locator_strategy']}={step_data['element']['locator_value']}" if step_data.get('element') else '无'

                log = f"✗ 操作超时\n"
                log += f"  - 元素: '{element_name}'\n"
                log += f"  - 定位器: {locator_info}\n"
                log += f"  - 超时时间: {execution_time}秒\n"
                log += f"  - 错误: {error_str}"
                step_result['error'] = log
            else:
                element_name = step_data['element'].get('name', '未知元素') if step_data.get('element') else '页面'
                locator_info = f"{step_data['element']['locator_strategy']}={step_data['element']['locator_value']}" if step_data.get('element') else '无'

                log = f"✗ 执行失败\n"
                log += f"  - 元素: '{element_name}'\n"
                log += f"  - 定位器: {locator_info}\n"
                log += f"  - 执行时间: {execution_time}秒\n"
                log += f"  - 错误: {error_str}"
                step_result['error'] = log

            # 打印详细日志便于调试
            print(f"❌ Playwright 步骤执行失败:")
            print(f"   异常类型: {error_type}")
            print(f"   错误信息: {error_str[:500]}")  # 限制长度避免刷屏

        return step_result

    def run_with_selenium(self):
        """使用 Selenium 执行测试"""
        start_time = time.time()
        passed = 0
        failed = 0
        skipped = 0

        # 检查 Selenium 是否可用（使用延迟导入）
        try:
            _import_selenium()
        except ImportError as e:
            error_msg = (
                f"Selenium 模块未正确安装。\n\n"
                f"请运行: pip install selenium webdriver-manager\n\n"
                f"详细错误: {str(e)}"
            )
            print(f"❌ {error_msg}")
            
            # 更新套件执行状态
            if self.execution:
                self.update_execution_result(
                    status='FAILED',
                    failed=len(self.test_cases),
                    error_msg=error_msg
                )
            
            # 更新所有用例状态为失败
            for test_case in self.test_cases:
                TestCaseExecution.objects.filter(
                    test_case=test_case,
                    test_suite=self.test_suite,
                    status='pending'
                ).update(
                    status='failed',
                    error_message=error_msg,
                    finished_at=timezone.now()
                )
            
            return

        # 预先获取所有脚本数据，避免在 Selenium 上下文中访问 ORM
        scripts_data = []
        for test_script in self.scripts:
            script_data = {
                'id': test_script.id,
                'name': test_script.name,
                'project_id': self.test_suite.project.id,
                'script_type': test_script.script_type,
                'language': test_script.language,
                'framework': test_script.framework,
                'content': test_script.content,
                'steps': []
            }
            
            # 如果是低代码脚本，获取步骤数据
            if test_script.script_type in ['LOW_CODE', '低代码']:
                steps = test_script.steps.select_related('target_element', 'target_element__locator_strategy').order_by('step_order')
                for step in steps:
                    step_data = {
                        'id': step.id,
                        'step_order': step.step_order,
                        'action_type': step.action_type,
                        'description': step.description,
                        'expected_result': step.expected_result,
                        'action_params': step.action_params,
                        'wait_before': step.wait_before,
                        'wait_after': step.wait_after,
                        'element': None
                    }
                    
                    # 如果有目标元素，预先获取元素数据
                    if step.target_element:
                        step_data['element'] = {
                            'id': step.target_element.id,
                            'name': step.target_element.name,
                            'locator_value': step.target_element.locator_value,
                            'locator_strategy': step.target_element.locator_strategy.name if step.target_element.locator_strategy else 'css'
                        }
                    
                    script_data['steps'].append(step_data)
            
            scripts_data.append(script_data)
        
        # 预先获取所有测试用例的步骤数据，避免在 Selenium 上下文中访问 ORM
        test_cases_data = []
        for test_case in self.test_cases:
            case_data = {
                'id': test_case.id,
                'name': test_case.name,
                'project_id': self.test_suite.project.id,
                'steps': []
            }

            # 获取步骤并预先加载所有相关数据
            steps = test_case.steps.select_related('element', 'element__locator_strategy').order_by('step_number')
            for step in steps:
                step_data = {
                    'id': step.id,
                    'step_number': step.step_number,
                    'action_type': step.action_type,
                    'description': step.description,
                    'input_value': step.input_value,
                    'wait_time': step.wait_time,
                    'assert_type': step.assert_type,
                    'assert_value': step.assert_value,
                    'element': None
                }

                # 如果有元素，预先获取元素数据
                if step.element:
                    step_data['element'] = {
                        'id': step.element.id,
                        'name': step.element.name,
                        'locator_value': step.element.locator_value,
                        'locator_strategy': step.element.locator_strategy.name if step.element.locator_strategy else 'css'
                    }

                case_data['steps'].append(step_data)

            test_cases_data.append(case_data)

        # 预先创建所有测试用例执行记录（不设置 started_at，等实际执行时再设置）
        case_executions = {}
        for case_data in test_cases_data:
            case_execution = TestCaseExecution.objects.create(
                test_case_id=case_data['id'],
                project_id=case_data['project_id'],
                test_suite=self.test_suite,
                execution_source='suite',
                status='pending',  # 初始状态为 pending
                engine=self.engine,
                browser=self.browser,
                headless=self.headless,
                created_by=self.executed_by
                # 注意：不设置 started_at，等用例实际开始执行时再设置
            )
            case_executions[case_data['id']] = case_execution

        # 优化：整个测试套件共用一个浏览器实例，避免频繁启动/关闭
        # 注意：Safari 不支持浏览器复用（会话管理问题），需要每个用例独立启动
        total_items = len(scripts_data) + len(test_cases_data)
        print(f"准备执行 {total_items} 个项目（{len(scripts_data)} 个脚本，{len(test_cases_data)} 个测试用例）")
        
        # 暂时禁用浏览器复用，解决测试套件闪退问题
        # Safari 需要独立浏览器实例，其他浏览器也暂时禁用复用
        use_browser_reuse = False
        
        if use_browser_reuse:
            # 在套件开始时启动一次浏览器（Chrome/Firefox/Edge）
            driver = None
            try:
                driver = self.create_selenium_driver()
                print(f"✓ 浏览器已启动（将复用于所有用例）\n")
            except Exception as e:
                print(f"✗ 浏览器启动失败: {str(e)}")
                # 标记所有用例为失败
                for case_data in test_cases_data:
                    self.results.append({
                        'test_case_id': case_data['id'],
                        'test_case_name': case_data['name'],
                        'status': 'failed',
                        'steps': [],
                        'error': f"浏览器启动失败: {str(e)}",
                        'start_time': datetime.now().isoformat(),
                        'end_time': datetime.now().isoformat(),
                        'screenshots': []
                    })
                    failed += 1
                # 更新执行记录并返回
                for case_result in self.results:
                    case_execution = case_executions[case_result['test_case_id']]
                    case_execution.status = 'failed'
                    case_execution.finished_at = timezone.now()
                    case_execution.execution_time = 0
                    case_execution.error_message = case_result['error']
                    case_execution.save()
                duration = time.time() - start_time
                self.update_execution_result('FAILED', 0, len(test_cases_data), 0, duration)
                return
        else:
            # Safari：不预先启动浏览器，每个用例独立启动
            driver = None
            print(f"ℹ️  Safari 浏览器将为每个用例独立启动（Safari 不支持浏览器复用）\n")

        # 执行所有脚本和测试用例
        # 先执行所有脚本
        for i, script_data in enumerate(scripts_data, 1):
            print(f"\n{'='*60}")
            print(f"正在执行第 {i}/{total_items} 个项目：脚本 - {script_data['name']}")
            print(f"{'='*60}")
            
            try:
                # 执行脚本
                script_result = self.execute_script_selenium(driver if 'driver' in locals() else None, script_data)
                self.results.append(script_result)
                print(f"✓ 脚本执行完成，状态：{script_result['status']}")
                
                if script_result['status'] == 'passed':
                    passed += 1
                elif script_result['status'] == 'failed':
                    failed += 1
                else:
                    skipped += 1
                    
            except Exception as e:
                print(f"✗ 脚本执行出现异常：{str(e)}")
                self.results.append({
                    'type': 'script',
                    'script_id': script_data['id'],
                    'script_name': script_data['name'],
                    'status': 'failed',
                    'steps': [],
                    'error': f"脚本执行异常：{str(e)}",
                    'start_time': datetime.now().isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'screenshots': []
                })
                failed += 1
        
        # 然后执行所有测试用例
        for i, case_data in enumerate(test_cases_data, 1):
            print(f"\n{'='*60}")
            print(f"正在执行第 {len(scripts_data) + i}/{total_items} 个项目：用例 - {case_data['name']}")
            print(f"{'='*60}")
            
            # 记录用例实际开始执行时间
            case_execution = case_executions[case_data['id']]
            case_execution.started_at = timezone.now()
            case_execution.status = 'running'
            case_execution.save()

            # Safari：为每个用例启动新的浏览器
            if not use_browser_reuse:
                try:
                    driver = self.create_selenium_driver()
                    print(f"✓ Safari 浏览器已启动")
                except Exception as e:
                    print(f"✗ Safari 浏览器启动失败: {str(e)}")
                    self.results.append({
                        'test_case_id': case_data['id'],
                        'test_case_name': case_data['name'],
                        'status': 'failed',
                        'steps': [],
                        'error': f"浏览器启动失败: {str(e)}",
                        'start_time': datetime.now().isoformat(),
                        'end_time': datetime.now().isoformat(),
                        'screenshots': []
                    })
                    failed += 1
                    # 更新执行记录
                    case_execution.status = 'failed'
                    case_execution.finished_at = timezone.now()
                    case_execution.execution_time = (case_execution.finished_at - case_execution.started_at).total_seconds()
                    case_execution.error_message = f"浏览器启动失败: {str(e)}"
                    case_execution.save()
                    continue

            try:
                # 导航到项目基础URL（只在第一个用例时执行，后续用例复用页面状态）
                # 注意：如果浏览器不复用（如Safari），每个用例都会重新启动浏览器，所以需要每次都导航
                if self.test_suite.project.base_url and (not use_browser_reuse or i == 1):
                    try:
                        print(f"正在导航到: {self.test_suite.project.base_url}")

                        # 检测是否在Linux服务器环境
                        import platform
                        is_linux = platform.system() == 'Linux'

                        # 导航到URL
                        driver.get(self.test_suite.project.base_url)

                        # 等待页面基本加载完成
                        # 在服务器环境（特别是无头模式）需要更长的等待时间
                        try:
                            WebDriverWait(driver, 15 if is_linux else 10).until(
                                lambda d: d.execute_script("return document.readyState") == "complete"
                            )
                        except:
                            pass  # 即使超时也继续执行

                        # 额外等待，确保动态内容加载（Vue/React等SPA应用）
                        extra_wait = 3 if is_linux else 2
                        time.sleep(extra_wait)

                        print(f"✓ 成功导航到: {self.test_suite.project.base_url} (已等待页面加载完成，额外{extra_wait}秒)")
                    except Exception as e:
                        print(f"✗ 导航失败: {str(e)}")
                        # 导航失败，记录错误并继续下一个用例
                        self.results.append({
                            'test_case_id': case_data['id'],
                            'test_case_name': case_data['name'],
                            'status': 'failed',
                            'steps': [],
                            'error': f"导航到基础URL失败: {str(e)}",
                            'start_time': datetime.now().isoformat(),
                            'end_time': datetime.now().isoformat(),
                            'screenshots': []
                        })
                        failed += 1
                        continue

                # 执行测试用例
                case_result = self.execute_test_case_selenium_no_db(driver, case_data)
                self.results.append(case_result)
                print(f"✓ 用例执行完成，状态: {case_result['status']}")

                # 立即更新该用例的执行记录（包含准确的执行时间）
                case_execution = case_executions[case_data['id']]
                case_execution.status = case_result['status']
                case_execution.finished_at = timezone.now()
                case_execution.execution_time = (case_execution.finished_at - case_execution.started_at).total_seconds()
                case_execution.execution_logs = json.dumps(case_result['steps'], ensure_ascii=False)
                if case_result['error']:
                    case_execution.error_message = case_result['error']
                if case_result.get('screenshots'):
                    case_execution.screenshots = case_result['screenshots']
                case_execution.save()
                
                print(f"⏱️  执行时长: {case_execution.execution_time:.2f}秒")

                if case_result['status'] == 'passed':
                    passed += 1
                elif case_result['status'] == 'failed':
                    failed += 1
                else:
                    skipped += 1

            except Exception as e:
                print(f"✗ 用例执行出现异常: {str(e)}")
                # 记录异常
                self.results.append({
                    'test_case_id': case_data['id'],
                    'test_case_name': case_data['name'],
                    'status': 'failed',
                    'steps': [],
                    'error': f"用例执行异常: {str(e)}",
                    'start_time': datetime.now().isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'screenshots': []
                })
                failed += 1
                
                # 更新执行记录
                case_execution = case_executions[case_data['id']]
                case_execution.status = 'failed'
                case_execution.finished_at = timezone.now()
                case_execution.execution_time = (case_execution.finished_at - case_execution.started_at).total_seconds()
                case_execution.error_message = f"用例执行异常: {str(e)}"
                case_execution.save()
            
            finally:
                # Safari：每个用例执行完都关闭浏览器
                if not use_browser_reuse and driver:
                    try:
                        driver.quit()
                        print(f"✓ Safari 浏览器已关闭\n")
                    except Exception as e:
                        print(f"✗ 关闭 Safari 浏览器时出错: {str(e)}\n")
                    driver = None

        # 所有用例执行完毕后，关闭浏览器（仅对复用浏览器的情况）
        if use_browser_reuse and driver:
            try:
                print(f"\n{'='*60}")
                print(f"正在关闭浏览器...")
                driver.quit()
                print(f"✓ 浏览器已关闭")
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"✗ 关闭浏览器时出错: {str(e)}")

        # 注意：每个用例的执行记录已在执行过程中实时更新，不需要在这里统一更新
        
        duration = time.time() - start_time
        status = 'SUCCESS' if failed == 0 else 'FAILED'
        self.update_execution_result(status, passed, failed, skipped, duration)

    def create_selenium_driver(self):
        """创建 Selenium WebDriver"""
        # 延迟导入 Selenium 模块
        try:
            selenium_modules = _import_selenium()
            webdriver = selenium_modules['webdriver']
            ChromeOptions = selenium_modules['ChromeOptions']
            FirefoxOptions = selenium_modules['FirefoxOptions']
            EdgeOptions = selenium_modules['EdgeOptions']
        except ImportError as e:
            raise ImportError(f"Selenium 未安装: {str(e)}")
        
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.firefox import GeckoDriverManager
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        from apps.ui_automation.selenium_engine import SeleniumTestEngine
        import os
        
        # 配置webdriver_manager使用本地缓存，避免每次下载
        # 缓存目录：~/.wdm
        os.environ['WDM_LOG_LEVEL'] = '0'  # 减少日志输出
        os.environ['WDM_PRINT_FIRST_LINE'] = 'False'  # 不打印首行信息
        
        # 检查浏览器是否可用
        is_available, error_msg = SeleniumTestEngine.check_browser_available(self.browser)
        if not is_available:
            # 提供安装建议
            install_tips = {
                'chrome': 'brew install --cask google-chrome',
                'firefox': 'brew install --cask firefox',
                'edge': 'brew install --cask microsoft-edge',
            }
            tip = install_tips.get(self.browser, '')
            full_error = f"{error_msg}\n\n💡 安装命令（macOS）：{tip}" if tip else error_msg
            raise Exception(full_error)
        
        if self.browser == 'chrome':
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            # 禁用自动化特征检测
            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 禁用密码保存和泄露提醒（解决弹框遮挡元素的问题）
            prefs = {
                'credentials_enable_service': False,  # 禁用密码保存服务
                'profile.password_manager_enabled': False,  # 禁用密码管理器
                'profile.default_content_setting_values.notifications': 2,  # 禁用通知
                'autofill.profile_enabled': False,  # 禁用自动填充
                'profile.default_content_setting_values.automatic_downloads': 1,  # 允许自动下载
                'password_manager_leak_detection': False,  # 禁用密码泄露检测（prefs级别）
                'safebrowsing.enabled': False,  # 禁用安全浏览
                'safebrowsing.disable_download_protection': True,
                'intl.accept_languages': 'zh-CN,zh,en-US,en',  # 设置语言
                'profile.exit_type': 'Normal',  # 避免"Chrome未正常关闭"提示
            }
            options.add_experimental_option('prefs', prefs)
            
            # 禁用密码泄露检查和其他安全警告（更全面的设置）
            # 将所有 disable-features 合并为一个参数，避免覆盖
            disabled_features = [
                'PasswordLeakDetection',
                'PrivacySandboxSettings4',
                'TranslateUI',
                'SavePasswordBubble',
                'AutofillServerCommunication',
                'CreditCardSave',
                'HeaderUI',
                'AccountConsistency',
            ]
            options.add_argument(f'--disable-features={",".join(disabled_features)}')
            
            options.add_argument('--disable-infobars')  # 禁用信息栏
            options.add_argument('--disable-save-password-bubble')  # 禁用保存密码气泡
            options.add_argument('--disable-password-generation')  # 禁用密码生成
            options.add_argument('--disable-password-manager-reauthentication')  # 禁用密码管理器重新认证
            options.add_argument('--disable-popup-blocking')  # 禁用弹窗拦截
            options.add_argument('--disable-notifications')  # 禁用所有通知
            options.add_argument('--no-default-browser-check') # 禁用默认浏览器检查
            options.add_argument('--no-first-run') # 禁用首次运行界面
            
            # 针对密码弹窗的额外参数
            options.add_argument('--password-store=basic')
            options.add_argument('--use-mock-keychain')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-device-discovery-notifications')
            
            # 使用缓存优先策略
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        elif self.browser == 'firefox':
            options = FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--width=1920')
            options.add_argument('--height=1080')
            
            # 性能优化：禁用不必要的功能加快启动速度
            options.set_preference('browser.cache.disk.enable', False)
            options.set_preference('browser.cache.memory.enable', True)
            options.set_preference('browser.cache.offline.enable', False)
            options.set_preference('network.http.use-cache', False)
            options.set_preference('browser.startup.homepage', 'about:blank')
            options.set_preference('startup.homepage_welcome_url', 'about:blank')
            options.set_preference('startup.homepage_welcome_url.additional', 'about:blank')
            # 禁用自动更新检查
            options.set_preference('app.update.auto', False)
            options.set_preference('app.update.enabled', False)
            # 禁用扩展和插件检查
            options.set_preference('extensions.update.enabled', False)
            options.set_preference('extensions.update.autoUpdateDefault', False)
            
            # 使用缓存优先策略
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
        elif self.browser == 'safari':
            # Safari 不支持 headless 模式
            # 需要先启用：sudo safaridriver --enable
            # 并在 Safari 设置 -> 开发菜单中启用"允许远程自动化"
            try:
                driver = webdriver.Safari()
                driver.set_window_size(1920, 1080)
            except Exception as e:
                error_msg = str(e)
                if 'Could not create a session' in error_msg or 'InvalidSessionIdException' in error_msg:
                    raise Exception(
                        "Safari 远程自动化未启用。\n\n"
                        "请按以下步骤配置：\n"
                        "1. 在终端执行: sudo safaridriver --enable\n"
                        "2. 打开 Safari → 设置 → 高级 → 勾选'在菜单栏中显示开发菜单'\n"
                        "3. Safari 菜单栏 → 开发 → 勾选'允许远程自动化'\n\n"
                        f"原始错误: {error_msg}"
                    )
                raise
        elif self.browser == 'edge':
            options = EdgeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            # 使用缓存优先策略
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
        else:
            # 默认使用Chrome
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            # 禁用自动化特征检测
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 禁用密码保存和泄露提醒（解决弹框遮挡元素的问题）
            prefs = {
                'credentials_enable_service': False,  # 禁用密码保存服务
                'profile.password_manager_enabled': False,  # 禁用密码管理器
                'profile.default_content_setting_values.notifications': 2,  # 禁用通知
                'autofill.profile_enabled': False,  # 禁用自动填充
                'profile.default_content_setting_values.automatic_downloads': 1,  # 允许自动下载
            }
            options.add_experimental_option('prefs', prefs)
            
            # 禁用密码泄露检查和其他安全警告
            options.add_argument('--disable-features=PasswordLeakDetection')  # 禁用密码泄露检测
            options.add_argument('--disable-features=PrivacySandboxSettings4')  # 禁用隐私沙盒
            options.add_argument('--disable-features=TranslateUI')  # 禁用翻译提示
            options.add_argument('--disable-infobars')  # 禁用信息栏
            
            # 使用缓存优先策略
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        return driver

    def execute_test_case_selenium_no_db(self, driver, case_data):
        """使用 Selenium 执行单个测试用例（不访问数据库）

        Args:
            driver: Selenium WebDriver对象
            case_data: 预先准备的用例数据字典，包含id, name, project_id, steps等
        """
        result = {
            'test_case_id': case_data['id'],
            'test_case_name': case_data['name'],
            'status': 'passed',
            'steps': [],
            'error': None,
            'start_time': datetime.now().isoformat(),
            'screenshots': []
        }

        try:
            # 遍历预先准备好的步骤数据
            for step_data in case_data['steps']:
                step_result = self.execute_step_selenium(driver, step_data)
                result['steps'].append(step_result)
                
                # 步骤执行完后添加短暂延迟，确保页面状态稳定
                # 特别是点击操作后，可能触发动画、下拉框展开等
                if step_result['success'] and step_data['action_type'] in ['click', 'fill', 'hover']:
                    # 点击操作后等待更长时间（下拉框展开动画）
                    if step_data['action_type'] == 'click':
                        time.sleep(0.8)  # 等待800ms，确保下拉框完全展开
                    else:
                        time.sleep(0.3)  # 其他操作等待300ms

                # 如果步骤失败,捕获失败截图
                if not step_result['success']:
                    result['status'] = 'failed'
                    # 使用step的error信息作为case的error
                    result['error'] = step_result.get('error', f"步骤 {step_data['step_number']} 执行失败")

                    # 捕获失败截图
                    try:
                        import base64
                        screenshot_bytes = driver.get_screenshot_as_png()
                        screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
                        result['screenshots'].append({
                            'url': f'data:image/png;base64,{screenshot_base64}',
                            'description': f'步骤 {step_data["step_number"]} 失败截图: {step_data.get("description", "")}',
                            'step_number': step_data['step_number'],
                            'timestamp': datetime.now().isoformat()
                        })
                    except Exception as screenshot_error:
                        print(f"捕获失败截图失败: {str(screenshot_error)}")

                    break

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)

            # 捕获异常截图
            try:
                import base64
                screenshot_bytes = driver.get_screenshot_as_png()
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
                result['screenshots'].append({
                    'url': f'data:image/png;base64,{screenshot_base64}',
                    'description': f'异常截图: {str(e)}',
                    'step_number': None,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as screenshot_error:
                print(f"捕获异常截图失败: {str(screenshot_error)}")

        result['end_time'] = datetime.now().isoformat()
        return result

    def execute_test_case_selenium(self, driver, case_data):
        """使用 Selenium 执行单个测试用例 - 已弃用，保留用于���后兼容

        Args:
            driver: Selenium WebDriver对象
            case_data: 预先准备的用例数据字典，包含id, name, project_id, steps等
        """
        result = {
            'test_case_id': case_data['id'],
            'test_case_name': case_data['name'],
            'status': 'passed',
            'steps': [],
            'error': None,
            'start_time': datetime.now().isoformat()
        }

        case_execution = TestCaseExecution.objects.create(
            test_case_id=case_data['id'],
            project_id=case_data['project_id'],
            status='running',
            browser=self.browser,
            created_by=self.executed_by,
            started_at=timezone.now()
        )

        try:
            # 遍历预先准备好的步骤数据
            for step_data in case_data['steps']:
                step_result = self.execute_step_selenium(driver, step_data)
                result['steps'].append(step_result)

                if not step_result['success']:
                    result['status'] = 'failed'
                    # 使用step的error信息作为case的error
                    result['error'] = step_result.get('error', f"步骤 {step_data['step_number']} 执行失败")
                    break

            # 更新用例执行记录
            case_execution.status = result['status']
            case_execution.finished_at = timezone.now()
            case_execution.execution_time = (case_execution.finished_at - case_execution.started_at).total_seconds()
            case_execution.execution_logs = json.dumps(result['steps'], ensure_ascii=False)
            if result['error']:
                case_execution.error_message = result['error']
            case_execution.save()

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)

            case_execution.status = 'error'
            case_execution.error_message = str(e)
            case_execution.finished_at = timezone.now()
            case_execution.save()

        result['end_time'] = datetime.now().isoformat()
        return result

    def execute_step_selenium(self, driver, step_data):
        """使用 Selenium 执行单个步骤

        Args:
            driver: Selenium WebDriver对象
            step_data: 预先准备的步骤数据字典
        """
        from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
        start_time = time.time()

        step_result = {
            'step_number': step_data['step_number'],
            'action_type': step_data['action_type'],
            'description': step_data['description'],
            'success': False,
            'error': None
        }

        try:
            if step_data['element']:
                element = step_data['element']
                locator_value = element['locator_value']
                locator_strategy = element['locator_strategy'].lower()
                element_name = element.get('name', '未知元素')

                # 根据定位策略获取元素
                wait = WebDriverWait(driver, step_data['wait_time'] / 1000)

                # 自动修正定位策略：如果值以 // 开头，强制使用 XPath
                if locator_value.startswith('//') or locator_value.startswith('xpath='):
                    locator_strategy = 'xpath'
                    if locator_value.startswith('xpath='):
                        locator_value = locator_value[6:]

                # 根据定位策略构造 Playwright 选择器
                if locator_strategy in ['css', 'css selector']:
                    by = By.CSS_SELECTOR
                elif locator_strategy == 'xpath':
                    by = By.XPATH
                elif locator_strategy == 'id':
                    by = By.ID
                elif locator_strategy == 'name':
                    by = By.NAME
                elif locator_strategy in ['class', 'class name']:
                    by = By.CLASS_NAME
                elif locator_strategy in ['tag', 'tag name']:
                    by = By.TAG_NAME
                elif locator_strategy == 'link text':
                    by = By.LINK_TEXT
                elif locator_strategy == 'partial link text':
                    by = By.PARTIAL_LINK_TEXT
                else:
                    by = By.CSS_SELECTOR

                # 根据操作类型选择合适的等待条件
                if step_data['action_type'] == 'click':
                    # 点击操作：等待元素可点击（解决 stale element 问题）
                    # 通过定位器特征自动识别下拉框选项
                    is_dropdown_option = (
                        'dropdown' in locator_value.lower() or 
                        'el-select' in locator_value.lower() or 
                        'role="option"' in element_name.lower() or 
                        '下拉' in element_name or 
                        '选项' in element_name or
                        'el-select-dropdown__item' in locator_value.lower() or
                        ('//li' in locator_value and 'span=' in locator_value)  # XPath 下拉框模式
                    )
                    
                    if is_dropdown_option:
                        # 下拉框选项：特殊处理，遍历所有匹配元素找到可见的那个
                        print(f"  检测到下拉框选项（定位器匹配），尝试查找可见元素...")
                        
                        # 自定义等待逻辑：轮询查找可见元素
                        end_time = time.time() + (step_data['wait_time'] / 1000)
                        found_visible = False
                        
                        while time.time() < end_time:
                            try:
                                # 查找所有匹配元素
                                elements = driver.find_elements(by, locator_value)
                                for el in elements:
                                    if el.is_displayed():
                                        element_obj = el
                                        found_visible = True
                                        print(f"  ✓ 找到可见的下拉框选项")
                                        break
                                
                                if found_visible:
                                    break
                                    
                                time.sleep(0.5)
                            except:
                                time.sleep(0.5)
                        
                        if not found_visible:
                            # 如果没找到可见元素，回退到默认行为（可能会抛出超时）
                            print(f"  ⚠️ 未找到可见的下拉框选项，尝试默认等待...")
                            element_obj = wait.until(EC.visibility_of_element_located((by, locator_value)))
                    else:
                        element_obj = wait.until(EC.element_to_be_clickable((by, locator_value)))
                else:
                    # 其他操作：等待元素出现
                    element_obj = wait.until(EC.presence_of_element_located((by, locator_value)))

                # 执行操作（添加 stale element 重试机制）
                max_retries = 3
                
                if step_data['action_type'] == 'click':
                    for attempt in range(max_retries):
                        try:
                            # 每次重试都重新查找元素（解决stale element问题）
                            if attempt > 0:
                                print(f"⚠️  重新查找元素（Stale Element 重试）... (尝试 {attempt + 1}/{max_retries})")
                                # 增加等待时间，让页面 DOM 稳定（对于 Vue/React 应用很重要）
                                wait_time = 1.0 if attempt == 1 else 1.5  # 第一次重试等1秒，第二次重试等1.5秒
                                print(f"等待 {wait_time}秒 让页面稳定...")
                                time.sleep(wait_time)
                                # 重新定位元素
                                if is_dropdown_option:
                                    element_obj = wait.until(EC.visibility_of_element_located((by, locator_value)))
                                else:
                                    element_obj = wait.until(EC.element_to_be_clickable((by, locator_value)))
                                # 等待元素状态稳定
                                time.sleep(0.3)
                                print(f"✓ 元素重新定位成功")
                            
                            # 对于下拉框选项，先滚动到可视区域
                            if 'dropdown' in locator_value.lower() or 'el-select' in locator_value.lower() or '下拉' in element_name or '选项' in element_name:
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element_obj)
                                    time.sleep(0.3)  # 等待滚动完成
                                except:
                                    pass
                            
                            # 如果是 el-select 容器，尝试点击内部的可点击区域
                            if 'el-select' in locator_value.lower() and 'ancestor::' in locator_value.lower():
                                # 这是点击 el-select 容器，需要找到真正的触发器
                                try:
                                    # 尝试找到并点击内部的 input 或 wrapper
                                    clickable = element_obj.find_element(By.CSS_SELECTOR, '.el-select__wrapper, input')
                                    clickable.click()
                                except:
                                    # 如果找不到，直接点击容器
                                    element_obj.click()
                            else:
                                element_obj.click()
                            
                            step_result['success'] = True
                            break
                        except StaleElementReferenceException:
                            if attempt < max_retries - 1:
                                print(f"⚠️  元素过期，正在重试... ({attempt + 1}/{max_retries})")
                                # 继续下一次循环，会重新查找元素
                                continue
                            else:
                                raise
                        except Exception as click_error:
                            # 如果是下拉框选项且点击失败，尝试使用 JavaScript 点击
                            if attempt < max_retries - 1 and ('not visible' in str(click_error).lower() or 'not interactable' in str(click_error).lower()):
                                print(f"⚠️  元素不可交互，尝试使用 JavaScript 点击... ({attempt + 1}/{max_retries})")
                                try:
                                    driver.execute_script("arguments[0].click();", element_obj)
                                    step_result['success'] = True
                                    break
                                except:
                                    if attempt < max_retries - 1:
                                        time.sleep(0.5)
                                        # 重新定位
                                        if 'dropdown' in locator_value.lower() or 'el-select' in locator_value.lower():
                                            element_obj = wait.until(EC.visibility_of_element_located((by, locator_value)))
                                        else:
                                            element_obj = wait.until(EC.element_to_be_clickable((by, locator_value)))
                                    else:
                                        raise
                            else:
                                raise

                elif step_data['action_type'] == 'fill':
                    # 解析输入值中的变量表达式
                    resolved_value = resolve_variables(step_data['input_value'])
                    
                    for attempt in range(max_retries):
                        try:
                            element_obj.clear()
                            element_obj.send_keys(resolved_value)
                            step_result['success'] = True
                            
                            # 记录解析后的值（用于调试）
                            if resolved_value != step_data['input_value']:
                                step_result['resolved_value'] = resolved_value
                                print(f"  ✓ 变量解析: {step_data['input_value']} -> {resolved_value}")
                            
                            break
                        except StaleElementReferenceException:
                            if attempt < max_retries - 1:
                                print(f"⚠️  元素过期（Stale Element），正在重试... (尝试 {attempt + 2}/{max_retries})")
                                # 增加等待时间，让页面 DOM 稳定
                                wait_time = 1.0 if attempt == 0 else 1.5
                                print(f"等待 {wait_time}秒 让页面稳定...")
                                time.sleep(wait_time)
                                element_obj = wait.until(EC.presence_of_element_located((by, locator_value)))
                                time.sleep(0.3)  # 确保元素状态稳定
                                print(f"✓ 元素重新定位成功")
                            else:
                                raise

                elif step_data['action_type'] == 'getText':
                    for attempt in range(max_retries):
                        try:
                            text = element_obj.text
                            step_result['result'] = text
                            step_result['success'] = True
                            break
                        except StaleElementReferenceException:
                            if attempt < max_retries - 1:
                                print(f"⚠️  元素过期（Stale Element），正在重试... (尝试 {attempt + 2}/{max_retries})")
                                # 增加等待时间，让页面 DOM 稳定
                                wait_time = 1.0 if attempt == 0 else 1.5
                                print(f"等待 {wait_time}秒 让页面稳定...")
                                time.sleep(wait_time)
                                element_obj = wait.until(EC.presence_of_element_located((by, locator_value)))
                                time.sleep(0.3)  # 确保元素状态稳定
                                print(f"✓ 元素重新定位成功")
                            else:
                                raise

                elif step_data['action_type'] == 'hover':
                    from selenium.webdriver.common.action_chains import ActionChains
                    for attempt in range(max_retries):
                        try:
                            ActionChains(driver).move_to_element(element_obj).perform()
                            step_result['success'] = True
                            break
                        except StaleElementReferenceException:
                            if attempt < max_retries - 1:
                                print(f"⚠️  元素过期（Stale Element），正在重试... (尝试 {attempt + 2}/{max_retries})")
                                # 增加等待时间，让页面 DOM 稳定
                                wait_time = 1.0 if attempt == 0 else 1.5
                                print(f"等待 {wait_time}秒 让页面稳定...")
                                time.sleep(wait_time)
                                element_obj = wait.until(EC.presence_of_element_located((by, locator_value)))
                                time.sleep(0.3)  # 确保元素状态稳定
                                print(f"✓ 元素重新定位成功")
                            else:
                                raise

                elif step_data['action_type'] == 'screenshot':
                    screenshot_path = f'screenshots/step_{step_data["step_number"]}.png'
                    driver.save_screenshot(screenshot_path)
                    step_result['screenshot'] = screenshot_path
                    step_result['success'] = True

                elif step_data['action_type'] == 'assert':
                    # 解析断言值中的变量
                    resolved_assert_value = resolve_variables(step_data['assert_value'])
                    if resolved_assert_value != step_data['assert_value']:
                         print(f"  ✓ 断言变量解析: {step_data['assert_value']} -> {resolved_assert_value}")

                    if step_data['assert_type'] == 'textContains':
                        text = element_obj.text
                        if resolved_assert_value in text:
                            step_result['success'] = True
                        else:
                            # 格式化为详细的错误信息，与selenium_engine.py保持一致
                            log = f"✗ 断言失败: 文本不包含 '{resolved_assert_value}'\n"
                            log += f"  - 实际文本: '{text}'"
                            step_result['error'] = log
                    elif step_data['assert_type'] == 'textEquals':
                        text = element_obj.text
                        if text == resolved_assert_value:
                            step_result['success'] = True
                        else:
                            # 格式化为详细的错误信息
                            log = f"✗ 断言失败: 文本不等于 '{resolved_assert_value}'\n"
                            log += f"  - 期望: '{resolved_assert_value}'\n"
                            log += f"  - 实际: '{text}'"
                            step_result['error'] = log
                    elif step_data['assert_type'] == 'isVisible':
                        is_visible = element_obj.is_displayed()
                        step_result['success'] = is_visible
                        if not is_visible:
                            step_result['error'] = f"✗ 断言失败: 元素 '{element_name}' 不可见"
                    elif step_data['assert_type'] == 'exists':
                        # 元素已经找到，说明存在
                        step_result['success'] = True

            else:
                if step_data['action_type'] == 'wait':
                    time.sleep(step_data['wait_time'] / 1000)
                    step_result['success'] = True
                
                elif step_data['action_type'] == 'switchTab':
                    # Selenium 切换标签页逻辑
                    try:
                        # 获取当前所有窗口句柄
                        handles = driver.window_handles
                        
                        # 简单的策略：切换到最后一个窗口（通常是新打开的）
                        # 如果指定了索引，则切换到指定索引
                        target_index = -1
                        if step_data.get('input_value') and str(step_data['input_value']).isdigit():
                            target_index = int(step_data['input_value'])
                        
                        if target_index >= 0 and target_index < len(handles):
                            driver.switch_to.window(handles[target_index])
                        else:
                            driver.switch_to.window(handles[-1])
                        
                        step_result['success'] = True
                        print(f"✓ Selenium 切换标签页成功 (Handle Count: {len(handles)})")
                    except Exception as e:
                        step_result['error'] = f"切换标签页失败: {str(e)}"
                        step_result['success'] = False

        except TimeoutException as e:
            # 格式化为详细的错误信息，与selenium_engine.py保持一致
            execution_time = round(time.time() - start_time, 2)
            element_name = step_data['element'].get('name', '未知元素') if step_data.get('element') else '页面'
            locator_info = f"{step_data['element']['locator_strategy']}={step_data['element']['locator_value']}" if step_data.get('element') else '无'

            # 获取超时设置（从element或step）
            timeout_seconds = 10  # 默认值
            if step_data.get('element') and step_data['element'].get('wait_timeout'):
                timeout_seconds = step_data['element']['wait_timeout']
            elif step_data.get('wait_time'):
                timeout_seconds = step_data['wait_time'] / 1000
            
            # 提取TimeoutException的完整堆栈信息（类似Playwright的显示方式）
            error_parts = []
            
            # 1. 基本错误信息
            base_msg = str(e).strip()
            if base_msg and base_msg not in ['', 'Message:', 'Message: ', 'Message']:
                error_parts.append(base_msg)
            else:
                # 如果str(e)为空，说明是标准的超时异常
                error_parts.append(f"TimeoutException: 等待元素超时")
            
            # 2. 尝试从msg属性获取详细信息
            if hasattr(e, 'msg') and e.msg:
                msg_str = str(e.msg).strip()
                if msg_str and msg_str not in ['', 'Message:', 'Message: ', 'Message']:
                    if msg_str not in error_parts:
                        error_parts.append(msg_str)
            
            # 3. 从args获取
            if hasattr(e, 'args') and len(e.args) > 0 and e.args[0]:
                args_str = str(e.args[0]).strip()
                if args_str and args_str not in ['', 'Message:', 'Message: ', 'Message']:
                    if args_str not in error_parts:
                        error_parts.append(args_str)
            
            # 4. 如果有stacktrace，添加堆栈信息（类似Playwright的格式）
            if hasattr(e, 'stacktrace') and e.stacktrace:
                stacktrace_str = str(e.stacktrace).strip()
                if stacktrace_str:
                    error_parts.append(f"\nSelenium堆栈跟踪:\n{stacktrace_str}")
            
            # 4.5. 添加Python的traceback信息（这个总是可用的）
            try:
                import traceback
                tb_lines = traceback.format_tb(e.__traceback__)
                if tb_lines:
                    # 只取最后2层堆栈（最相关的部分）
                    relevant_tb = tb_lines[-2:] if len(tb_lines) >= 2 else tb_lines
                    tb_str = ''.join(relevant_tb).strip()
                    if tb_str:
                        # 提取等待条件信息（从堆栈中）
                        wait_condition = "未知条件"
                        if 'EC.visibility_of_element_located' in tb_str:
                            wait_condition = "等待元素可见 (visibility_of_element_located)"
                        elif 'EC.element_to_be_clickable' in tb_str:
                            wait_condition = "等待元素可点击 (element_to_be_clickable)"
                        elif 'EC.presence_of_element_located' in tb_str:
                            wait_condition = "等待元素存在 (presence_of_element_located)"
                        
                        error_parts.append(f"\n等待条件: {wait_condition}")
                        error_parts.append(f"\n调用堆栈:\n{tb_str}")
            except:
                pass
            
            # 5. 如果仍然没有有用信息，提供操作类型相关的提示
            if len(error_parts) == 0 or (len(error_parts) == 1 and 'TimeoutException' in error_parts[0]):
                # 添加操作相关的上下文
                action_type_str = step_data.get('action_type', action_type) if isinstance(step_data, dict) else action_type
                if action_type_str == 'click':
                    error_parts.append(f"等待元素可点击失败（超时{timeout_seconds}秒）")
                elif action_type_str == 'fill':
                    error_parts.append(f"等待输入框可用失败（超时{timeout_seconds}秒）")
                elif action_type_str == 'waitFor':
                    error_parts.append(f"等待元素出现失败（超时{timeout_seconds}秒）")
            
            # 合并所有错误信息
            error_msg = '\n'.join(error_parts)

            log = f"✗ 操作超时\n"
            log += f"  - 元素: '{element_name}'\n"
            log += f"  - 定位器: {locator_info}\n"
            log += f"  - 超时设置: {timeout_seconds}秒\n"
            log += f"  - 实际用时: {execution_time}秒\n"
            log += f"  - 错误详情: {error_msg}"
            step_result['error'] = log

        except Exception as e:
            # 格式化为详细的错误信息，与selenium_engine.py保持一致
            execution_time = round(time.time() - start_time, 2)
            element_name = step_data['element'].get('name', '未知元素') if step_data.get('element') else '页面'
            locator_info = f"{step_data['element']['locator_strategy']}={step_data['element']['locator_value']}" if step_data.get('element') else '无'

            # 提取详细的错误信息（改进版 - 添加调试日志）
            error_type = type(e).__name__
            error_msg = ""

            # 🔍 调试：打印异常对象的所有信息
            print(f"=" * 60)
            print(f"🔍 Selenium 异常调试信息 (test_executor):")
            print(f"  异常类型: {error_type}")
            print(f"  str(e): {repr(str(e))}")
            print(f"  hasattr msg: {hasattr(e, 'msg')}")
            if hasattr(e, 'msg'):
                print(f"  e.msg 值: {repr(e.msg)}")
                print(f"  e.msg 类型: {type(e.msg)}")
            print(f"  hasattr args: {hasattr(e, 'args')}")
            if hasattr(e, 'args'):
                print(f"  e.args 长度: {len(e.args)}")
                print(f"  e.args 内容: {e.args}")
            print(f"  hasattr stacktrace: {hasattr(e, 'stacktrace')}")
            if hasattr(e, 'stacktrace'):
                print(f"  e.stacktrace 前200字符: {str(e.stacktrace)[:200]}")
            print(f"  dir(e): {[attr for attr in dir(e) if not attr.startswith('_')]}")
            print(f"=" * 60)

            # 定义无意义的错误信息列表
            meaningless_messages = ['', 'Message', 'Message:', 'Message: ', 'Message:\n']

            # 尝试提取更详细的 Selenium 异常信息（使用优先级策略）
            try:
                # 优先级1: 从 msg 属性获取（Selenium 异常的主要信息源）
                if hasattr(e, 'msg') and e.msg:
                    temp = str(e.msg).strip()
                    if temp not in meaningless_messages:
                        error_msg = temp
                        print(f"✓ 从 e.msg 提取到错误: {error_msg[:100]}")

                # 优先级2: 从 args 获取
                if not error_msg and hasattr(e, 'args') and len(e.args) > 0 and e.args[0]:
                    temp = str(e.args[0]).strip()
                    if temp not in meaningless_messages:
                        error_msg = temp
                        print(f"✓ 从 e.args[0] 提取到错误: {error_msg[:100]}")

                # 优先级3: 使用 str(e)，但排除无意义的值
                if not error_msg:
                    temp = str(e).strip()
                    if temp not in meaningless_messages:
                        error_msg = temp
                        print(f"✓ 从 str(e) 提取到错误: {error_msg[:100]}")

                # 优先级4: 从 stacktrace 提取
                if not error_msg and hasattr(e, 'stacktrace') and e.stacktrace:
                    error_msg = f"详细堆栈:\n{e.stacktrace[:300]}"
                    print(f"✓ 从 e.stacktrace 提取到错误")

                # 优先级5: 从 __dict__ 提取有用信息
                if not error_msg and hasattr(e, '__dict__'):
                    useful_attrs = {k: v for k, v in e.__dict__.items()
                                   if v is not None and not k.startswith('_') and k not in ['msg', 'args', 'stacktrace']}
                    if useful_attrs:
                        error_msg = f"异常属性: {useful_attrs}"
                        print(f"✓ 从 e.__dict__ 提取到错误")

                # 如果还是没有，使用默认信息
                if not error_msg:
                    error_msg = f"未知错误 (异常类型: {error_type})"
                    print(f"⚠️ 无法提取任何有用信息，使用默认错误消息")

            except Exception as extract_error:
                print(f"⚠️  提取错误信息时出错: {extract_error}")
                error_msg = f"无法提取详细错误信息 (异常类型: {error_type})"

            # 添加异常类型前缀（如果还没有）
            if error_type not in error_msg and error_type != 'Exception':
                error_msg = f"{error_type}: {error_msg}"

            log = f"✗ 执行失败\n"
            log += f"  - 元素: '{element_name}'\n"
            log += f"  - 定位器: {locator_info}\n"
            log += f"  - 执行时间: {execution_time}秒\n"
            log += f"  - 错误: {error_msg}"
            step_result['error'] = log

            # 打印详细日志便于调试
            print(f"❌ Selenium 步骤执行失败:")
            print(f"   异常类型: {error_type}")
            print(f"   错误信息: {error_msg[:500]}")  # 限制长度避免刷屏

        return step_result

    def execute_test_suite_ai(self, task_description):
        """
        使用 AI Agent 执行测试套件
        
        Args:
            task_description: 自然语言任务描述
            
        Returns:
            dict: 执行结果，包含状态、步骤详情等
        """
        from .ai_agent import run_ai_task_sync
        
        print(f"🤖 开始 AI 模式执行测试套件: {self.test_suite.name}")
        print(f"📝 任务描述: {task_description}")
        
        start_time = time.time()
        
        try:
            # 更新套件状态为运行中
            self.test_suite.execution_status = 'running'
            self.test_suite.save()
            
            # 执行 AI 任务
            print("🚀 正在调用 AI Agent...")
            history = run_ai_task_sync(task_description)
            
            # 解析执行结果
            all_results = history.all_results if hasattr(history, 'all_results') else []
            model_outputs = history.all_model_outputs if hasattr(history, 'all_model_outputs') else []
            
            # 统计成功和失败的步骤
            passed_count = 0
            failed_count = 0
            steps_detail = []
            
            for i, result in enumerate(all_results):
                step_info = {
                    'step': i + 1,
                    'action': result.extracted_content or str(result.error) if result.error else '未知操作',
                    'success': not result.error,
                    'error': str(result.error) if result.error else None
                }
                
                if result.error:
                    failed_count += 1
                    print(f"  ❌ 步骤 {i + 1}: {step_info['action']} - 失败")
                else:
                    passed_count += 1
                    print(f"  ✅ 步骤 {i + 1}: {step_info['action']}")
                
                steps_detail.append(step_info)
            
            # 判断整体执行状态
            execution_status = 'passed' if failed_count == 0 and passed_count > 0 else 'failed'
            
            # 计算执行时间
            duration = time.time() - start_time
            
            # 更新套件状态
            self.test_suite.execution_status = execution_status
            self.test_suite.passed_count = passed_count
            self.test_suite.failed_count = failed_count
            self.test_suite.save()
            
            # 更新执行记录（如果存在）
            if hasattr(self, 'execution') and self.execution:
                self.update_execution_result(
                    status=execution_status,
                    passed=passed_count,
                    failed=failed_count,
                    skipped=0,
                    duration=duration
                )
            
            result_summary = {
                'status': 'success',
                'execution_status': execution_status,
                'passed_count': passed_count,
                'failed_count': failed_count,
                'total_steps': len(all_results),
                'duration': round(duration, 2),
                'steps': steps_detail,
                'model_outputs': model_outputs
            }
            
            print(f"\n✅ AI 执行完成!")
            print(f"   状态: {execution_status}")
            print(f"   通过: {passed_count}, 失败: {failed_count}")
            print(f"   耗时: {duration:.2f}秒")
            
            return result_summary
            
        except Exception as e:
            # 执行失败，更新状态
            duration = time.time() - start_time
            error_msg = str(e)
            
            print(f"\n❌ AI 执行失败: {error_msg}")
            
            self.test_suite.execution_status = 'failed'
            self.test_suite.failed_count = 1
            self.test_suite.passed_count = 0
            self.test_suite.save()
            
            # 更新执行记录
            if hasattr(self, 'execution') and self.execution:
                self.update_execution_result(
                    status='failed',
                    passed=0,
                    failed=1,
                    skipped=0,
                    duration=duration,
                    error_msg=error_msg
                )
            
            return {
                'status': 'error',
                'execution_status': 'failed',
                'error': error_msg,
                'duration': round(duration, 2)
            }
