"""
OpenAI DALL-E 圖像生成服務
支援 DALL-E-3 模型進行高品質圖像生成
"""

import os
import time
import requests
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 嘗試導入 OpenAI SDK
try:
    import openai
    OPENAI_AVAILABLE = True
    print("✅ OpenAI SDK 可用")
except ImportError as e:
    print(f"⚠️ OpenAI SDK 不可用: {e}")
    print("💡 請執行: pip install openai")
    OPENAI_AVAILABLE = False
    
    # 創建模擬的 OpenAI 類別
    class openai:
        class OpenAI:
            def __init__(self, api_key=None):
                raise Exception("OpenAI SDK 不可用")

class OpenAIImageService:
    """OpenAI DALL-E 圖像生成服務"""
    
    def __init__(self):
        """初始化 OpenAI 圖像生成服務"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_IMAGE_GEN_MODEL', 'dall-e-3')
        self.use_mock = False
        
        if not OPENAI_AVAILABLE:
            print("⚠️ OpenAI SDK 不可用，將使用模擬模式")
            self.use_mock = True
            return
        
        if not self.api_key:
            print("⚠️ OPENAI_API_KEY 未設定，將使用模擬模式")
            self.use_mock = True
            return
        
        try:
            # 初始化 OpenAI 客戶端
            self.client = openai.OpenAI(api_key=self.api_key)
            print(f"✅ OpenAI 圖像服務已初始化")
            print(f"   模型: {self.model}")
            print(f"   API Key: {'已設定' if self.api_key else '未設定'}")
            
        except Exception as e:
            print(f"❌ OpenAI 圖像服務初始化失敗: {e}")
            self.use_mock = True
    
    def generate_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成圖像
        
        Args:
            params: 生成參數
                - prompt: 圖像描述
                - count: 生成數量 (1-4)
                - size: 圖像尺寸 ('1024x1024', '1024x1792', '1792x1024')
                - quality: 圖像品質 ('standard', 'hd')
                - style: 圖像風格 ('vivid', 'natural')
        
        Returns:
            包含生成結果的字典
        """
        if self.use_mock:
            return self._generate_mock_images(params)
        
        try:
            # 驗證參數
            validation_result = self._validate_params(params)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            prompt = params['prompt']
            count = min(int(params.get('count', 1)), 4)  # DALL-E-3 最多4張
            size = params.get('size', '1024x1024')
            quality = params.get('quality', 'standard')
            style = params.get('style', 'vivid')
            
            print(f"🎨 開始生成圖像 (OpenAI DALL-E)...")
            print(f"   Prompt: {prompt[:100]}...")
            print(f"   數量: {count}, 尺寸: {size}")
            print(f"   品質: {quality}, 風格: {style}")
            
            # 調用 OpenAI API (根據官方範例)
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                n=count,
                size=size,
                quality=quality,
                style=style
            )
            
            # 處理響應
            images = []
            generated_dir = os.path.join(os.getcwd(), 'generated')
            os.makedirs(generated_dir, exist_ok=True)
            
            for i, image_data in enumerate(response.data):
                try:
                    # 下載圖像
                    image_url = image_data.url
                    print(f"📥 下載圖像 {i+1}...")
                    
                    # 生成檔案名稱
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_prompt = "".join(filter(str.isalnum, prompt[:30])).lower()
                    filename = f"dalle_{safe_prompt}_{timestamp}_{i}.png"
                    local_path = os.path.join(generated_dir, filename)
                    
                    # 下載圖像檔案
                    img_response = requests.get(image_url, timeout=30)
                    img_response.raise_for_status()
                    
                    with open(local_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    # 檢查檔案大小
                    file_size = os.path.getsize(local_path)
                    if file_size > 0:
                        image_info = {
                            'url': f'/generated/{filename}',
                            'filename': filename,
                            'path': local_path,
                            'size': size,
                            'quality': quality,
                            'style': style,
                            'file_size': file_size,
                            'timestamp': datetime.now().isoformat(),
                            'model': self.model,
                            'revised_prompt': getattr(image_data, 'revised_prompt', prompt)
                        }
                        images.append(image_info)
                        print(f"✅ 圖像 {i+1} 已保存: {filename} ({file_size:,} bytes)")
                    else:
                        print(f"❌ 圖像檔案大小為0: {filename}")
                        
                except Exception as e:
                    print(f"❌ 下載第 {i+1} 張圖像時發生錯誤: {e}")
                    continue
            
            if images:
                return {
                    'success': True,
                    'images': images,
                    'total_count': len(images),
                    'generation_time': f'{len(images) * 10} 秒',
                    'model': self.model,
                    'prompt': prompt,
                    'parameters': {
                        'count': count,
                        'size': size,
                        'quality': quality,
                        'style': style
                    },
                    'mock_mode': False,
                    'api_type': 'OpenAI DALL-E'
                }
            else:
                return {
                    'success': False,
                    'error': '無法下載任何生成的圖像'
                }
                
        except Exception as e:
            print(f"❌ OpenAI 圖像生成錯誤: {e}")
            traceback.print_exc()
            
            # 檢查是否為內容政策錯誤
            error_message = str(e)
            if 'image_generation_user_error' in error_message or 'content_policy' in error_message.lower():
                return {
                    'success': False,
                    'error': 'Prompt 內容不符合 OpenAI 內容政策，請修改後重試。建議移除可能敏感的描述，或使用「🎨 優化 Prompt」功能獲得安全的替代建議。',
                    'error_type': 'content_policy_violation',
                    'suggestion': '請嘗試使用更安全、正面的描述，避免涉及敏感內容。'
                }
            elif 'bad_request' in error_message.lower() or '400' in error_message:
                return {
                    'success': False,
                    'error': '請求參數有誤，請檢查 Prompt 內容和生成設定。',
                    'error_type': 'bad_request',
                    'suggestion': '請確認 Prompt 內容適當，並檢查圖像尺寸、品質等設定是否正確。'
                }
            else:
                return {
                    'success': False,
                    'error': f'圖像生成失敗: {error_message}',
                    'error_type': 'general_error'
                }
    
    def _generate_mock_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成模擬圖像（當無法使用真實 API 時）"""
        print("🎭 使用模擬模式生成圖像...")
        time.sleep(2)  # 模擬處理時間
        
        prompt = params.get('prompt', '測試圖像')
        count = min(int(params.get('count', 1)), 4)
        size = params.get('size', '1024x1024')
        quality = params.get('quality', 'standard')
        style = params.get('style', 'vivid')
        
        # 創建模擬圖像
        images = []
        generated_dir = os.path.join(os.getcwd(), 'generated')
        os.makedirs(generated_dir, exist_ok=True)
        
        for i in range(count):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dalle_mock_{timestamp}_{i}.png"
            local_path = os.path.join(generated_dir, filename)
            
            # 創建簡單的模擬圖像
            self._create_mock_image(local_path, size, prompt)
            
            if os.path.exists(local_path):
                image_info = {
                    'url': f'/generated/{filename}',
                    'filename': filename,
                    'path': local_path,
                    'size': size,
                    'quality': quality,
                    'style': style,
                    'file_size': os.path.getsize(local_path),
                    'timestamp': datetime.now().isoformat(),
                    'model': f"{self.model} (模擬)",
                    'revised_prompt': f"模擬生成: {prompt}"
                }
                images.append(image_info)
        
        return {
            'success': True,
            'images': images,
            'total_count': len(images),
            'generation_time': '2 秒 (模擬)',
            'model': f"{self.model} (模擬)",
            'prompt': prompt,
            'parameters': {
                'count': count,
                'size': size,
                'quality': quality,
                'style': style
            },
            'mock_mode': True
        }
    
    def _create_mock_image(self, image_path: str, size: str, prompt: str):
        """創建模擬圖像檔案"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 解析尺寸
            width, height = map(int, size.split('x'))
            
            # 創建圖像
            image = Image.new('RGB', (width, height), color='lightblue')
            draw = ImageDraw.Draw(image)
            
            # 添加文字
            try:
                # 嘗試使用系統字體
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            text = f"DALL-E Mock\n{prompt[:50]}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill='black', font=font)
            
            # 保存圖像
            image.save(image_path, 'PNG')
            
        except ImportError:
            # 如果沒有 PIL，創建一個簡單的檔案
            with open(image_path, 'wb') as f:
                # 創建一個最小的 PNG 檔案
                png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xa8\x05\x00\x00\x00\x00IEND\xaeB`\x82'
                f.write(png_data)
    
    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """驗證生成參數"""
        if not params.get('prompt'):
            return {'valid': False, 'error': '請提供圖像描述'}
        
        prompt = params['prompt'].strip()
        if len(prompt) > 4000:
            return {'valid': False, 'error': '圖像描述過長（最多4000字符）'}
        
        count = params.get('count', 1)
        try:
            count = int(count)
            if count < 1 or count > 4:
                return {'valid': False, 'error': '生成數量必須在1-4之間'}
        except (ValueError, TypeError):
            return {'valid': False, 'error': '生成數量必須是數字'}
        
        size = params.get('size', '1024x1024')
        valid_sizes = ['1024x1024', '1024x1792', '1792x1024']
        if size not in valid_sizes:
            return {'valid': False, 'error': f'不支援的圖像尺寸: {size}'}
        
        quality = params.get('quality', 'standard')
        if quality not in ['standard', 'hd']:
            return {'valid': False, 'error': f'不支援的圖像品質: {quality}'}
        
        style = params.get('style', 'vivid')
        if style not in ['vivid', 'natural']:
            return {'valid': False, 'error': f'不支援的圖像風格: {style}'}
        
        return {'valid': True}
    
    def get_supported_sizes(self) -> List[str]:
        """獲取支援的圖像尺寸"""
        return ['1024x1024', '1024x1792', '1792x1024']
    
    def get_supported_qualities(self) -> List[str]:
        """獲取支援的圖像品質"""
        return ['standard', 'hd']
    
    def get_supported_styles(self) -> List[str]:
        """獲取支援的圖像風格"""
        return ['vivid', 'natural']
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型資訊"""
        return {
            'name': self.model,
            'provider': 'OpenAI',
            'type': 'image_generation',
            'max_images': 4,
            'supported_sizes': self.get_supported_sizes(),
            'supported_qualities': self.get_supported_qualities(),
            'supported_styles': self.get_supported_styles(),
            'mock_mode': self.use_mock
        }
    
    def calculate_cost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """計算生成成本"""
        count = int(params.get('count', 1))
        size = params.get('size', '1024x1024')
        quality = params.get('quality', 'standard')
        
        # DALL-E-3 定價 (2024年價格)
        if quality == 'hd':
            if size == '1024x1024':
                price_per_image = 0.080  # $0.080 per image
            else:  # 1024x1792 or 1792x1024
                price_per_image = 0.120  # $0.120 per image
        else:  # standard quality
            if size == '1024x1024':
                price_per_image = 0.040  # $0.040 per image
            else:  # 1024x1792 or 1792x1024
                price_per_image = 0.080  # $0.080 per image
        
        total_cost = count * price_per_image
        
        return {
            'total_cost_usd': total_cost,
            'total_cost_twd': total_cost * 31,  # 假設匯率 1 USD = 31 TWD
            'cost_per_image_usd': price_per_image,
            'cost_breakdown': {
                'count': count,
                'size': size,
                'quality': quality,
                'price_per_image': price_per_image
            }
        }

def test_openai_image_service():
    """測試 OpenAI 圖像生成服務"""
    print("🧪 測試 OpenAI 圖像生成服務...")
    
    service = OpenAIImageService()
    
    test_params = {
        'prompt': 'A beautiful sunset over a mountain landscape',
        'count': 1,
        'size': '1024x1024',
        'quality': 'standard',
        'style': 'vivid'
    }
    
    result = service.generate_images(test_params)
    
    if result['success']:
        print("✅ 測試成功")
        print(f"   生成了 {result['total_count']} 張圖像")
        print(f"   模型: {result['model']}")
        print(f"   模擬模式: {result.get('mock_mode', False)}")
    else:
        print(f"❌ 測試失敗: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    test_openai_image_service() 