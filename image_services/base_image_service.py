from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import time

class BaseImageService(ABC):
    """圖片搜尋服務基礎類別"""
    
    def __init__(self, api_key: str = None, **kwargs):
        self.api_key = api_key
        self.platform_name = self.get_platform_name()
        
    @abstractmethod
    def get_platform_name(self) -> str:
        """回傳平台名稱"""
        pass
    
    @abstractmethod
    def search_images(self, 
                     query: str, 
                     page: int = 1, 
                     per_page: int = 12,
                     **kwargs) -> Dict:
        """
        搜尋圖片的抽象方法
        
        Args:
            query: 搜尋關鍵字
            page: 頁碼
            per_page: 每頁數量
            **kwargs: 其他平台特定參數
            
        Returns:
            標準格式的搜尋結果
        """
        pass
    
    @abstractmethod
    def download_image(self, image_url: str, filename: str = None) -> Dict:
        """下載圖片的抽象方法"""
        pass
    
    def get_standard_result_format(self) -> Dict:
        """回傳標準結果格式範例"""
        return {
            'success': True,
            'platform': self.platform_name,
            'query': '',
            'total': 0,
            'total_pages': 0,
            'current_page': 1,
            'per_page': 12,
            'results': [],
            'message': ''
        }
    
    def get_standard_image_format(self) -> Dict:
        """回傳標準圖片格式範例"""
        return {
            'id': '',
            'platform': self.platform_name,
            'description': '',
            'width': 0,
            'height': 0,
            'aspect_ratio': 1.0,
            'urls': {
                'original': '',
                'large': '',
                'medium': '',
                'small': '',
                'thumb': ''
            },
            'download_url': '',
            'color': '#000000',
            'likes': 0,
            'views': 0,
            'author': {
                'name': '',
                'username': '',
                'profile_url': '',
                'profile_image': ''
            },
            'tags': [],
            'created_at': '',
            'source_url': ''
        }
    
    def create_mock_results(self, query: str, per_page: int) -> Dict:
        """創建模擬搜尋結果"""
        mock_photos = []
        
        for i in range(min(per_page, 8)):
            mock_photos.append({
                'id': f'{self.platform_name.lower()}_mock_{i}_{int(time.time())}',
                'platform': self.platform_name,
                'description': f'來自 {self.platform_name} 關於 "{query}" 的模擬圖片 {i+1}',
                'width': 1920,
                'height': 1080,
                'aspect_ratio': 1.78,
                'urls': {
                    'original': f'https://picsum.photos/1920/1080?random={i+100}',
                    'large': f'https://picsum.photos/1920/1080?random={i+100}',
                    'medium': f'https://picsum.photos/1080/720?random={i+100}',
                    'small': f'https://picsum.photos/640/480?random={i+100}',
                    'thumb': f'https://picsum.photos/200/200?random={i+100}'
                },
                'download_url': f'https://picsum.photos/1920/1080?random={i+100}',
                'color': '#667788',
                'likes': 50 + i * 10,
                'views': 1000 + i * 100,
                'author': {
                    'name': f'{self.platform_name} 示例攝影師',
                    'username': f'{self.platform_name.lower()}_photographer_{i}',
                    'profile_url': f'https://example.com/{self.platform_name.lower()}/photographer_{i}',
                    'profile_image': f'https://picsum.photos/32/32?random={i+50}'
                },
                'tags': [query, '示例', '測試', self.platform_name],
                'created_at': '2024-01-01T00:00:00Z',
                'source_url': f'https://example.com/{self.platform_name.lower()}/photo/{i}'
            })
        
        result = self.get_standard_result_format()
        result.update({
            'query': query,
            'total': 100,
            'total_pages': 10,
            'current_page': 1,
            'per_page': per_page,
            'results': mock_photos,
            'message': f'模擬模式：從 {self.platform_name} 找到相關圖片（搜尋關鍵字: {query}）'
        })
        
        return result 