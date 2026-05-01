# -*- coding: utf-8 -*-
"""
Mock 图像数据生成工具 - 支持 API Fox 图像类动态变量
图片 URL、头像、占位图等
"""
import random
from typing import Dict, Any, List


class MockImageTools:
    """Mock 图像工具类 - 100% 兼容 API Fox"""
    
    # 图片服务域名
    IMAGE_SERVICES = {
        'picsum': 'https://picsum.photos',
        'placeholder': 'https://via.placeholder.com',
        'unsplash': 'https://source.unsplash.com',
    }
    
    # 常见的图片尺寸
    COMMON_SIZES = [
        (100, 100), (200, 200), (300, 300), (400, 400), (500, 500),
        (640, 480), (800, 600), (1024, 768), (1280, 720), (1920, 1080),
        (300, 250), (728, 90), (160, 600), (320, 50), (970, 250)
    ]
    
    # 头像服务
    AVATAR_SERVICES = [
        'https://api.dicebear.com/7.x/avataaars/svg',
        'https://api.dicebear.com/7.x/bottts/svg',
        'https://api.dicebear.com/7.x/initials/svg',
        'https://api.dicebear.com/7.x/lorelei/svg',
        'https://api.dicebear.com/7.x/notionists/svg',
    ]
    
    # 图片分类关键词（用于 Unsplash）
    IMAGE_CATEGORIES = [
        'nature', 'water', 'mountain', 'forest', 'sky', 'sunset',
        'technology', 'computer', 'phone', 'code', 'programming',
        'people', 'business', 'office', 'meeting', 'team',
        'architecture', 'building', 'city', 'interior', 'house',
        'food', 'drink', 'restaurant', 'cooking', 'fruit',
        'animal', 'dog', 'cat', 'bird', 'wildlife',
        'travel', 'car', 'transport', 'road', 'street',
        'fashion', 'clothing', 'accessory', 'shoe', 'watch'
    ]
    
    # 颜色列表
    COLORS = [
        'FF0000', '00FF00', '0000FF', 'FFFF00', 'FF00FF', '00FFFF',
        '000000', 'FFFFFF', '808080', 'C0C0C0', '800000', '808000',
        '008000', '800080', '008080', '000080'
    ]
    
    @staticmethod
    def image_url(width: int = 640, height: int = 480, 
                  category: str = None, random_id: bool = True) -> Dict[str, Any]:
        """
        生成随机图片 URL
        支持 picsum 和 unsplash 两种服务
        """
        service = random.choice(['picsum', 'unsplash'])
        
        if service == 'picsum':
            if random_id:
                url = f"https://picsum.photos/{width}/{height}?random={random.randint(1, 10000)}"
            else:
                url = f"https://picsum.photos/{width}/{height}"
        else:
            # Unsplash
            if category and category in MockImageTools.IMAGE_CATEGORIES:
                url = f"https://source.unsplash.com/{width}x{height}/?{category}"
            else:
                url = f"https://source.unsplash.com/{width}x{height}"
        
        return {'result': url}
    
    @staticmethod
    def image_avatar(seed: str = None, style: str = None) -> Dict[str, Any]:
        """
        生成随机头像 URL
        使用 DiceBear API
        """
        if seed is None:
            seed = random.randint(1, 10000)
        
        if style is None:
            style = random.choice(['avataaars', 'bottts', 'initials', 'lorelei', 'notionists'])
        
        url = f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}"
        return {'result': url}
    
    @staticmethod
    def image_placeholder(width: int = 300, height: int = 200, 
                          text: str = None, bg_color: str = None, 
                          text_color: str = None) -> Dict[str, Any]:
        """
        生成占位图 URL
        使用 via.placeholder.com 服务
        """
        size = f"{width}x{height}"
        
        if bg_color is None:
            bg_color = random.choice(MockImageTools.COLORS)
        if text_color is None:
            text_color = 'FFFFFF' if bg_color != 'FFFFFF' else '000000'
        
        url = f"https://via.placeholder.com/{size}/{bg_color}/{text_color}"
        
        if text:
            url += f"?text={text}"
        
        return {'result': url}
    
    @staticmethod
    def image_abstract(width: int = 640, height: int = 480) -> Dict[str, Any]:
        """生成抽象艺术图片 URL"""
        # 使用 picsum 的随机图片
        url = f"https://picsum.photos/seed/{random.randint(1, 10000)}/{width}/{height}"
        return {'result': url}
    
    @staticmethod
    def image_nature(width: int = 640, height: int = 480) -> Dict[str, Any]:
        """生成自然风景图片 URL"""
        url = f"https://source.unsplash.com/{width}x{height}/?nature"
        return {'result': url}
    
    @staticmethod
    def image_technology(width: int = 640, height: int = 480) -> Dict[str, Any]:
        """生成科技相关图片 URL"""
        url = f"https://source.unsplash.com/{width}x{height}/?technology"
        return {'result': url}
    
    @staticmethod
    def image_business(width: int = 640, height: int = 480) -> Dict[str, Any]:
        """生成商务相关图片 URL"""
        url = f"https://source.unsplash.com/{width}x{height}/?business"
        return {'result': url}
    
    @staticmethod
    def image_people(width: int = 640, height: int = 480) -> Dict[str, Any]:
        """生成人物相关图片 URL"""
        url = f"https://source.unsplash.com/{width}x{height}/?people"
        return {'result': url}
    
    @staticmethod
    def image_food(width: int = 640, height: int = 480) -> Dict[str, Any]:
        """生成美食相关图片 URL"""
        url = f"https://source.unsplash.com/{width}x{height}/?food"
        return {'result': url}
    
    @staticmethod
    def image_dimensions() -> Dict[str, Any]:
        """随机图片尺寸"""
        width, height = random.choice(MockImageTools.COMMON_SIZES)
        return {'result': {'width': width, 'height': height}}
    
    @staticmethod
    def image_category() -> Dict[str, Any]:
        """随机图片分类"""
        return {'result': random.choice(MockImageTools.IMAGE_CATEGORIES)}
    
    @staticmethod
    def image_data_uri(width: int = 100, height: int = 100, 
                       color: str = 'ccc') -> Dict[str, Any]:
        """
        生成 Base64 编码的占位图片 Data URI
        简单的 SVG 格式
        """
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
            <rect width="100%" height="100%" fill="#{color}"/>
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
                  font-family="sans-serif" font-size="14" fill="#666">
                {width}x{height}
            </text>
        </svg>'''
        
        import base64
        encoded = base64.b64encode(svg.encode()).decode()
        data_uri = f"data:image/svg+xml;base64,{encoded}"
        
        return {'result': data_uri}
