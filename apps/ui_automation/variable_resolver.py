"""
UI自动化测试变量解析器
支持在测试步骤的输入值中使用动态函数表达式
语法：${function_name(args)}
"""
import re
import random
import string
import uuid
import hashlib
import base64
from datetime import datetime, timedelta


class VariableResolver:
    """UI自动化测试变量解析器"""
    
    def __init__(self):
        # 注册所有内置函数
        self.functions = {
            # 随机数函数
            'random_int': self._random_int,
            'random_float': self._random_float,
            'random_digits': self._random_digits,
            
            # 随机字符串函数
            'random_string': self._random_string,
            'random_letters': self._random_letters,
            'random_chinese': self._random_chinese,
            
            # 业务数据函数 (旧版命名兼容)
            'random_phone': self._random_phone,
            'random_email': self._random_email,
            'random_id_card': self._random_id_card,
            'random_name': self._random_name,
            'random_company': self._random_company,
            'random_address': self._random_address,
            
            # 业务数据函数 (新版命名 - 前端变量助手使用)
            'generate_chinese_name': self._generate_chinese_name,
            'generate_chinese_phone': self._generate_chinese_phone,
            'generate_chinese_email': self._generate_chinese_email,
            'generate_chinese_address': self._generate_chinese_address,
            'generate_id_card': self._generate_id_card,
            'generate_company_name': self._generate_company_name,
            'generate_bank_card': self._generate_bank_card,
            'generate_hk_id_card': self._generate_hk_id_card,
            'generate_business_license': self._generate_business_license,
            'generate_user_profile': self._generate_user_profile,
            'generate_coordinates': self._generate_coordinates,
            
            # 时间日期函数
            'timestamp': self._timestamp,
            'timestamp_sec': self._timestamp_sec,
            'datetime': self._datetime,
            'date': self._date,
            'time': self._time,
            'date_offset': self._date_offset,
            
            # 其他工具函数
            'uuid': self._uuid,
            'guid': self._guid,
            'base64': self._base64,
            'md5': self._md5,
            'sha1': self._sha1,
            'sha256': self._sha256,
            'random_mac': self._random_mac,
            'random_ip': self._random_ip,
            'random_password': self._random_password,
        }
    
    def resolve(self, text):
        """解析文本中的所有变量表达式
        
        Args:
            text: 包含变量表达式的文本，如 "user_${random_string(6)}@test.com"
            
        Returns:
            解析后的文本，如 "user_abc123@test.com"
        """
        if not text or not isinstance(text, str):
            return text
        
        # 匹配 ${function_name(args)} 模式
        pattern = r'\$\{([^}]+)\}'
        
        def replace_func(match):
            expression = match.group(1)
            try:
                result = str(self._evaluate_expression(expression))
                print(f"✓ 变量解析成功: ${{{expression}}} -> {result}")
                return result
            except Exception as e:
                # 如果解析失败，保留原始表达式
                print(f"⚠️  变量解析失败: ${{{expression}}} - {str(e)}")
                return match.group(0)
        
        result = re.sub(pattern, replace_func, text)
        if result != text:
            print(f"✓ 文本变量解析: '{text}' -> '{result}'")
        return result
    
    def _evaluate_expression(self, expression):
        """评估单个表达式
        
        Args:
            expression: 函数表达式，如 "random_int(100, 200)" 或 "timestamp()"
            
        Returns:
            函数执行结果
        """
        # 解析函数名和参数
        match = re.match(r'(\w+)\((.*)\)', expression.strip())
        if not match:
            # 无参数函数
            func_name = expression.strip()
            args = []
        else:
            func_name = match.group(1)
            args_str = match.group(2)
            args = self._parse_args(args_str)
        
        # 调用对应函数
        if func_name in self.functions:
            return self.functions[func_name](*args)
        else:
            raise ValueError(f"未知函数: {func_name}")
    
    def _parse_args(self, args_str):
        """解析函数参数
        
        Args:
            args_str: 参数字符串，如 "100, 200" 或 "YYYY-MM-DD"
            
        Returns:
            参数列表
        """
        if not args_str.strip():
            return []
        
        args = []
        for arg in args_str.split(','):
            arg = arg.strip()
            # 尝试转换为数字
            try:
                if '.' in arg:
                    args.append(float(arg))
                else:
                    args.append(int(arg))
            except ValueError:
                # 如果是纯字母（参数名如 'count', 'gender' 等），跳过（使用函数默认值）
                if arg.isalpha():
                    continue
                # 移除引号
                args.append(arg.strip('\'"'))
        return args
    
    # ========== 随机数函数 ==========
    
    def _random_int(self, min_val=0, max_val=100):
        """生成随机整数
        
        Args:
            min_val: 最小值（包含）
            max_val: 最大值（包含）
            
        Returns:
            随机整数
            
        Example:
            ${random_int(1000, 9999)} -> 5678
        """
        return random.randint(int(min_val), int(max_val))
    
    def _random_float(self, min_val=0.0, max_val=1.0, decimals=2):
        """生成随机浮点数
        
        Args:
            min_val: 最小值
            max_val: 最大值
            decimals: 小数位数
            
        Returns:
            随机浮点数
            
        Example:
            ${random_float(0, 100, 2)} -> 45.67
        """
        value = random.uniform(float(min_val), float(max_val))
        return round(value, int(decimals))
    
    def _random_digits(self, length=6):
        """生成随机数字字符串
        
        Args:
            length: 字符串长度
            
        Returns:
            随机数字字符串
            
        Example:
            ${random_digits(6)} -> "123456"
        """
        return ''.join(random.choices(string.digits, k=int(length)))
    
    # ========== 随机字符串函数 ==========
    
    def _random_string(self, length=8):
        """生成随机字母数字字符串
        
        Args:
            length: 字符串长度
            
        Returns:
            随机字母数字字符串
            
        Example:
            ${random_string(8)} -> "aB3xY9zK"
        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=int(length)))
    
    def _random_letters(self, length=8):
        """生成随机字母字符串
        
        Args:
            length: 字符串长度
            
        Returns:
            随机字母字符串
            
        Example:
            ${random_letters(8)} -> "aBxYzKmN"
        """
        return ''.join(random.choices(string.ascii_letters, k=int(length)))
    
    def _random_chinese(self, length=2):
        """生成随机中文字符
        
        Args:
            length: 字符数量
            
        Returns:
            随机中文字符串
            
        Example:
            ${random_chinese(2)} -> "张三"
        """
        # 常用汉字Unicode范围
        chinese_chars = []
        for _ in range(int(length)):
            chinese_chars.append(chr(random.randint(0x4e00, 0x9fa5)))
        return ''.join(chinese_chars)
    
    # ========== 业务数据函数 ==========
    
    def _random_phone(self):
        """生成随机手机号（中国大陆）
        
        Returns:
            11位手机号
            
        Example:
            ${random_phone()} -> "13812345678"
        """
        prefixes = [
            '130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
            '150', '151', '152', '153', '155', '156', '157', '158', '159',
            '180', '181', '182', '183', '184', '185', '186', '187', '188', '189',
            '170', '171', '176', '177', '178'
        ]
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=8))
        return prefix + suffix
    
    def _random_email(self):
        """生成随机邮箱地址
        
        Returns:
            邮箱地址
            
        Example:
            ${random_email()} -> "abc12345@test.com"
        """
        username = self._random_string(8).lower()
        domains = ['test.com', 'example.com', 'demo.com', 'mail.com', 'qq.com', '163.com']
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def _random_id_card(self):
        """生成随机身份证号（18位）
        
        Returns:
            18位身份证号
            
        Example:
            ${random_id_card()} -> "110101199001011234"
            
        Note:
            简化实现，不保证完全符合校验规则，仅用于测试
        """
        # 地区代码（北京、上海、广州等）
        area_codes = ['110101', '310101', '440101', '500101', '320101', '330101']
        area_code = random.choice(area_codes)
        
        # 出生日期
        birth_year = random.randint(1970, 2005)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # 简化处理，避免月份天数问题
        birth_date = f"{birth_year}{birth_month:02d}{birth_day:02d}"
        
        # 顺序码
        sequence = f"{random.randint(0, 999):03d}"
        
        # 校验码（简化处理，随机生成）
        check_digits = string.digits + 'X'
        check_digit = random.choice(check_digits)
        
        return area_code + birth_date + sequence + check_digit
    
    def _random_name(self):
        """生成随机中文姓名
        
        Returns:
            中文姓名（2-3个字）
            
        Example:
            ${random_name()} -> "张伟"
        """
        # 常见姓氏
        surnames = [
            '王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
            '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高'
        ]
        
        # 常见名字用字
        name_chars = [
            '伟', '芳', '娜', '秀', '敏', '静', '丽', '强', '磊', '军',
            '洋', '勇', '艳', '杰', '涛', '明', '超', '秀', '英', '华',
            '文', '玉', '建', '国', '春', '梅', '兰', '红', '霞', '鹏'
        ]
        
        surname = random.choice(surnames)
        name_length = random.randint(1, 2)
        given_name = ''.join(random.choices(name_chars, k=name_length))
        
        return surname + given_name
    
    def _random_company(self):
        """生成随机公司名称
        
        Returns:
            公司名称
            
        Example:
            ${random_company()} -> "北京科技有限公司"
        """
        cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安']
        types = ['科技', '网络', '信息', '软件', '电子', '智能', '数据', '云计算']
        suffixes = ['有限公司', '股份有限公司', '技术有限公司', '集团有限公司']
        
        city = random.choice(cities)
        type_name = random.choice(types)
        suffix = random.choice(suffixes)
        
        return f"{city}{type_name}{suffix}"
    
    def _random_address(self):
        """生成随机地址
        
        Returns:
            地址
            
        Example:
            ${random_address()} -> "北京市朝阳区建国路123号"
        """
        cities = ['北京市', '上海市', '广州市', '深圳市', '杭州市', '成都市']
        districts = ['朝阳区', '海淀区', '浦东新区', '天河区', '南山区', '西湖区']
        streets = ['建国路', '中山路', '人民路', '解放路', '和平路', '胜利路']
        
        city = random.choice(cities)
        district = random.choice(districts)
        street = random.choice(streets)
        number = random.randint(1, 999)
        
        return f"{city}{district}{street}{number}号"
    
    # ========== 时间日期函数 ==========
    
    def _timestamp(self):
        """获取当前时间戳（毫秒）
        
        Returns:
            13位时间戳
            
        Example:
            ${timestamp()} -> 1702234567890
        """
        return int(datetime.now().timestamp() * 1000)
    
    def _timestamp_sec(self):
        """获取当前时间戳（秒）
        
        Returns:
            10位时间戳
            
        Example:
            ${timestamp_sec()} -> 1702234567
        """
        return int(datetime.now().timestamp())
    
    def _datetime(self, format_str='YYYY-MM-DD HH:mm:ss'):
        """格式化当前日期时间
        
        Args:
            format_str: 日期时间格式，支持 YYYY MM DD HH mm ss
            
        Returns:
            格式化的日期时间字符串
            
        Example:
            ${datetime(YYYY-MM-DD HH:mm:ss)} -> "2024-12-10 23:05:30"
        """
        # 转换为Python datetime格式
        format_str = format_str.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
        format_str = format_str.replace('HH', '%H').replace('mm', '%M').replace('ss', '%S')
        return datetime.now().strftime(format_str)
    
    def _date(self, format_str='YYYY-MM-DD'):
        """格式化当前日期
        
        Args:
            format_str: 日期格式，支持 YYYY MM DD
            
        Returns:
            格式化的日期字符串
            
        Example:
            ${date(YYYY-MM-DD)} -> "2024-12-10"
        """
        format_str = format_str.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
        return datetime.now().strftime(format_str)
    
    def _time(self, format_str='HH:mm:ss'):
        """格式化当前时间
        
        Args:
            format_str: 时间格式，支持 HH mm ss
            
        Returns:
            格式化的时间字符串
            
        Example:
            ${time(HH:mm:ss)} -> "23:05:30"
        """
        format_str = format_str.replace('HH', '%H').replace('mm', '%M').replace('ss', '%S')
        return datetime.now().strftime(format_str)
    
    def _date_offset(self, days=0, format_str='YYYY-MM-DD'):
        """获取偏移日期
        
        Args:
            days: 偏移天数，正数为未来，负数为过去
            format_str: 日期格式
            
        Returns:
            格式化的日期字符串
            
        Example:
            ${date_offset(-1, YYYY-MM-DD)} -> "2024-12-09" (昨天)
            ${date_offset(7, YYYY-MM-DD)} -> "2024-12-17" (7天后)
        """
        target_date = datetime.now() + timedelta(days=int(days))
        format_str = format_str.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
        return target_date.strftime(format_str)
    
    # ========== 其他工具函数 ==========
    
    def _uuid(self):
        """生成UUID
        
        Returns:
            UUID字符串
            
        Example:
            ${uuid()} -> "550e8400-e29b-41d4-a716-446655440000"
        """
        return str(uuid.uuid4())
    
    def _guid(self):
        """生成GUID（同UUID）
        
        Returns:
            GUID字符串
            
        Example:
            ${guid()} -> "550e8400-e29b-41d4-a716-446655440000"
        """
        return str(uuid.uuid4())
    
    def _base64(self, text):
        """Base64编码
        
        Args:
            text: 要编码的文本
            
        Returns:
            Base64编码后的字符串
            
        Example:
            ${base64(hello)} -> "aGVsbG8="
        """
        return base64.b64encode(str(text).encode()).decode()
    
    def _md5(self, text):
        """MD5哈希

        Args:
            text: 要哈希的文本

        Returns:
            MD5哈希值（32位小写）

        Example:
            ${md5(hello)} -> "5d41402abc4b2a76b9719d911017c592"
        """
        return hashlib.md5(str(text).encode()).hexdigest()

    def _sha1(self, text):
        """SHA1哈希

        Args:
            text: 要哈希的文本

        Returns:
            SHA1哈希值（40位小写）

        Example:
            ${sha1(hello)} -> "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
        """
        import sha1
        return hashlib.sha1(str(text).encode()).hexdigest()

    def _sha256(self, text):
        """SHA256哈希

        Args:
            text: 要哈希的文本

        Returns:
            SHA256哈希值（64位小写）

        Example:
            ${sha256(hello)} -> "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        """
        return hashlib.sha256(str(text).encode()).hexdigest()

    def _random_mac(self):
        """生成随机MAC地址

        Returns:
            MAC地址（格式: xx:xx:xx:xx:xx:xx）

        Example:
            ${random_mac()} -> "00:1a:2b:3c:4d:5e"
        """
        mac = [random.randint(0x00, 0xff) for _ in range(6)]
        # 确保第一个字节的最低位为0（单播地址）
        mac[0] = mac[0] & 0xfe
        return ':'.join(f'{x:02x}' for x in mac)

    def _random_ip(self, version=4):
        """生成随机IP地址

        Args:
            version: IP版本（4或6）

        Returns:
            IP地址字符串

        Example:
            ${random_ip()} -> "192.168.1.100"
            ${random_ip(6)} -> "2001:db8::1"
        """
        if version == 4:
            return '.'.join(str(random.randint(0, 255)) for _ in range(4))
        elif version == 6:
            # 简化生成随机IPv6地址
            parts = []
            for i in range(8):
                parts.append(f'{random.randint(0, 0xffff):04x}')
            return ':'.join(parts)
        else:
            return '.'.join(str(random.randint(0, 255)) for _ in range(4))

    def _random_password(self, length=12):
        """生成随机密码

        Args:
            length: 密码长度

        Returns:
            随机密码（包含大小写字母、数字和特殊字符）

        Example:
            ${random_password(16)} -> "aB3$xY9zK@2#mN"
        """
        chars = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(random.choices(chars, k=int(length)))

    # ========== 新版业务数据函数 (前端变量助手使用) ==========

    def _generate_chinese_name(self, gender='random', count=1):
        """生成中文姓名

        Args:
            gender: 性别 ('male', 'female', 'random')
            count: 生成数量

        Returns:
            中文姓名或姓名列表

        Example:
            ${generate_chinese_name(random, 1)} -> "张伟"
        """
        surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
                    '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高']
        male_names = ['伟', '强', '磊', '军', '洋', '勇', '杰', '涛', '明', '超',
                      '鹏', '飞', '波', '辉', '刚', '健', '俊', '峰', '建', '华']
        female_names = ['芳', '娜', '秀', '敏', '静', '丽', '艳', '娟', '霞', '玲',
                        '婷', '雪', '梅', '兰', '红', '英', '华', '文', '玉', '春']

        def generate_one():
            surname = random.choice(surnames)
            if gender == 'male':
                name = random.choice(male_names)
                if random.random() > 0.5:
                    name += random.choice(male_names)
            elif gender == 'female':
                name = random.choice(female_names)
                if random.random() > 0.5:
                    name += random.choice(female_names)
            else:
                all_names = male_names + female_names
                name = random.choice(all_names)
                if random.random() > 0.5:
                    name += random.choice(all_names)
            return surname + name

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_chinese_phone(self, count=1):
        """生成中国手机号

        Args:
            count: 生成数量

        Returns:
            手机号或手机号列表

        Example:
            ${generate_chinese_phone(1)} -> "13812345678"
        """
        prefixes = ['138', '139', '135', '136', '137', '150', '151', '152', '157', '158', '159',
                    '182', '183', '187', '188', '130', '131', '132', '155', '156', '185', '186']

        def generate_one():
            prefix = random.choice(prefixes)
            suffix = ''.join(random.choices(string.digits, k=8))
            return prefix + suffix

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_chinese_email(self, count=1):
        """生成邮箱地址

        Args:
            count: 生成数量

        Returns:
            邮箱或邮箱列表

        Example:
            ${generate_chinese_email(1)} -> "zhangwei123@test.com"
        """
        domains = ['qq.com', '163.com', '126.com', 'gmail.com', 'outlook.com', 'test.com']

        def generate_one():
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            domain = random.choice(domains)
            return f"{username}@{domain}"

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_chinese_address(self, full_address=True, count=1):
        """生成中国地址

        Args:
            full_address: 是否生成完整地址
            count: 生成数量

        Returns:
            地址或地址列表

        Example:
            ${generate_chinese_address(true, 1)} -> "北京市朝阳区建国路123号"
        """
        provinces = ['北京市', '上海市', '广东省', '浙江省', '江苏省', '四川省', '湖北省', '陕西省']
        cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安']
        districts = ['朝阳区', '海淀区', '浦东新区', '天河区', '南山区', '西湖区', '鼓楼区', '武昌区']
        streets = ['建国路', '中山路', '人民路', '解放路', '和平路', '胜利路', '建设路', '文化路']

        def generate_one():
            if full_address:
                province = random.choice(provinces)
                district = random.choice(districts)
                street = random.choice(streets)
                number = random.randint(1, 999)
                return f"{province}{district}{street}{number}号"
            else:
                city = random.choice(cities)
                district = random.choice(districts)
                return f"{city}{district}"

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_id_card(self, count=1):
        """生成身份证号

        Args:
            count: 生成数量

        Returns:
            身份证号或身份证号列表

        Example:
            ${generate_id_card(1)} -> "110101199001011234"
        """
        area_codes = ['110101', '310101', '440101', '500101', '320101', '330101', '510101', '420101']

        def generate_one():
            area_code = random.choice(area_codes)
            birth_year = random.randint(1970, 2005)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birth_date = f"{birth_year}{birth_month:02d}{birth_day:02d}"
            sequence = f"{random.randint(0, 999):03d}"
            check_digit = random.choice(string.digits + 'X')
            return area_code + birth_date + sequence + check_digit

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_company_name(self, count=1):
        """生成公司名称

        Args:
            count: 生成数量

        Returns:
            公司名称或公司名称列表

        Example:
            ${generate_company_name(1)} -> "北京科技有限公司"
        """
        cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安', '南京']
        types = ['科技', '网络', '信息', '软件', '电子', '智能', '数据', '云计算', '互联网']
        suffixes = ['有限公司', '股份有限公司', '技术有限公司', '集团有限公司', '网络科技有限公司']

        def generate_one():
            city = random.choice(cities)
            type_name = random.choice(types)
            suffix = random.choice(suffixes)
            return f"{city}{type_name}{suffix}"

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_bank_card(self, count=1):
        """生成银行卡号

        Args:
            count: 生成数量

        Returns:
            银行卡号或银行卡号列表

        Example:
            ${generate_bank_card(1)} -> "6222021234567890123"
        """
        prefixes = ['622202', '622203', '622208', '622848', '622845', '622846', '622847']

        def generate_one():
            prefix = random.choice(prefixes)
            suffix = ''.join(random.choices(string.digits, k=13))
            return prefix + suffix

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_hk_id_card(self, count=1):
        """生成香港身份证号

        Args:
            count: 生成数量

        Returns:
            香港身份证号或身份证号列表

        Example:
            ${generate_hk_id_card(1)} -> "Y123456(7)"
        """
        def generate_one():
            prefix = random.choice(string.ascii_uppercase)
            numbers = ''.join(random.choices(string.digits, k=6))
            check = random.randint(0, 9)
            return f"{prefix}{numbers}({check})"

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_business_license(self, count=1):
        """生成营业执照号

        Args:
            count: 生成数量

        Returns:
            营业执照号或营业执照号列表

        Example:
            ${generate_business_license(1)} -> "91110108MA1234567X"
        """
        def generate_one():
            prefix = '91'
            area_code = random.choice(['110105', '110108', '310101', '440106', '330106'])
            org_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            check = random.choice(string.ascii_uppercase + string.digits)
            return f"{prefix}{area_code}{org_code}{check}"

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_user_profile(self, count=1):
        """生成用户档案

        Args:
            count: 生成数量

        Returns:
            用户档案JSON字符串或档案列表
        """
        def generate_one():
            import json
            profile = {
                'name': self._generate_chinese_name(),
                'phone': self._generate_chinese_phone(),
                'email': self._generate_chinese_email(),
                'id_card': self._generate_id_card(),
                'address': self._generate_chinese_address()
            }
            return json.dumps(profile, ensure_ascii=False)

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]

    def _generate_coordinates(self, count=1):
        """生成经纬度坐标

        Args:
            count: 生成数量

        Returns:
            经纬度坐标或坐标列表

        Example:
            ${generate_coordinates(1)} -> "39.9042,116.4074"
        """
        def generate_one():
            # 中国范围内的经纬度
            lat = round(random.uniform(18.0, 53.5), 4)
            lng = round(random.uniform(73.5, 135.0), 4)
            return f"{lat},{lng}"

        count = int(count)
        if count == 1:
            return generate_one()
        return [generate_one() for _ in range(count)]


# 全局单例
_resolver = VariableResolver()


def resolve_variables(text):
    """便捷函数：解析文本中的变量表达式
    
    Args:
        text: 包含变量表达式的文本
        
    Returns:
        解析后的文本
        
    Example:
        >>> resolve_variables("user_${random_string(6)}@test.com")
        "user_abc123@test.com"
        
        >>> resolve_variables("手机号：${random_phone()}")
        "手机号：13812345678"
    """
    return _resolver.resolve(text)
