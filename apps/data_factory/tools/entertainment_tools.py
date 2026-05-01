# -*- coding: utf-8 -*-
"""
娱乐数据生成工具 - 支持 API Fox 娱乐类动态变量
音乐、动物、食物等
"""
import random
from typing import Dict, Any, List


class EntertainmentTools:
    """娱乐数据工具类 - 100% 兼容 API Fox"""
    
    # 音乐数据
    MUSIC_GENRES = [
        'Rock', 'Pop', 'Hip Hop', 'Jazz', 'Blues', 'Country', 'Electronic',
        'Classical', 'Reggae', 'Metal', 'Folk', 'Soul', 'R&B', 'Punk',
        'Alternative', 'Indie', 'Dance', 'Techno', 'House', 'Trance',
        'Dubstep', 'Ambient', 'Funk', 'Disco', 'Gospel', 'Opera',
        'Latin', 'Salsa', 'K-Pop', 'J-Pop', 'C-Pop', 'World'
    ]
    
    MUSIC_SONG_NAMES = [
        'Bohemian Rhapsody', 'Stairway to Heaven', 'Hotel California',
        'Sweet Child O Mine', 'Imagine', 'Smells Like Teen Spirit',
        'Billie Jean', 'Like a Prayer', 'I Will Always Love You',
        'Hey Jude', 'Let It Be', 'Yesterday', 'Wonderwall',
        'Creep', 'Seven Nation Army', 'Rolling in the Deep',
        'Bad Romance', 'Uptown Funk', 'Shape of You', 'Blinding Lights'
    ]
    
    MUSIC_ARTISTS = [
        'The Beatles', 'Michael Jackson', 'Madonna', 'Elvis Presley',
        'Queen', 'Led Zeppelin', 'Pink Floyd', 'U2', 'Nirvana',
        'Eminem', 'Jay-Z', 'Beyoncé', 'Taylor Swift', 'Ed Sheeran',
        'Adele', 'Bruno Mars', 'Drake', 'Rihanna', 'Kanye West',
        'Coldplay', 'Maroon 5', 'Imagine Dragons', 'The Weeknd'
    ]
    
    # 动物数据
    ANIMAL_TYPES = [
        'dog', 'cat', 'bird', 'fish', 'horse', 'cow', 'pig', 'sheep',
        'goat', 'chicken', 'duck', 'rabbit', 'mouse', 'rat', 'snake',
        'lizard', 'frog', 'turtle', 'elephant', 'lion', 'tiger',
        'bear', 'wolf', 'fox', 'deer', 'monkey', 'panda', 'koala',
        'kangaroo', 'giraffe', 'zebra', 'hippopotamus', 'rhinoceros'
    ]
    
    ANIMAL_NAMES = [
        'Max', 'Bella', 'Charlie', 'Luna', 'Cooper', 'Lucy', 'Buddy',
        'Daisy', 'Rocky', 'Molly', 'Bear', 'Sadie', 'Duke', 'Maggie',
        'Tucker', 'Chloe', 'Jack', 'Sophie', 'Oliver', 'Bailey'
    ]
    
    # 食物数据
    FOOD_DISHES = [
        'Spaghetti Bolognese', 'Chicken Curry', 'Beef Tacos', 'Sushi Platter',
        'Pad Thai', 'Caesar Salad', 'Margherita Pizza', 'Fish and Chips',
        'Kung Pao Chicken', 'Beef Burger', 'Chicken Tikka Masala',
        'Pho', 'Ramen', 'Dim Sum', 'Burrito', 'Falafel Wrap',
        'Steak', 'Lobster', 'Crab Cakes', 'Spring Rolls'
    ]
    
    FOOD_INGREDIENTS = [
        'Tomato', 'Onion', 'Garlic', 'Chicken', 'Beef', 'Pork',
        'Rice', 'Pasta', 'Potato', 'Carrot', 'Bell Pepper',
        'Mushroom', 'Cheese', 'Eggs', 'Milk', 'Butter',
        'Olive Oil', 'Soy Sauce', 'Ginger', 'Basil'
    ]
    
    FOOD_FRUITS = [
        'Apple', 'Banana', 'Orange', 'Grape', 'Strawberry', 'Blueberry',
        'Mango', 'Pineapple', 'Watermelon', 'Peach', 'Pear', 'Cherry',
        'Lemon', 'Lime', 'Kiwi', 'Papaya', 'Coconut', 'Avocado'
    ]
    
    FOOD_VEGETABLES = [
        'Broccoli', 'Spinach', 'Kale', 'Lettuce', 'Cucumber', 'Tomato',
        'Carrot', 'Potato', 'Onion', 'Garlic', 'Pepper', 'Zucchini',
        'Eggplant', 'Cauliflower', 'Cabbage', 'Celery', 'Asparagus'
    ]
    
    @staticmethod
    def music_genre(count: int = 1) -> Dict[str, Any]:
        """随机音乐类型"""
        genres = random.choices(EntertainmentTools.MUSIC_GENRES, k=count)
        return {'result': genres[0] if count == 1 else genres}
    
    @staticmethod
    def music_song_name(count: int = 1) -> Dict[str, Any]:
        """随机歌曲名"""
        songs = random.choices(EntertainmentTools.MUSIC_SONG_NAMES, k=count)
        return {'result': songs[0] if count == 1 else songs}
    
    @staticmethod
    def music_artist(count: int = 1) -> Dict[str, Any]:
        """随机艺术家"""
        artists = random.choices(EntertainmentTools.MUSIC_ARTISTS, k=count)
        return {'result': artists[0] if count == 1 else artists}
    
    @staticmethod
    def animal_type(count: int = 1) -> Dict[str, Any]:
        """随机动物类型"""
        animals = random.choices(EntertainmentTools.ANIMAL_TYPES, k=count)
        return {'result': animals[0] if count == 1 else animals}
    
    @staticmethod
    def animal_name(count: int = 1) -> Dict[str, Any]:
        """随机动物名称"""
        names = random.choices(EntertainmentTools.ANIMAL_NAMES, k=count)
        return {'result': names[0] if count == 1 else names}
    
    @staticmethod
    def food_dish(count: int = 1) -> Dict[str, Any]:
        """随机菜品"""
        dishes = random.choices(EntertainmentTools.FOOD_DISHES, k=count)
        return {'result': dishes[0] if count == 1 else dishes}
    
    @staticmethod
    def food_ingredient(count: int = 1) -> Dict[str, Any]:
        """随机食材"""
        ingredients = random.choices(EntertainmentTools.FOOD_INGREDIENTS, k=count)
        return {'result': ingredients[0] if count == 1 else ingredients}
    
    @staticmethod
    def food_fruit(count: int = 1) -> Dict[str, Any]:
        """随机水果"""
        fruits = random.choices(EntertainmentTools.FOOD_FRUITS, k=count)
        return {'result': fruits[0] if count == 1 else fruits}
    
    @staticmethod
    def food_vegetable(count: int = 1) -> Dict[str, Any]:
        """随机蔬菜"""
        vegetables = random.choices(EntertainmentTools.FOOD_VEGETABLES, k=count)
        return {'result': vegetables[0] if count == 1 else vegetables}
