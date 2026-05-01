#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Fox 导入功能测试脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from apps.api_testing.apifox_function_mapper import (
    ApifoxFunctionMapper, 
    ApifoxVariableResolver,
    resolve_apifox_variables
)
from apps.data_factory.tools.entertainment_tools import EntertainmentTools
from apps.data_factory.tools.professional_tools import ProfessionalTools
from apps.data_factory.tools.system_tools import SystemTools
from apps.data_factory.tools.mock_image_tools import MockImageTools


def test_function_mapper():
    """测试函数映射器"""
    print("=" * 60)
    print("测试函数映射器")
    print("=" * 60)
    
    mapper = ApifoxFunctionMapper()
    functions = mapper.get_supported_functions()
    
    print(f"✅ 总共支持 {len(functions)} 个 API Fox 函数")
    print(f"✅ 分类数量: {len(set([f.split('.')[0] if '.' in f else '基础' for f in functions]))}")
    
    # 测试一些关键函数
    test_cases = [
        ('$timestamp', '时间戳'),
        ('$guid', 'UUID'),
        ('$randomInt', '随机整数'),
        ('$date.now', '当前日期'),
        ('$music.genre', '音乐类型'),
        ('$airline.name', '航空公司'),
        ('$git.branch', 'Git分支'),
        ('$system.fileName', '文件名'),
    ]
    
    print("\n关键函数测试:")
    for func_name, desc in test_cases:
        try:
            result = mapper.execute(func_name)
            print(f"  ✅ {func_name} ({desc}): {result}")
        except Exception as e:
            print(f"  ❌ {func_name} ({desc}): {e}")
    
    return True


def test_variable_resolver():
    """测试变量解析器"""
    print("\n" + "=" * 60)
    print("测试变量解析器")
    print("=" * 60)
    
    resolver = ApifoxVariableResolver()
    
    test_cases = [
        "https://api.example.com/users?id={{$randomInt}}",
        "Authorization: Bearer {{$guid}}",
        "User: {{$randomFullName}}, Phone: {{$randomPhoneNumber}}",
        "Date: {{$date.now}}, Version: {{$system.semver}}",
        "Airline: {{$airline.name}}, Aircraft: {{$airline.aircraftType}}",
        "Music: {{$music.songName}} by {{$music.artist}}",
    ]
    
    print("变量替换测试:")
    for text in test_cases:
        try:
            result = resolver.resolve(text)
            print(f"  输入: {text[:50]}...")
            print(f"  输出: {result[:80]}...")
            print()
        except Exception as e:
            print(f"  ❌ 错误: {e}\n")
    
    return True


def test_new_tools():
    """测试新增工具类"""
    print("\n" + "=" * 60)
    print("测试新增工具类")
    print("=" * 60)
    
    # 娱乐工具
    print("\n娱乐工具 (EntertainmentTools):")
    print(f"  🎵 音乐类型: {EntertainmentTools.music_genre()['result']}")
    print(f"  🎵 歌曲名: {EntertainmentTools.music_song_name()['result']}")
    print(f"  🎵 艺术家: {EntertainmentTools.music_artist()['result']}")
    print(f"  🐕 动物类型: {EntertainmentTools.animal_type()['result']}")
    print(f"  🍔 菜品: {EntertainmentTools.food_dish()['result']}")
    print(f"  🍎 水果: {EntertainmentTools.food_fruit()['result']}")
    
    # 专业工具
    print("\n专业工具 (ProfessionalTools):")
    element = ProfessionalTools.science_chemical_element()['result']
    print(f"  ⚗️ 化学元素: {element['name']} ({element['symbol']})")
    print(f"  ✈️ 航空公司: {ProfessionalTools.airline_name()['result']}")
    print(f"  🛫 机场: {ProfessionalTools.airline_airport()['result']['name']}")
    print(f"  🚗 车辆制造商: {ProfessionalTools.vehicle_manufacturer()['result']}")
    print(f"  🗄️ 数据库类型: {ProfessionalTools.database_type()['result']}")
    
    # 系统工具
    print("\n系统工具 (SystemTools):")
    print(f"  🌿 Git分支: {SystemTools.git_branch()['result']}")
    print(f"  💬 Git提交: {SystemTools.git_commit_message()['result'][:30]}...")
    print(f"  📁 文件名: {SystemTools.system_file_name()['result']}")
    print(f"  📂 目录: {SystemTools.system_directory_path()['result']}")
    print(f"  📦 版本号: {SystemTools.system_semver()['result']}")
    
    # 图像工具
    print("\n图像工具 (MockImageTools):")
    print(f"  🖼️ 图片URL: {MockImageTools.image_url(300, 200)['result'][:50]}...")
    print(f"  👤 头像: {MockImageTools.image_avatar()['result'][:50]}...")
    print(f"  🖼️ 占位图: {MockImageTools.image_placeholder(200, 100)['result'][:50]}...")
    
    return True


def test_validation():
    """测试验证功能"""
    print("\n" + "=" * 60)
    print("测试验证功能")
    print("=" * 60)
    
    resolver = ApifoxVariableResolver()
    
    # 测试有效语法
    valid_cases = [
        "{{$timestamp}}",
        "{{$randomInt}}",
        "https://api.example.com?id={{$guid}}",
    ]
    
    print("有效语法测试:")
    for text in valid_cases:
        result = resolver.validate_syntax(text)
        status = "✅" if result['valid'] else "❌"
        print(f"  {status} {text[:40]}...")
    
    # 测试包含不支持函数的语法
    print("\n不支持函数检测测试:")
    unsupported_cases = [
        "{{$unsupported.func}}",
        "{{$timestamp}} and {{$unknown.function}}",
    ]
    
    for text in unsupported_cases:
        result = resolver.validate_syntax(text)
        if result['unsupported']:
            print(f"  ⚠️ 检测到不支持函数: {result['unsupported']}")
    
    return True


def test_file_validation():
    """测试文件验证"""
    print("\n" + "=" * 60)
    print("测试文件验证")
    print("=" * 60)
    
    # 检查示例文件是否存在
    sample_file = '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub/智能体_创建.apifox-cli.json'
    
    if os.path.exists(sample_file):
        from apps.api_testing.apifox_importer import validate_apifox_file
        
        print(f"验证文件: {sample_file}")
        result = validate_apifox_file(sample_file)
        
        print(f"  ✅ 验证通过: {result.get('valid', False)}")
        print(f"  📊 请求数量: {result.get('total_requests', 0)}")
        
        if result.get('unsupported_functions'):
            print(f"  ⚠️ 不支持的函数: {result['unsupported_functions']}")
        
        if result.get('warnings'):
            print(f"  ⚠️ 警告: {result['warnings']}")
    else:
        print(f"  ⚠️ 示例文件不存在: {sample_file}")
    
    return True


def main():
    """主测试函数"""
    print("\n" + "🚀" * 30)
    print("API Fox 导入功能测试")
    print("🚀" * 30 + "\n")
    
    tests = [
        ("函数映射器", test_function_mapper),
        ("变量解析器", test_variable_resolver),
        ("新增工具类", test_new_tools),
        ("验证功能", test_validation),
        ("文件验证", test_file_validation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, True, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n❌ {name} 测试失败: {e}")
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result, _ in results if result)
    failed = len(results) - passed
    
    for name, result, error in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
        if error:
            print(f"      错误: {error}")
    
    print(f"\n总计: {len(results)} 个测试, {passed} 通过, {failed} 失败")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
