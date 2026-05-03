# -*- coding: utf-8 -*-
"""
娱乐数据生成工具 - 支持 API Fox 娱乐类动态变量
音乐、动物、食物等
"""
import random
from typing import Dict, Any, List


class EntertainmentTools:
    """娱乐数据工具类 - 100% 兼容 API Fox"""

    # 音乐类型 - 中文
    MUSIC_GENRES_CN = [
        '摇滚', '流行', '嘻哈', '爵士', '蓝调', '乡村', '电子',
        '古典', '雷鬼', '金属', '民谣', '灵魂', '节奏布鲁斯', '朋克',
        '另类', '独立', '舞曲', '科技舞曲', '浩室', '迷幻舞曲',
        '回响贝斯', '氛围音乐', '放克', '迪斯科', '福音', '歌剧',
        '拉丁', '萨尔萨', '韩语流行', '日语流行', '华语流行', '世界音乐'
    ]

    # 中文歌曲名
    MUSIC_SONG_NAMES_CN = [
        '月亮代表我的心', '甜蜜蜜', '吻别', '海阔天空', '朋友',
        '千千阙歌', '红日', '忘情水', '真的爱你', '青花瓷',
        '十年', '平凡之路', '演员', '小幸运', '告白气球',
        '成都', '体面', '说散就散', '年少有为', '光年之外'
    ]

    # 中文歌手/艺术家
    MUSIC_ARTISTS_CN = [
        '周杰伦', '邓紫棋', '薛之谦', '李荣浩', '林俊杰',
        '陈奕迅', '张学友', '刘德华', '王力宏', '李宇春',
        '张靓颖', '周深', '毛不易', '华晨宇', '五月天',
        'SHE', '凤凰传奇', 'TFBOYS', '王一博', '肖战'
    ]

    # 动物类型 - 中文
    ANIMAL_TYPES_CN = [
        '狗', '猫', '鸟', '鱼', '马', '牛', '猪', '羊',
        '山羊', '鸡', '鸭', '兔子', '老鼠', '蛇',
        '蜥蜴', '青蛙', '乌龟', '大象', '狮子', '老虎',
        '熊', '狼', '狐狸', '鹿', '猴子', '熊猫', '考拉',
        '袋鼠', '长颈鹿', '斑马', '河马', '犀牛'
    ]

    # 宠物名字 - 中文
    ANIMAL_NAMES_CN = [
        '小白', '小黑', '大黄', '旺财', '来福',
        '咪咪', '球球', '豆豆', '团团', '圆圆',
        '可乐', '奶茶', '布丁', '蛋糕', '芒果',
        '奥利奥', '汤圆', '花花', '虎子', '龙龙'
    ]

    # 中文菜品
    FOOD_DISHES_CN = [
        '红烧肉', '宫保鸡丁', '麻婆豆腐', '糖醋排骨', '鱼香肉丝',
        '水煮鱼', '回锅肉', '番茄炒蛋', '青椒肉丝', '蒜蓉西兰花',
        '北京烤鸭', '小笼包', '火锅', '烧烤', '酸菜鱼',
        '饺子', '面条', '炒饭', '煎饼果子', '肉夹馍'
    ]

    # 食材 - 中文
    FOOD_INGREDIENTS_CN = [
        '西红柿', '洋葱', '大蒜', '鸡肉', '牛肉', '猪肉',
        '大米', '面条', '土豆', '胡萝卜', '甜椒',
        '蘑菇', '芝士', '鸡蛋', '牛奶', '黄油',
        '橄榄油', '酱油', '姜', '葱', '香菜'
    ]

    # 水果 - 中文
    FOOD_FRUITS_CN = [
        '苹果', '香蕉', '橙子', '葡萄', '草莓', '蓝莓',
        '芒果', '菠萝', '西瓜', '桃子', '梨', '樱桃',
        '柠檬', '青柠', '猕猴桃', '木瓜', '椰子', '牛油果'
    ]

    # 蔬菜 - 中文
    FOOD_VEGETABLES_CN = [
        '西兰花', '菠菜', '羽衣甘蓝', '生菜', '黄瓜', '西红柿',
        '胡萝卜', '土豆', '洋葱', '大蒜', '甜椒', '西葫芦',
        '茄子', '花椰菜', '卷心菜', '芹菜', '芦笋', '豆角'
    ]
    
    @staticmethod
    def music_genre(count: int = 1) -> Dict[str, Any]:
        """随机音乐类型"""
        genres = random.choices(EntertainmentTools.MUSIC_GENRES_CN, k=count)
        return {'result': genres[0] if count == 1 else genres}

    @staticmethod
    def music_song_name(count: int = 1) -> Dict[str, Any]:
        """随机歌曲名"""
        songs = random.choices(EntertainmentTools.MUSIC_SONG_NAMES_CN, k=count)
        return {'result': songs[0] if count == 1 else songs}

    @staticmethod
    def music_artist(count: int = 1) -> Dict[str, Any]:
        """随机艺术家"""
        artists = random.choices(EntertainmentTools.MUSIC_ARTISTS_CN, k=count)
        return {'result': artists[0] if count == 1 else artists}

    @staticmethod
    def animal_type(count: int = 1) -> Dict[str, Any]:
        """随机动物类型"""
        animals = random.choices(EntertainmentTools.ANIMAL_TYPES_CN, k=count)
        return {'result': animals[0] if count == 1 else animals}

    @staticmethod
    def animal_name(count: int = 1) -> Dict[str, Any]:
        """随机动物名称"""
        names = random.choices(EntertainmentTools.ANIMAL_NAMES_CN, k=count)
        return {'result': names[0] if count == 1 else names}

    @staticmethod
    def food_dish(count: int = 1) -> Dict[str, Any]:
        """随机菜品"""
        dishes = random.choices(EntertainmentTools.FOOD_DISHES_CN, k=count)
        return {'result': dishes[0] if count == 1 else dishes}

    @staticmethod
    def food_ingredient(count: int = 1) -> Dict[str, Any]:
        """随机食材"""
        ingredients = random.choices(EntertainmentTools.FOOD_INGREDIENTS_CN, k=count)
        return {'result': ingredients[0] if count == 1 else ingredients}

    @staticmethod
    def food_fruit(count: int = 1) -> Dict[str, Any]:
        """随机水果"""
        fruits = random.choices(EntertainmentTools.FOOD_FRUITS_CN, k=count)
        return {'result': fruits[0] if count == 1 else fruits}

    @staticmethod
    def food_vegetable(count: int = 1) -> Dict[str, Any]:
        """随机蔬菜"""
        vegetables = random.choices(EntertainmentTools.FOOD_VEGETABLES_CN, k=count)
        return {'result': vegetables[0] if count == 1 else vegetables}
