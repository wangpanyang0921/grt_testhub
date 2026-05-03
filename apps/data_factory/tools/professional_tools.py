# -*- coding: utf-8 -*-
"""
专业数据生成工具 - 支持 API Fox 专业类动态变量
科学、航空、车辆、数据库等
"""
import random
import string
from typing import Dict, Any, List


class ProfessionalTools:
    """专业数据工具类 - 100% 兼容 API Fox"""
    
    # 科学数据 - 英文
    CHEMICAL_ELEMENTS_EN = [
        {'symbol': 'H', 'name': 'Hydrogen', 'number': 1},
        {'symbol': 'He', 'name': 'Helium', 'number': 2},
        {'symbol': 'Li', 'name': 'Lithium', 'number': 3},
        {'symbol': 'C', 'name': 'Carbon', 'number': 6},
        {'symbol': 'N', 'name': 'Nitrogen', 'number': 7},
        {'symbol': 'O', 'name': 'Oxygen', 'number': 8},
        {'symbol': 'Na', 'name': 'Sodium', 'number': 11},
        {'symbol': 'Mg', 'name': 'Magnesium', 'number': 12},
        {'symbol': 'Al', 'name': 'Aluminium', 'number': 13},
        {'symbol': 'Si', 'name': 'Silicon', 'number': 14},
        {'symbol': 'Fe', 'name': 'Iron', 'number': 26},
        {'symbol': 'Cu', 'name': 'Copper', 'number': 29},
        {'symbol': 'Ag', 'name': 'Silver', 'number': 47},
        {'symbol': 'Au', 'name': 'Gold', 'number': 79},
    ]
    
    # 科学数据 - 中文
    CHEMICAL_ELEMENTS_CN = [
        {'symbol': 'H', 'name': '氢', 'number': 1},
        {'symbol': 'He', 'name': '氦', 'number': 2},
        {'symbol': 'Li', 'name': '锂', 'number': 3},
        {'symbol': 'C', 'name': '碳', 'number': 6},
        {'symbol': 'N', 'name': '氮', 'number': 7},
        {'symbol': 'O', 'name': '氧', 'number': 8},
        {'symbol': 'Na', 'name': '钠', 'number': 11},
        {'symbol': 'Mg', 'name': '镁', 'number': 12},
        {'symbol': 'Al', 'name': '铝', 'number': 13},
        {'symbol': 'Si', 'name': '硅', 'number': 14},
        {'symbol': 'Fe', 'name': '铁', 'number': 26},
        {'symbol': 'Cu', 'name': '铜', 'number': 29},
        {'symbol': 'Ag', 'name': '银', 'number': 47},
        {'symbol': 'Au', 'name': '金', 'number': 79},
    ]
    
    SCIENCE_UNITS_EN = [
        'meter', 'kilogram', 'second', 'ampere', 'kelvin',
        'mole', 'candela', 'newton', 'joule', 'watt',
        'pascal', 'hertz', 'volt', 'ohm', 'farad'
    ]
    
    SCIENCE_UNITS_CN = [
        '米', '千克', '秒', '安培', '开尔文',
        '摩尔', '坎德拉', '牛顿', '焦耳', '瓦特',
        '帕斯卡', '赫兹', '伏特', '欧姆', '法拉'
    ]
    
    # 航空数据 - 英文
    AIRLINES_EN = [
        {'name': 'American Airlines', 'iata': 'AA'},
        {'name': 'Delta Air Lines', 'iata': 'DL'},
        {'name': 'United Airlines', 'iata': 'UA'},
        {'name': 'Southwest Airlines', 'iata': 'WN'},
        {'name': 'Emirates', 'iata': 'EK'},
        {'name': 'Qatar Airways', 'iata': 'QR'},
        {'name': 'Singapore Airlines', 'iata': 'SQ'},
    ]
    
    # 航空数据 - 中文
    AIRLINES_CN = [
        {'name': '中国国际航空', 'iata': 'CA'},
        {'name': '中国东方航空', 'iata': 'MU'},
        {'name': '中国南方航空', 'iata': 'CZ'},
        {'name': '海南航空', 'iata': 'HU'},
        {'name': '厦门航空', 'iata': 'MF'},
        {'name': '深圳航空', 'iata': 'ZH'},
        {'name': '四川航空', 'iata': '3U'},
        {'name': '山东航空', 'iata': 'SC'},
        {'name': '春秋航空', 'iata': '9C'},
        {'name': '吉祥航空', 'iata': 'HO'},
    ]
    
    AIRPORTS_EN = [
        {'name': 'Beijing Capital', 'iata': 'PEK', 'city': 'Beijing'},
        {'name': 'Shanghai Pudong', 'iata': 'PVG', 'city': 'Shanghai'},
        {'name': 'Guangzhou Baiyun', 'iata': 'CAN', 'city': 'Guangzhou'},
        {'name': 'Los Angeles', 'iata': 'LAX', 'city': 'Los Angeles'},
        {'name': 'John F. Kennedy', 'iata': 'JFK', 'city': 'New York'},
        {'name': 'Heathrow', 'iata': 'LHR', 'city': 'London'},
        {'name': 'Charles de Gaulle', 'iata': 'CDG', 'city': 'Paris'},
        {'name': 'Dubai', 'iata': 'DXB', 'city': 'Dubai'},
        {'name': 'Tokyo Haneda', 'iata': 'HND', 'city': 'Tokyo'},
        {'name': 'Singapore Changi', 'iata': 'SIN', 'city': 'Singapore'},
    ]
    
    AIRPORTS_CN = [
        {'name': '北京首都国际机场', 'iata': 'PEK', 'city': '北京'},
        {'name': '上海浦东国际机场', 'iata': 'PVG', 'city': '上海'},
        {'name': '广州白云国际机场', 'iata': 'CAN', 'city': '广州'},
        {'name': '深圳宝安国际机场', 'iata': 'SZX', 'city': '深圳'},
        {'name': '成都天府国际机场', 'iata': 'TFU', 'city': '成都'},
        {'name': '杭州萧山国际机场', 'iata': 'HGH', 'city': '杭州'},
        {'name': '西安咸阳国际机场', 'iata': 'XIY', 'city': '西安'},
        {'name': '重庆江北国际机场', 'iata': 'CKG', 'city': '重庆'},
        {'name': '昆明长水国际机场', 'iata': 'KMG', 'city': '昆明'},
        {'name': '南京禄口国际机场', 'iata': 'NKG', 'city': '南京'},
    ]
    
    AIRCRAFT_TYPES_CN = [
        '波音737', '波音747', '波音777', '波音787',
        '空客A320', '空客A330', '空客A350', '空客A380',
        '中国商飞C919', '巴西航空E190', '庞巴迪CRJ900'
    ]
    
    # 车辆数据 - 英文
    VEHICLE_MANUFACTURERS_EN = [
        'Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz',
        'Audi', 'Volkswagen', 'Porsche', 'Tesla', 'Nissan', 'Hyundai',
        'Kia', 'Volvo', 'Jaguar', 'Land Rover', 'Lexus', 'Subaru',
        'Mazda', 'Mitsubishi', 'Buick', 'Cadillac', 'Lincoln', 'Jeep'
    ]
    
    # 车辆数据 - 中文
    VEHICLE_MANUFACTURERS_CN = [
        '丰田', '本田', '福特', '雪佛兰', '宝马', '奔驰',
        '奥迪', '大众', '保时捷', '特斯拉', '日产', '现代',
        '起亚', '沃尔沃', '捷豹', '路虎', '雷克萨斯', '斯巴鲁',
        '马自达', '三菱', '别克', '凯迪拉克', '林肯', '吉普',
        '比亚迪', '蔚来', '小鹏', '理想', '长城', '吉利',
        '奇瑞', '长安', '五菱', '红旗', '荣威', '名爵'
    ]
    
    VEHICLE_MODELS_CN = [
        '卡罗拉', '思域', '凯美瑞', '雅阁', '帕萨特', '迈腾',
        '宝马3系', '奔驰C级', '奥迪A4L', '特斯拉Model 3', 'Model Y',
        '轩逸', '朗逸', '哈弗H6', '长安CS75', '比亚迪汉', '比亚迪唐',
        '蔚来ES6', '蔚来ET7', '小鹏P7', '理想ONE', '理想L9',
        '五菱宏光', '坦克300', '奔驰E级', '宝马5系', '奥迪A6L'
    ]
    
    VEHICLE_TYPES_CN = [
        '轿车', 'SUV', '跑车', '卡车', '面包车', 'MPV',
        '敞篷车', '旅行车', '掀背车', '硬顶跑车', '电动车',
        '混合动力车', '柴油车', '豪华车', '紧凑型车', '中型车', '大型车'
    ]
    
    FUEL_TYPES_CN = ['汽油', '柴油', '纯电动', '混合动力', '插电混动']
    
    # 数据库引擎
    DATABASE_ENGINES = [
        'InnoDB', 'MyISAM', 'Memory', 'CSV', 'Archive', 'Blackhole'
    ]

    @staticmethod
    def science_chemical_element() -> Dict[str, Any]:
        """随机化学元素"""
        element = random.choice(ProfessionalTools.CHEMICAL_ELEMENTS_CN)
        return {'result': element}

    @staticmethod
    def science_chemical_symbol() -> Dict[str, Any]:
        """随机化学元素符号"""
        element = random.choice(ProfessionalTools.CHEMICAL_ELEMENTS_CN)
        return {'result': element['symbol']}

    @staticmethod
    def science_chemical_name() -> Dict[str, Any]:
        """随机化学元素名称"""
        element = random.choice(ProfessionalTools.CHEMICAL_ELEMENTS_CN)
        return {'result': element['name']}

    @staticmethod
    def science_unit() -> Dict[str, Any]:
        """随机科学单位"""
        return {'result': random.choice(ProfessionalTools.SCIENCE_UNITS_CN)}

    @staticmethod
    def airline_name() -> Dict[str, Any]:
        """随机航空公司名称"""
        return {'result': random.choice(ProfessionalTools.AIRLINES_CN)['name']}

    @staticmethod
    def airline_iata_code() -> Dict[str, Any]:
        """随机航空公司 IATA 代码"""
        return {'result': random.choice(ProfessionalTools.AIRLINES_CN)['iata']}

    @staticmethod
    def airline_airport() -> Dict[str, Any]:
        """随机机场信息"""
        return {'result': random.choice(ProfessionalTools.AIRPORTS_CN)}

    @staticmethod
    def airline_airport_name() -> Dict[str, Any]:
        """随机机场名称"""
        return {'result': random.choice(ProfessionalTools.AIRPORTS_CN)['name']}

    @staticmethod
    def airline_airport_iata_code() -> Dict[str, Any]:
        """随机机场 IATA 代码"""
        return {'result': random.choice(ProfessionalTools.AIRPORTS_CN)['iata']}

    @staticmethod
    def airline_aircraft_type() -> Dict[str, Any]:
        """随机机型"""
        return {'result': random.choice(ProfessionalTools.AIRCRAFT_TYPES_CN)}

    @staticmethod
    def vehicle_manufacturer() -> Dict[str, Any]:
        """随机车辆制造商"""
        return {'result': random.choice(ProfessionalTools.VEHICLE_MANUFACTURERS_CN)}

    @staticmethod
    def vehicle_model() -> Dict[str, Any]:
        """随机车辆型号"""
        return {'result': random.choice(ProfessionalTools.VEHICLE_MODELS_CN)}

    @staticmethod
    def vehicle_type() -> Dict[str, Any]:
        """随机车辆类型"""
        return {'result': random.choice(ProfessionalTools.VEHICLE_TYPES_CN)}

    @staticmethod
    def vehicle_fuel_type() -> Dict[str, Any]:
        """随机燃料类型"""
        return {'result': random.choice(ProfessionalTools.FUEL_TYPES_CN)}
    
    @staticmethod
    def database_type() -> Dict[str, Any]:
        """随机数据库类型"""
        return {'result': random.choice(ProfessionalTools.DATABASE_TYPES)}
    
    @staticmethod
    def database_column() -> Dict[str, Any]:
        """随机数据库列名"""
        return {'result': random.choice(ProfessionalTools.DATABASE_COLUMNS)}
    
    @staticmethod
    def database_engine() -> Dict[str, Any]:
        """随机数据库引擎"""
        return {'result': random.choice(ProfessionalTools.DATABASE_ENGINES)}
