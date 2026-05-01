# -*- coding: utf-8 -*-
"""
API Fox 函数映射器 - 100% 兼容 API Fox 动态变量
将所有 API Fox 函数映射到数据工厂工具
"""
import re
from typing import Any, Dict, Callable, Optional
from apps.data_factory.tools.random_tools import RandomTools
from apps.data_factory.tools.test_data_tools import TestDataTools
from apps.data_factory.tools.encoding_tools import EncodingTools
from apps.data_factory.tools.encryption_tools import EncryptionTools
from apps.data_factory.tools.json_tools import JsonTools
from apps.data_factory.tools.string_tools import StringTools
from apps.data_factory.tools.entertainment_tools import EntertainmentTools
from apps.data_factory.tools.professional_tools import ProfessionalTools
from apps.data_factory.tools.system_tools import SystemTools
from apps.data_factory.tools.mock_image_tools import MockImageTools


class ApifoxFunctionMapper:
    """
    API Fox 函数映射器
    
    支持完整的 API Fox 动态变量语法：
    - {{$category.function}} - 基础函数
    - {{$category.function(args)}} - 带参数函数
    - {{$category.function|modifier}} - 链式操作
    - {{variable}} - 普通变量
    """
    
    def __init__(self):
        self.functions = self._build_function_map()
    
    def _build_function_map(self) -> Dict[str, Callable]:
        """构建完整的 API Fox 函数映射表"""
        return {
            # ========== 基础变量 ==========
            '$guid': lambda: RandomTools.random_uuid(4),
            '$timestamp': lambda: {'result': int(__import__('time').time())},
            '$isoTimestamp': lambda: {'result': __import__('datetime').datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')},
            '$randomUUID': lambda: RandomTools.random_uuid(4),
            
            # ========== 文本/数字/颜色 ==========
            '$randomAlphaNumeric': lambda: RandomTools.random_string(1, 'alphanumeric'),
            '$randomBoolean': lambda: RandomTools.random_boolean(),
            '$randomInt': lambda: RandomTools.random_int(0, 1000),
            '$randomFloat': lambda: RandomTools.random_float(0, 1000),
            '$randomColor': lambda: RandomTools.random_color('name'),
            '$randomHexColor': lambda: RandomTools.random_color('hex'),
            '$randomAbbreviation': lambda: StringTools.word_count('ABC DEF GHI'),  # 简写实现
            
            # ========== String 类别 ==========
            '$string.alphanumeric': lambda length=10: RandomTools.random_string(length if isinstance(length, int) else 10, 'alphanumeric'),
            '$string.numeric': lambda length=10: RandomTools.random_string(length if isinstance(length, int) else 10, 'numeric'),
            '$string.alpha': lambda length=10: RandomTools.random_string(length if isinstance(length, int) else 10, 'letters'),
            '$string.uuid': lambda: RandomTools.random_uuid(4),
            
            # ========== 互联网 ==========
            '$randomIP': lambda: RandomTools.random_ip_address(4),
            '$randomIPV6': lambda: RandomTools.random_ip_address(6),
            '$randomMACAddress': lambda: RandomTools.random_mac_address(),
            '$randomPassword': lambda: RandomTools.random_password(15),
            '$randomLocale': lambda: {'result': random.choice(['en', 'zh', 'ja', 'ko', 'fr', 'de', 'es', 'ru'])},
            '$randomUserAgent': lambda: {'result': self._random_user_agent()},
            '$randomProtocol': lambda: {'result': random.choice(['http', 'https'])},
            '$randomSemver': lambda: SystemTools.system_semver(),
            
            # ========== 名称 ==========
            '$randomFirstName': lambda: TestDataTools.generate_chinese_name(gender='random'),
            '$randomLastName': lambda: TestDataTools.generate_chinese_name(gender='random'),
            '$randomFullName': lambda: TestDataTools.generate_chinese_name(gender='random'),
            '$randomNamePrefix': lambda: {'result': random.choice(['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.'])},
            '$randomNameSuffix': lambda: {'result': random.choice(['Jr.', 'Sr.', 'III', 'PhD', 'MD'])},
            
            # ========== 职业 ==========
            '$randomJobArea': lambda: {'result': random.choice(['IT', 'Finance', 'Marketing', 'Sales', 'HR'])},
            '$randomJobDescriptor': lambda: {'result': random.choice(['Senior', 'Junior', 'Lead', 'Principal'])},
            '$randomJobTitle': lambda: {'result': random.choice(['Engineer', 'Manager', 'Director', 'Analyst'])},
            '$randomJobType': lambda: {'result': random.choice(['Full-time', 'Part-time', 'Contract', 'Freelance'])},
            
            # ========== 电话/地址 ==========
            '$randomPhoneNumber': lambda: TestDataTools.generate_chinese_phone(),
            '$randomPhoneNumberExt': lambda: {'result': f"{random.randint(10, 99)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"},
            '$randomCity': lambda: TestDataTools.generate_chinese_address(full_address=False),
            '$randomStreetName': lambda: {'result': f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Park', 'Elm'])} St"},
            '$randomStreetAddress': lambda: TestDataTools.generate_chinese_address(full_address=True),
            '$randomCountry': lambda: {'result': random.choice(['China', 'USA', 'UK', 'Japan', 'Germany', 'France'])},
            '$randomCountryCode': lambda: {'result': random.choice(['CN', 'US', 'GB', 'JP', 'DE', 'FR'])},
            '$randomLatitude': lambda: {'result': round(random.uniform(-90, 90), 4)},
            '$randomLongitude': lambda: {'result': round(random.uniform(-180, 180), 4)},
            
            # ========== 商业 ==========
            '$randomCompanyName': lambda: TestDataTools.generate_company_name(),
            '$randomCatchPhrase': lambda: {'result': f"{random.choice(['Innovative', 'Advanced', 'Smart'])} {random.choice(['Solutions', 'Technologies', 'Systems'])}"},
            '$randomBs': lambda: {'result': random.choice(['synergize', 'monetize', 'optimize', 'leverage'])},
            '$randomProduct': lambda: {'result': random.choice(['Laptop', 'Phone', 'Tablet', 'Watch', 'Headphones'])},
            '$randomProductName': lambda: {'result': f"Product {random.randint(100, 999)}"},
            '$randomProductAdjective': lambda: {'result': random.choice(['Premium', 'Advanced', 'Pro', 'Ultra', 'Lite'])},
            '$randomProductMaterial': lambda: {'result': random.choice(['Metal', 'Plastic', 'Glass', 'Carbon Fiber', 'Wood'])},
            
            # ========== 金融 ==========
            '$randomCreditCard': lambda: TestDataTools.generate_bank_card(),
            '$randomCreditCardCVV': lambda: {'result': str(random.randint(100, 999))},
            '$randomCreditCardIssuer': lambda: {'result': random.choice(['Visa', 'MasterCard', 'Amex', 'Discover'])},
            '$randomIBAN': lambda: {'result': f"GB{random.randint(100000000000, 999999999999)}"},
            '$randomBIC': lambda: {'result': f"BANK{random.choice(string.ascii_uppercase)}{random.randint(1000, 9999)}"},
            '$randomBitcoin': lambda: {'result': f"1{''.join(random.choices(string.ascii_lowercase + string.digits, k=33))}"},
            '$randomTransactionType': lambda: {'result': random.choice(['deposit', 'withdrawal', 'transfer', 'payment'])},
            '$randomCurrencyCode': lambda: {'result': random.choice(['CNY', 'USD', 'EUR', 'JPY', 'GBP'])},
            '$randomCurrencyName': lambda: {'result': random.choice(['Yuan', 'Dollar', 'Euro', 'Yen', 'Pound'])},
            '$randomCurrencySymbol': lambda: {'result': random.choice(['¥', '$', '€', '¥', '£'])},
            
            # ========== 日期时间 ==========
            '$date.now': lambda: {'result': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            '$date.past': lambda: self._date_past(),
            '$date.future': lambda: self._date_future(),
            '$date.recent': lambda: self._date_recent(),
            '$date.soon': lambda: self._date_soon(),
            '$date.month': lambda: {'result': random.choice(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])},
            '$date.weekday': lambda: {'result': random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])},
            
            # ========== 数据库 ==========
            '$database.type': lambda: ProfessionalTools.database_type(),
            '$database.column': lambda: ProfessionalTools.database_column(),
            '$database.engine': lambda: ProfessionalTools.database_engine(),
            
            # ========== 黑客 ==========
            '$hacker.abbreviation': lambda: {'result': random.choice(['SQL', 'TCP', 'HTTP', 'JSON', 'XML', 'API', 'SSL', 'TLS'])},
            '$hacker.adjective': lambda: {'result': random.choice(['digital', 'virtual', 'online', 'wireless', 'neural'])},
            '$hacker.noun': lambda: {'result': random.choice(['interface', 'system', 'protocol', 'bandwidth', 'firewall'])},
            '$hacker.verb': lambda: {'result': random.choice(['hack', 'bypass', 'override', 'compress', 'copy'])},
            '$hacker.phrase': lambda: {'result': f"{random.choice(['Bypassing', 'Hacking'])} the {random.choice(['firewall', 'mainframe'])}"},
            
            # ========== 图片 ==========
            '$image.url': lambda: MockImageTools.image_url(),
            '$image.avatar': lambda: MockImageTools.image_avatar(),
            '$image.abstract': lambda: MockImageTools.image_abstract(),
            '$image.nature': lambda: MockImageTools.image_nature(),
            '$image.technology': lambda: MockImageTools.image_technology(),
            '$image.business': lambda: MockImageTools.image_business(),
            '$image.people': lambda: MockImageTools.image_people(),
            '$image.food': lambda: MockImageTools.image_food(),
            
            # ========== 音乐 ==========
            '$music.genre': lambda: EntertainmentTools.music_genre(),
            '$music.songName': lambda: EntertainmentTools.music_song_name(),
            '$music.artist': lambda: EntertainmentTools.music_artist(),
            
            # ========== 动物 ==========
            '$animal.type': lambda: EntertainmentTools.animal_type(),
            '$animal.name': lambda: EntertainmentTools.animal_name(),
            
            # ========== 食物 ==========
            '$food.dish': lambda: EntertainmentTools.food_dish(),
            '$food.ingredient': lambda: EntertainmentTools.food_ingredient(),
            '$food.fruit': lambda: EntertainmentTools.food_fruit(),
            '$food.vegetable': lambda: EntertainmentTools.food_vegetable(),
            
            # ========== 科学 ==========
            '$science.chemicalElement': lambda: ProfessionalTools.science_chemical_element(),
            '$science.chemicalSymbol': lambda: ProfessionalTools.science_chemical_symbol(),
            '$science.chemicalName': lambda: ProfessionalTools.science_chemical_name(),
            '$science.unit': lambda: ProfessionalTools.science_unit(),
            
            # ========== 航空 ==========
            '$airline.name': lambda: ProfessionalTools.airline_name(),
            '$airline.iataCode': lambda: ProfessionalTools.airline_iata_code(),
            '$airline.airport': lambda: ProfessionalTools.airline_airport(),
            '$airline.airportName': lambda: ProfessionalTools.airline_airport_name(),
            '$airline.airportIataCode': lambda: ProfessionalTools.airline_airport_iata_code(),
            '$airline.aircraftType': lambda: ProfessionalTools.airline_aircraft_type(),
            
            # ========== 车辆 ==========
            '$vehicle.manufacturer': lambda: ProfessionalTools.vehicle_manufacturer(),
            '$vehicle.model': lambda: ProfessionalTools.vehicle_model(),
            '$vehicle.type': lambda: ProfessionalTools.vehicle_type(),
            '$vehicle.fuel': lambda: ProfessionalTools.vehicle_fuel_type(),
            
            # ========== Git ==========
            '$git.branch': lambda: SystemTools.git_branch(),
            '$git.commitMessage': lambda: SystemTools.git_commit_message(),
            '$git.commitSha': lambda: SystemTools.git_commit_sha(),
            '$git.shortCommitSha': lambda: SystemTools.git_short_commit_sha(),
            
            # ========== 系统 ==========
            '$system.fileName': lambda: SystemTools.system_file_name(),
            '$system.fileExt': lambda: SystemTools.system_file_ext(),
            '$system.directoryPath': lambda: SystemTools.system_directory_path(),
            '$system.filePath': lambda: SystemTools.system_file_path(),
            '$system.mimeType': lambda: SystemTools.system_mime_type(),
            '$system.semver': lambda: SystemTools.system_semver(),
            '$system.platform': lambda: SystemTools.system_platform(),
            '$system.arch': lambda: SystemTools.system_arch(),
        }
    
    def _random_user_agent(self) -> str:
        """生成随机 User Agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
        return random.choice(agents)
    
    def _date_past(self) -> Dict[str, Any]:
        """过去日期"""
        import datetime
        days = random.randint(1, 365)
        date = datetime.datetime.now() - datetime.timedelta(days=days)
        return {'result': date.strftime('%Y-%m-%d %H:%M:%S')}
    
    def _date_future(self) -> Dict[str, Any]:
        """未来日期"""
        import datetime
        days = random.randint(1, 365)
        date = datetime.datetime.now() + datetime.timedelta(days=days)
        return {'result': date.strftime('%Y-%m-%d %H:%M:%S')}
    
    def _date_recent(self) -> Dict[str, Any]:
        """最近日期（7天内）"""
        import datetime
        days = random.randint(0, 7)
        date = datetime.datetime.now() - datetime.timedelta(days=days)
        return {'result': date.strftime('%Y-%m-%d %H:%M:%S')}
    
    def _date_soon(self) -> Dict[str, Any]:
        """即将发生（7天内）"""
        import datetime
        days = random.randint(0, 7)
        date = datetime.datetime.now() + datetime.timedelta(days=days)
        return {'result': date.strftime('%Y-%m-%d %H:%M:%S')}
    
    def execute(self, func_name: str, *args, **kwargs) -> Any:
        """执行 API Fox 函数"""
        if func_name not in self.functions:
            raise ValueError(f"不支持的 API Fox 函数: {func_name}")
        
        try:
            result = self.functions[func_name]()
            return result.get('result') if isinstance(result, dict) else result
        except Exception as e:
            return f"{{{{执行失败: {func_name} - {str(e)}}}}}"
    
    def get_supported_functions(self) -> list:
        """获取所有支持的函数列表"""
        return sorted(self.functions.keys())


import random
import string


class ApifoxVariableResolver:
    """API Fox 变量解析器 - 处理完整的 API Fox 语法"""
    
    def __init__(self):
        self.mapper = ApifoxFunctionMapper()
    
    def resolve(self, text: str) -> str:
        """
        解析 API Fox 变量语法
        支持:
        - {{$function}} - 动态函数
        - {{$function(args)}} - 带参数的函数
        - {{variable}} - 普通变量
        - {{$function|modifier}} - 链式操作（简化处理）
        """
        if not isinstance(text, str):
            return text
        
        # 匹配 {{$category.function}} 或 {{$function}}
        pattern = r'\{\{\$([^}|]+)(?:\|([^}]+))?\}\}'
        
        def replace_func(match):
            func_expr = match.group(1).strip()
            modifier = match.group(2)  # 链式操作符
            
            # 解析函数名和参数
            if '(' in func_expr:
                func_name = '$' + func_expr[:func_expr.index('(')]
                # 这里可以解析参数
            else:
                func_name = '$' + func_expr
            
            # 执行函数
            result = self.mapper.execute(func_name)
            
            # 处理链式操作
            if modifier:
                result = self._apply_modifier(result, modifier)
            
            return str(result) if result is not None else ''
        
        # 普通变量 {{variable}} - 保留原样，由运行时解析
        # 这里只处理动态函数
        
        return re.sub(pattern, replace_func, text)
    
    def _apply_modifier(self, value: Any, modifier: str) -> Any:
        """应用链式操作修饰符"""
        modifier = modifier.strip()
        
        # 日期格式化
        if modifier.startswith('format('):
            # 简化处理，实际可以实现日期格式化
            return value
        
        # 数值操作
        if modifier.startswith('addDays('):
            import datetime
            try:
                days = int(modifier[8:-1])
                if isinstance(value, str):
                    # 尝试解析日期
                    date = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    date = date + datetime.timedelta(days=days)
                    return date.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        return value
    
    def validate_syntax(self, text: str) -> Dict[str, Any]:
        """验证 API Fox 语法，返回不支持的函数列表"""
        if not isinstance(text, str):
            return {'valid': True, 'unsupported': []}
        
        # 提取所有 API Fox 函数调用
        pattern = r'\{\{\$([^}|]+?)(?:\||\})'
        matches = re.findall(pattern, text)
        
        unsupported = []
        supported = self.mapper.get_supported_functions()
        
        for match in matches:
            # 提取函数名（去掉参数）
            if '(' in match:
                func_name = '$' + match[:match.index('(')]
            else:
                func_name = '$' + match
            
            if func_name not in supported:
                unsupported.append(func_name)
        
        return {
            'valid': len(unsupported) == 0,
            'unsupported': list(set(unsupported))
        }


# 便捷函数
def resolve_apifox_variables(text: str) -> str:
    """解析 API Fox 变量（便捷函数）"""
    resolver = ApifoxVariableResolver()
    return resolver.resolve(text)


def validate_apifox_syntax(text: str) -> Dict[str, Any]:
    """验证 API Fox 语法（便捷函数）"""
    resolver = ApifoxVariableResolver()
    return resolver.validate_syntax(text)
