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
    
    # 科学数据
    CHEMICAL_ELEMENTS = [
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
    
    SCIENCE_UNITS = [
        'meter', 'kilogram', 'second', 'ampere', 'kelvin',
        'mole', 'candela', 'newton', 'joule', 'watt',
        'pascal', 'hertz', 'volt', 'ohm', 'farad'
    ]
    
    # 航空数据
    AIRLINES = [
        {'name': 'American Airlines', 'iata': 'AA'},
        {'name': 'Delta Air Lines', 'iata': 'DL'},
        {'name': 'United Airlines', 'iata': 'UA'},
        {'name': 'Southwest Airlines', 'iata': 'WN'},
        {'name': 'Air China', 'iata': 'CA'},
        {'name': 'China Eastern', 'iata': 'MU'},
        {'name': 'China Southern', 'iata': 'CZ'},
        {'name': 'Emirates', 'iata': 'EK'},
        {'name': 'Qatar Airways', 'iata': 'QR'},
        {'name': 'Singapore Airlines', 'iata': 'SQ'},
    ]
    
    AIRPORTS = [
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
    
    AIRCRAFT_TYPES = [
        'Boeing 737', 'Boeing 747', 'Boeing 777', 'Boeing 787',
        'Airbus A320', 'Airbus A330', 'Airbus A350', 'Airbus A380',
        'Comac C919', 'Embraer E190', 'Bombardier CRJ900'
    ]
    
    # 车辆数据
    VEHICLE_MANUFACTURERS = [
        'Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz',
        'Audi', 'Volkswagen', 'Porsche', 'Tesla', 'Nissan', 'Hyundai',
        'Kia', 'Volvo', 'Jaguar', 'Land Rover', 'Lexus', 'Subaru',
        'Mazda', 'Mitsubishi', 'Buick', 'Cadillac', 'Lincoln', 'Jeep'
    ]
    
    VEHICLE_MODELS = [
        'Corolla', 'Civic', 'F-150', 'Silverado', '3 Series', 'C-Class',
        'A4', 'Golf', '911', 'Model S', 'Altima', 'Elantra',
        'Sportage', 'XC90', 'F-Type', 'Range Rover', 'RX', 'Outback',
        'CX-5', 'Outlander', 'Enclave', 'Escalade', 'Navigator', 'Wrangler'
    ]
    
    VEHICLE_TYPES = [
        'Sedan', 'SUV', 'Truck', 'Coupe', 'Convertible', 'Wagon',
        'Van', 'Minivan', 'Hatchback', 'Sports Car', 'Electric',
        'Hybrid', 'Diesel', 'Luxury', 'Compact', 'Mid-size', 'Full-size'
    ]
    
    FUEL_TYPES = ['Gasoline', 'Diesel', 'Electric', 'Hybrid', 'Plug-in Hybrid']
    
    # 数据库数据
    DATABASE_TYPES = [
        'MySQL', 'PostgreSQL', 'Oracle', 'SQL Server', 'MongoDB',
        'Redis', 'Elasticsearch', 'SQLite', 'MariaDB', 'Cassandra'
    ]
    
    DATABASE_COLUMNS = [
        'id', 'name', 'email', 'phone', 'address', 'status',
        'created_at', 'updated_at', 'deleted_at', 'user_id',
        'order_id', 'product_id', 'category_id', 'price', 'quantity'
    ]
    
    DATABASE_ENGINES = [
        'InnoDB', 'MyISAM', 'Memory', 'CSV', 'Archive', 'Blackhole'
    ]
    
    @staticmethod
    def science_chemical_element() -> Dict[str, Any]:
        """随机化学元素"""
        element = random.choice(ProfessionalTools.CHEMICAL_ELEMENTS)
        return {'result': element}
    
    @staticmethod
    def science_chemical_symbol() -> Dict[str, Any]:
        """随机化学元素符号"""
        element = random.choice(ProfessionalTools.CHEMICAL_ELEMENTS)
        return {'result': element['symbol']}
    
    @staticmethod
    def science_chemical_name() -> Dict[str, Any]:
        """随机化学元素名称"""
        element = random.choice(ProfessionalTools.CHEMICAL_ELEMENTS)
        return {'result': element['name']}
    
    @staticmethod
    def science_unit() -> Dict[str, Any]:
        """随机科学单位"""
        return {'result': random.choice(ProfessionalTools.SCIENCE_UNITS)}
    
    @staticmethod
    def airline_name() -> Dict[str, Any]:
        """随机航空公司名称"""
        return {'result': random.choice(ProfessionalTools.AIRLINES)['name']}
    
    @staticmethod
    def airline_iata_code() -> Dict[str, Any]:
        """随机航空公司 IATA 代码"""
        return {'result': random.choice(ProfessionalTools.AIRLINES)['iata']}
    
    @staticmethod
    def airline_airport() -> Dict[str, Any]:
        """随机机场信息"""
        return {'result': random.choice(ProfessionalTools.AIRPORTS)}
    
    @staticmethod
    def airline_airport_name() -> Dict[str, Any]:
        """随机机场名称"""
        return {'result': random.choice(ProfessionalTools.AIRPORTS)['name']}
    
    @staticmethod
    def airline_airport_iata_code() -> Dict[str, Any]:
        """随机机场 IATA 代码"""
        return {'result': random.choice(ProfessionalTools.AIRPORTS)['iata']}
    
    @staticmethod
    def airline_aircraft_type() -> Dict[str, Any]:
        """随机机型"""
        return {'result': random.choice(ProfessionalTools.AIRCRAFT_TYPES)}
    
    @staticmethod
    def vehicle_manufacturer() -> Dict[str, Any]:
        """随机车辆制造商"""
        return {'result': random.choice(ProfessionalTools.VEHICLE_MANUFACTURERS)}
    
    @staticmethod
    def vehicle_model() -> Dict[str, Any]:
        """随机车辆型号"""
        return {'result': random.choice(ProfessionalTools.VEHICLE_MODELS)}
    
    @staticmethod
    def vehicle_type() -> Dict[str, Any]:
        """随机车辆类型"""
        return {'result': random.choice(ProfessionalTools.VEHICLE_TYPES)}
    
    @staticmethod
    def vehicle_fuel_type() -> Dict[str, Any]:
        """随机燃料类型"""
        return {'result': random.choice(ProfessionalTools.FUEL_TYPES)}
    
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
