import os
import requests
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs
import uuid
from pathlib import Path

class GoogleImageSearchService:
    """Google 圖片搜尋服務"""
    
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
        self.base_url = 'https://www.googleapis.com/customsearch/v1'
        self.download_dir = Path('static/downloaded_images')
        self.download_dir.mkdir(exist_ok=True)
        
        # 如果沒有API金鑰，使用web scraping模式
        self.use_api = bool(self.api_key and self.search_engine_id)
        
        if self.use_api:
            print(f"✅ Google 圖片搜尋服務已初始化 (API模式)")
        else:
            print(f"✅ Google 圖片搜尋服務已初始化 (Web Scraping模式)")
    
    def search_images(self, 
                     query: str,
                     page: int = 1,
                     per_page: int = 12,
                     **kwargs) -> Dict:
        """
        搜尋Google圖片
        
        Args:
            query: 搜尋關鍵字
            page: 頁碼
            per_page: 每頁數量
        """
        if self.use_api:
            print(f"🔍 嘗試使用Google Search API搜尋: {query}")
            result = self._search_with_api(query, page, per_page, **kwargs)
            
            # 如果API失敗，自動回退到Web Scraping
            if not result.get('success'):
                print(f"⚠️ API搜尋失敗，回退到Web Scraping模式")
                print(f"❌ API錯誤: {result.get('error', '未知錯誤')}")
                return self._search_with_scraping(query, page, per_page, **kwargs)
            else:
                print(f"✅ API搜尋成功，找到 {len(result.get('images', []))} 張圖片")
                return result
        else:
            print(f"🔍 使用Web Scraping模式搜尋: {query}")
            return self._search_with_scraping(query, page, per_page, **kwargs)
    
    def _search_with_api(self, query: str, page: int, per_page: int, **kwargs) -> Dict:
        """使用Google Custom Search API搜尋"""
        try:
            # Google Custom Search API參數
            start_index = (page - 1) * per_page + 1
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'searchType': 'image',
                'start': start_index,
                'num': min(per_page, 10),  # API限制最多10個結果
                'safe': 'active',
                'imgSize': kwargs.get('size', 'medium'),
                'imgType': kwargs.get('type', 'photo'),
                'fileType': 'jpg,png,webp',
                'fields': 'items(title,link,snippet,image/thumbnailLink,image/width,image/height,image/contextLink,fileFormat,displayLink)'  # 只請求需要的欄位
            }
            
            # 添加圖片尺寸過濾
            if kwargs.get('orientation'):
                if kwargs['orientation'] == 'landscape':
                    params['imgSize'] = 'large'
                elif kwargs['orientation'] == 'portrait':
                    params['imgSize'] = 'medium'
            
            # 添加gzip支援的headers
            api_headers = {
                'Accept-Encoding': 'gzip',
                'User-Agent': 'ai-media-generator (gzip)'
            }
            
            response = requests.get(self.base_url, params=params, headers=api_headers, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            
            # 處理搜尋結果
            results = []
            items = data.get('items', [])
            
            for item in items:
                image_info = {
                    'id': item.get('title', '').replace(' ', '_') + f"_{int(time.time())}",
                    'url': item.get('link'),
                    'thumb_url': item.get('image', {}).get('thumbnailLink'),
                    'title': item.get('title', ''),
                    'description': item.get('snippet', ''),
                    'width': item.get('image', {}).get('width'),
                    'height': item.get('image', {}).get('height'),
                    'source_url': item.get('image', {}).get('contextLink'),
                    'file_type': item.get('fileFormat', '').upper(),
                    'platform': 'google',
                    'attribution': f"來源: {urlparse(item.get('displayLink', '')).netloc}",
                    'download_url': item.get('link')
                }
                results.append(image_info)
            
            return {
                'success': True,
                'query': query,
                'page': page,
                'per_page': per_page,
                'total_results': data.get('searchInformation', {}).get('totalResults', 0),
                'results': results,
                'images': results,  # 為前端兼容性添加
                'platform': 'google',
                'message': f'找到 {len(results)} 張圖片'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API請求失敗: {str(e)}',
                'message': '無法連接到Google搜尋API',
                'results': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'搜尋失敗: {str(e)}',
                'message': '搜尋過程中發生錯誤',
                'results': []
            }
    
    def _search_with_scraping(self, query: str, page: int, per_page: int, **kwargs) -> Dict:
        """使用Web Scraping搜尋（當沒有API金鑰時的備用方案）"""
        try:
            import re
            import json
            from urllib.parse import quote, unquote
            
            print(f"🔍 Web Scraping搜尋: {query}")
            
            # 構建Google圖片搜尋URL
            encoded_query = quote(query, safe='')
            start_index = (page - 1) * per_page
            
            # 構建搜尋參數
            tbs_params = []
            
            # 圖片尺寸參數
            size = kwargs.get('size', 'any')
            if size == 'large':
                tbs_params.append('isz:l')
            elif size == 'medium':
                tbs_params.append('isz:m')
            elif size == 'icon':
                tbs_params.append('isz:i')
            
            # 圖片方向參數
            orientation = kwargs.get('orientation', 'any')
            if orientation == 'landscape':
                tbs_params.append('iar:w')
            elif orientation == 'portrait':
                tbs_params.append('iar:t')
            
            # 圖片類型參數
            image_type = kwargs.get('type', 'any')
            if image_type == 'photo':
                tbs_params.append('itp:photo')
            elif image_type == 'clipart':
                tbs_params.append('itp:clipart')
            elif image_type == 'lineart':
                tbs_params.append('itp:lineart')
            elif image_type == 'face':
                tbs_params.append('itp:face')
            
            # 組合tbs參數
            tbs_param = ''
            if tbs_params:
                tbs_param = '&tbs=' + ','.join(tbs_params)
            
            # 添加語言參數以支援中文搜尋
            url = f"https://www.google.com/search?q={encoded_query}&tbm=isch&start={start_index}{tbs_param}&hl=zh-TW&gl=TW&safe=off"
            
            headers = {
                'User-Agent': 'ai-media-generator (gzip)',  # 加入gzip標識
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',  # 啟用gzip壓縮
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            print(f"📡 請求URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=120)
            response.raise_for_status()
            
            html_content = response.text
            print(f"📄 回應長度: {len(html_content)} 字元")
            
            results = []
            found_urls = set()  # 初始化found_urls變數
            
            # 方法1: 2025年新的JSON數據提取方法
            # Google現在使用不同的JSON結構存儲圖片數據
            json_patterns = [
                r'AF_initDataCallback\({[^}]*?"ds:1"[^}]*?},{.*?}\);',
                r'window\._sharedData\s*=\s*({.*?});',
                r'AF_initDataCallback\({[^}]*?"ds:0"[^}]*?},{.*?}\);',
                r'\\x22(https?://[^\\]*\.(?:jpg|jpeg|png|webp|gif)[^\\]*?)\\x22'
            ]
            
            for pattern in json_patterns:
                json_matches = re.findall(pattern, html_content, re.DOTALL)
                print(f"  🔍 JSON模式匹配到 {len(json_matches)} 個結果")
                
                for json_match in json_matches:
                    try:
                        if json_match.startswith('http'):
                            # 直接是URL
                            if json_match not in found_urls:
                                found_urls.add(json_match)
                        else:
                            # 嘗試從JSON中提取URL
                            url_matches = re.findall(r'https?://[^"\'\\]*\.(?:jpg|jpeg|png|webp|gif)[^"\'\\]*', json_match)
                            for url in url_matches:
                                if url not in found_urls and len(found_urls) < per_page * 3:
                                    found_urls.add(url)
                    except Exception as e:
                        continue
                
                if len(found_urls) >= per_page:
                    print(f"  ✅ JSON解析已找到足夠URL: {len(found_urls)}")
                    break
            
            # 方法2: 基於實際調試結果的圖片URL提取
            # 根據實際的Google頁面結構調整解析策略
            img_patterns = [
                # 過濾掉Google自己的圖示和無效URL
                r'"(https?://(?!ssl\.gstatic\.com|www\.gstatic\.com|fonts\.gstatic\.com)[^"]*\.(?:jpg|jpeg|png|webp|gif)(?:\?[^"]*)?)"',
                # img標籤中的src屬性（排除Google自己的圖片）
                r'<img[^>]+src="(https?://(?!ssl\.gstatic\.com|www\.gstatic\.com)[^"]*\.(?:jpg|jpeg|png|webp|gif)[^"]*)"',
                # data-src屬性
                r'data-src="(https?://(?!ssl\.gstatic\.com|www\.gstatic\.com)[^"]*\.(?:jpg|jpeg|png|webp|gif)[^"]*)"',
                # 通用圖片URL（但要過濾掉明顯的無效URL）
                r'(https?://(?!ssl\.gstatic\.com|www\.gstatic\.com|fonts\.gstatic\.com|www\.png)[^\s<>"\']*\.(?:jpg|jpeg|png|webp|gif)(?:\?[^\s<>"\']*)?)',
                # Google代理的圖片URL
                r'"(https://encrypted-tbn\d\.gstatic\.com/images\?[^"]*)"',
                # 其他Google圖片服務URL
                r'"(https://lh\d+\.googleusercontent\.com/[^"]*)"',
                # 更嚴格的模式：只匹配看起來像真實圖片網站的URL
                r'"(https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/[^"]*\.(?:jpg|jpeg|png|webp|gif)(?:\?[^"]*)?)"',
                # JavaScript中的圖片URL
                r'imgUrl["\']?\s*[:=]\s*["\']([^"\']*\.(?:jpg|jpeg|png|webp|gif)[^"\']*)["\']',
                # 尋找包含實際圖片網站域名的URL
                r'"(https?://(?:media\.|images\.|cdn\.|static\.|img\.|photo\.)[^"]*\.(?:jpg|jpeg|png|webp|gif)[^"]*)"',
                # Base64編碼的圖片數據
                r'"(data:image/[^;]+;base64,[A-Za-z0-9+/=]{200,})"'
            ]
            
            # found_urls已經在上面初始化了
            
            print(f"🔍 開始提取圖片URL，目標數量: {per_page * 3}")  # 多提取一些
            
            for i, pattern in enumerate(img_patterns):
                print(f"  🔎 使用模式 {i+1}: 正在搜尋...")
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                new_matches = 0
                for match in matches:
                    if match not in found_urls and len(found_urls) < per_page * 3:
                        found_urls.add(match)
                        new_matches += 1
                print(f"  ✅ 模式 {i+1} 找到 {len(matches)} 個匹配，新增 {new_matches} 個URL")
                
                # 如果已經找到足夠的URL，可以提前停止
                if len(found_urls) >= per_page * 2:
                    print(f"  🎯 已找到足夠的URL ({len(found_urls)}個)，停止搜尋")
                    break
            
            print(f"🔍 總共找到 {len(found_urls)} 個唯一圖片URL")
            
            # 方法3: 如果前面的方法都失敗，使用更寬鬆的搜尋
            if len(found_urls) == 0:
                print("⚠️ 前面的方法都沒找到URL，嘗試更寬鬆的搜尋...")
                
                # 搜尋所有看起來像圖片URL的字串（更寬鬆但仍要過濾無效URL）
                loose_patterns = [
                    # 基本圖片URL但排除明顯的無效域名
                    r'(https?://(?!ssl\.gstatic\.com|www\.gstatic\.com|fonts\.gstatic\.com|www\.png)[^\s<>"\']*\.(?:jpg|jpeg|png|webp|gif))',
                    # 包含images關鍵字的URL
                    r'(https?://[^\s<>"\']*images[^\s<>"\']*\.(?:jpg|jpeg|png|webp|gif))',
                    # 包含photo關鍵字的URL
                    r'(https?://[^\s<>"\']*photo[^\s<>"\']*\.(?:jpg|jpeg|png|webp|gif))',
                    # 包含thumb關鍵字的URL
                    r'(https?://[^\s<>"\']*thumb[^\s<>"\']*\.(?:jpg|jpeg|png|webp|gif))',
                    # 包含media關鍵字的URL
                    r'(https?://[^\s<>"\']*media[^\s<>"\']*\.(?:jpg|jpeg|png|webp|gif))',
                    # 包含cdn關鍵字的URL
                    r'(https?://[^\s<>"\']*cdn[^\s<>"\']*\.(?:jpg|jpeg|png|webp|gif))',
                    # 非常寬鬆的模式：任何看起來像真實網站的圖片URL
                    r'(https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/[^\s<>"\']*\.(?:jpg|jpeg|png|webp|gif))',
                ]
                
                for pattern in loose_patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    print(f"  🔍 寬鬆模式找到 {len(matches)} 個匹配")
                    for match in matches:
                        if match not in found_urls and len(found_urls) < per_page * 2:
                            found_urls.add(match)
                    
                    if len(found_urls) >= per_page:
                        break
                
                print(f"🔍 寬鬆搜尋後總共找到 {len(found_urls)} 個URL")
            
            # 轉換為結果格式
            valid_count = 0
            skipped_count = 0
            
            # 將URL按優先級排序（優先選擇高品質的URL）
            url_list = list(found_urls)
            priority_urls = []
            other_urls = []
            
            for url in url_list:
                # 優先選擇直接的圖片URL和高品質來源
                if (any(domain in url for domain in ['wikipedia.org', 'wikimedia.org', 'unsplash.com', 'pexels.com']) or
                    url.startswith('https://') and any(ext in url for ext in ['.jpg', '.jpeg', '.png', '.webp']) and
                    'encrypted-tbn' not in url):
                    priority_urls.append(url)
                else:
                    other_urls.append(url)
            
            # 合併優先級URL和其他URL
            sorted_urls = priority_urls + other_urls
            
            print(f"📊 URL優先級排序: {len(priority_urls)} 個高優先級, {len(other_urls)} 個一般優先級")
            
            for i, img_url in enumerate(sorted_urls[:per_page * 3]):  # 檢查更多URL
                # 跳過明顯無效的URL
                skip_reasons = []
                
                if '/1x1_' in img_url or 'spacer.gif' in img_url:
                    skip_reasons.append("尺寸過小")
                elif img_url.startswith('data:image') and len(img_url) < 200:
                    skip_reasons.append("Base64圖片太小")
                elif 'logo' in img_url.lower() and any(size in img_url for size in ['16x16', '32x32', '48x48']):
                    skip_reasons.append("小圖示")
                elif len(img_url) < 20:
                    skip_reasons.append("URL太短")
                
                if skip_reasons:
                    skipped_count += 1
                    if skipped_count <= 5:  # 只顯示前5個跳過的URL
                        print(f"⏭️ 跳過圖片 ({', '.join(skip_reasons)}): {img_url[:80]}...")
                    continue
                
                print(f"✅ 添加圖片 {valid_count + 1}: {img_url[:80]}...")
                    
                image_info = {
                    'id': f"google_scrape_{int(time.time())}_{valid_count}",
                    'url': img_url,
                    'thumb_url': img_url,
                    'title': f"{query} - 圖片 {valid_count + 1}",
                    'description': f"從Google搜尋獲得的 '{query}' 相關圖片",
                    'width': None,
                    'height': None,
                    'source_url': '',
                    'file_type': self._get_file_extension(img_url).upper(),
                    'platform': 'google',
                    'attribution': '來源: Google圖片搜尋',
                    'download_url': img_url
                }
                results.append(image_info)
                valid_count += 1
                
                # 達到目標數量就停止
                if valid_count >= per_page:
                    break
            
            if skipped_count > 5:
                print(f"⏭️ 另外跳過了 {skipped_count - 5} 個無效URL...")
            
            print(f"📈 處理結果: 有效圖片 {valid_count} 張，跳過 {skipped_count} 個URL")
            
            # 如果沒有找到足夠的結果，補充一些相關的示例
            if len(results) < 3:
                print("⚠️ 搜尋結果較少，補充示例圖片")
                fallback_results = self._get_fallback_results(query, per_page - len(results))
                results.extend(fallback_results['results'])
            
            print(f"✅ 最終返回 {len(results)} 張圖片")
            
            return {
                'success': True,
                'query': query,
                'page': page,
                'per_page': per_page,
                'total_results': len(results),
                'results': results,
                'images': results,  # 為前端兼容性添加
                'platform': 'google',
                'mode': 'web_scraping',
                'message': f'找到 {len(results)} 張圖片 (Web Scraping模式)'
            }
            
        except Exception as e:
            print(f"❌ Web scraping搜尋失敗: {e}")
            # 如果scraping失敗，提供一些示例結果
            return self._get_fallback_results(query, per_page)
    
    def _get_file_extension(self, url: str) -> str:
        """從URL中提取檔案副檔名"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            if '.jpg' in path:
                return 'jpg'
            elif '.jpeg' in path:
                return 'jpeg'
            elif '.png' in path:
                return 'png'
            elif '.webp' in path:
                return 'webp'
            elif '.gif' in path:
                return 'gif'
            else:
                return 'jpg'  # 預設
        except:
            return 'jpg'
    
    def _get_fallback_results(self, query: str, per_page: int) -> Dict:
        """提供備用示例結果"""
        results = []
        
        # 為不同關鍵字提供更相關的示例圖片
        keyword_seeds = {
            '海象': [1001, 1002, 1003, 1004, 1005, 1006],
            '貓': [200, 201, 202, 203, 204, 205],
            '狗': [220, 221, 222, 223, 224, 225],
            '花': [100, 101, 102, 103, 104, 105],
            '山': [300, 301, 302, 303, 304, 305],
            '海': [400, 401, 402, 403, 404, 405],
            '車': [500, 501, 502, 503, 504, 505],
            '建築': [600, 601, 602, 603, 604, 605],
            '食物': [700, 701, 702, 703, 704, 705],
            '人物': [800, 801, 802, 803, 804, 805]
        }
        
        # 找到最相關的種子
        seeds = None
        for keyword, seed_list in keyword_seeds.items():
            if keyword in query:
                seeds = seed_list
                break
        
        # 如果沒有找到特定關鍵字，使用通用種子
        if not seeds:
            import hashlib
            hash_int = int(hashlib.md5(query.encode()).hexdigest()[:8], 16)
            seeds = [(hash_int + i) % 1000 for i in range(per_page)]
        
        for i in range(min(per_page, len(seeds))):
            seed = seeds[i]
            results.append({
                'id': f"demo_{query}_{i+1}",
                'url': f"https://picsum.photos/800/600?random={seed}",
                'thumb_url': f"https://picsum.photos/300/200?random={seed}",
                'title': f"示例圖片: {query} #{i+1}",
                'description': f"這是關於 '{query}' 的相關示例圖片",
                'width': 800,
                'height': 600,
                'source_url': 'https://picsum.photos',
                'file_type': 'JPG',
                'platform': 'demo',
                'attribution': '示例圖片來源: Lorem Picsum',
                'download_url': f"https://picsum.photos/800/600?random={seed}"
            })
        
        return {
            'success': True,
            'query': query,
            'total_results': len(results),
            'results': results,
            'images': results,  # 為前端兼容性添加
            'platform': 'demo',
            'mode': 'fallback',
            'message': f'示例模式：顯示 {len(results)} 張 "{query}" 相關示例圖片'
        }
    
    def download_image(self, image_url: str, filename: str = None) -> Dict:
        """
        下載圖片到本地
        
        Args:
            image_url: 圖片URL
            filename: 自定義檔案名稱
        """
        try:
            # 產生檔案名稱
            if not filename:
                file_id = str(uuid.uuid4())[:8]
                timestamp = int(time.time())
                # 從URL中提取副檔名
                parsed_url = urlparse(image_url)
                path = parsed_url.path
                if '.' in path:
                    extension = path.split('.')[-1].lower()
                    if extension not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                        extension = 'jpg'
                else:
                    extension = 'jpg'
                filename = f"google_img_{timestamp}_{file_id}.{extension}"
            
            # 設定下載路徑
            download_path = self.download_dir / filename
            
            # 下載圖片
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=120)
            response.raise_for_status()
            
            # 檢查內容類型
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return {
                    'success': False,
                    'error': f'不是有效的圖片格式: {content_type}',
                    'message': '下載的內容不是圖片格式'
                }
            
            # 儲存檔案
            with open(download_path, 'wb') as f:
                f.write(response.content)
            
            # 檢查檔案大小
            file_size = download_path.stat().st_size
            if file_size == 0:
                download_path.unlink()  # 刪除空檔案
                return {
                    'success': False,
                    'error': '下載的檔案為空',
                    'message': '圖片下載失敗'
                }
            
            return {
                'success': True,
                'filename': filename,
                'file_path': str(download_path),
                'file_size': file_size,
                'download_url': f"/static/downloaded_images/{filename}",
                'message': f'圖片已成功下載: {filename}'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'下載失敗: {str(e)}',
                'message': '無法下載圖片，請檢查網路連線'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'下載過程中發生錯誤: {str(e)}',
                'message': '圖片下載失敗'
            }
    
    def get_search_options(self) -> Dict:
        """獲取搜尋選項"""
        return {
            'sizes': [
                {'id': 'any', 'name': '任何尺寸'},
                {'id': 'large', 'name': '大尺寸'},
                {'id': 'medium', 'name': '中等尺寸'},
                {'id': 'icon', 'name': '圖示'}
            ],
            'types': [
                {'id': 'photo', 'name': '照片'},
                {'id': 'clipart', 'name': '美工圖案'},
                {'id': 'lineart', 'name': '線條圖'},
                {'id': 'face', 'name': '人臉'}
            ],
            'orientations': [
                {'id': 'any', 'name': '任何方向'},
                {'id': 'landscape', 'name': '橫向'},
                {'id': 'portrait', 'name': '直向'}
            ]
        } 