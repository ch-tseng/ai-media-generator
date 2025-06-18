import os
import time
import random
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import uuid
from datetime import datetime

try:
    from google.cloud import aiplatform
    from vertexai.vision_models import ImageGenerationModel
    import vertexai
    VERTEX_AI_AVAILABLE = True
except ImportError:
    try:
        # 如果穩定版本不可用，嘗試預覽版本
        from vertexai.preview.vision_models import ImageGenerationModel
        import vertexai
        VERTEX_AI_AVAILABLE = True
    except ImportError:
        VERTEX_AI_AVAILABLE = False

class ImagenService:
    """Imagen 4 圖像生成服務（支援 Vertex AI）"""
    
    def __init__(self, project_id: str = None, location: str = "us-central1", use_mock: bool = False, model_name: str = None):
        """
        初始化 Imagen 服務
        
        Args:
            project_id: Google Cloud 專案 ID
            location: Google Cloud 區域
            use_mock: 是否使用模擬模式
            model_name: 使用的模型名稱（如果未指定則使用環境變數或預設值）
        """
        self.project_id = project_id
        self.location = location
        self.use_mock = use_mock  # 不自動切換到模擬模式
        
        # 設定模型名稱（優先順序：參數 > 環境變數 > 預設值）
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = os.environ.get('IMAGE_GEN_MODEL', 'imagen-4.0-fast-generate-preview-06-06')
        
        # Imagen 支援的參數（根據 Vertex AI 官方文件）
        # 參考: https://cloud.google.com/vertex-ai/generative-ai/docs/image/generate-images
        # 基於 Vertex AI 支援的長寬比：1:1, 3:4, 4:3, 9:16, 16:9
        self.supported_sizes = [
            '1024x1024',  # 正方形 (1:1)
            '1152x896',   # 橫向 (4:3)
            '896x1152',   # 直向 (3:4)
        ]
        self.supported_qualities = ['standard', 'high', 'ultra']

        
        # Imagen 模型版本（使用配置的模型）
        self.model_versions = {
            'standard': self.model_name,  # 使用配置的模型
            'high': self.model_name,      # 高品質使用相同模型但不同參數
            'ultra': self.model_name      # 超高品質
        }
        
        # 建立輸出目錄
        self.output_dir = 'generated/images'
        os.makedirs(self.output_dir, exist_ok=True)
        
        if self.use_mock:
            print(f"🔧 使用 Imagen 模擬模式 (模型: {self.model_name})")
        else:
            # 檢查必要條件
            if not VERTEX_AI_AVAILABLE:
                raise Exception("❌ Vertex AI 套件不可用，請安裝: pip install google-cloud-aiplatform")
            
            if not project_id:
                raise Exception("❌ 未設定 Google Cloud 專案 ID，請在 .env 文件中設定 GOOGLE_CLOUD_PROJECT")
            
            try:
                # 初始化 Vertex AI
                vertexai.init(project=project_id, location=location)
                # 使用配置的模型
                self.model = ImageGenerationModel.from_pretrained(self.model_name)
                print(f"✅ Imagen 服務已初始化 (專案: {project_id}, 模型: {self.model_name}, 真實 API 模式)")
            except Exception as e:
                error_msg = f"❌ Vertex AI 初始化失敗: {e}"
                if "authentication" in str(e).lower():
                    error_msg += "\n請檢查 GOOGLE_APPLICATION_CREDENTIALS 或 API 金鑰設定"
                elif "permission" in str(e).lower():
                    error_msg += "\n請確保服務帳戶有 Vertex AI 權限"
                raise Exception(error_msg)
    
    def generate_images(self, params: Dict[str, any]) -> Dict[str, any]:
        """
        生成圖像
        
        Args:
            params: 生成參數字典
                - prompt: 文字描述
                - count: 生成數量 (1-10)
                - quality: 品質等級 ('standard', 'high', 'ultra')
                - size: 圖像尺寸 ('1024x1024', '1024x1792', '1792x1024')
                - style: 風格 ('natural', 'artistic', 'realistic')
        
        Returns:
            生成結果字典
        """
        # 驗證參數
        validation_result = self._validate_parameters(params)
        if not validation_result.get('valid'):
            return validation_result
        
        prompt = params['prompt']
        count = params.get('count', 1)
        quality = params.get('quality', 'standard')
        size = params.get('size', '1024x1024')
        
        generation_id = str(uuid.uuid4())
        start_time = time.time()
        
        print(f"🎨 開始生成圖像 - ID: {generation_id}")
        print(f"📝 原始 Prompt: {prompt}")
        print(f"⚙️ 參數: {count}張, {quality}品質, {size}尺寸")
        print(f"🔧 使用模式: {'模擬' if self.use_mock else 'Vertex AI'}")
        
        if self.use_mock:
            return self._generate_images_mock(params, generation_id, start_time)
        else:
            return self._generate_images_vertex_ai(params, generation_id, start_time)
    
    def _generate_images_vertex_ai(self, params: Dict[str, any], generation_id: str, start_time: float) -> Dict[str, any]:
        """使用 Vertex AI 生成圖像"""
        try:
            prompt = params['prompt']
            count = params.get('count', 1)
            quality = params.get('quality', 'standard')
            size = params.get('size', '1024x1024')
            
            # 構建 Vertex AI 參數（根據 Vertex AI Python SDK 規範）
            # 參考: https://cloud.google.com/vertex-ai/generative-ai/docs/image/generate-images
            vertex_params = {
                'prompt': prompt,
            }
            
            # 添加尺寸參數 - 使用 aspect_ratio 參數
            aspect_ratio = self._convert_size_to_aspect_ratio(size)
            vertex_params['aspect_ratio'] = aspect_ratio
            
            # 添加圖像數量參數 - 每次最多生成 4 張
            vertex_params['number_of_images'] = min(count, 4)
            
            # 根據品質調整參數（如果 API 支援）
            # 注意：某些 Imagen 版本可能不支援 guidance_scale 參數
            # 品質主要透過模型版本選擇來控制（如 imagen-3.0-generate-001 vs imagen-3.0-fast-generate-001）
            if hasattr(self, 'model') and hasattr(self.model, 'generate_images'):
                # 對於支援品質參數的模型版本
                pass  # 暫時不設定額外的品質參數，依賴模型本身的品質
            
            print(f"📤 發送到 Vertex AI 的參數: {vertex_params}")
            print(f"📏 尺寸: {size} -> 長寬比: {aspect_ratio}")
            
            generated_images = []
            
            # 如果需要生成超過 4 張，分批處理
            batches = (count + 3) // 4  # 向上取整
            for batch_num in range(batches):
                batch_count = min(4, count - batch_num * 4)
                if batch_count <= 0:
                    break
                
                # 調整批次參數
                batch_params = vertex_params.copy()
                batch_params['number_of_images'] = batch_count
                
                # 調用 Vertex AI（使用基本參數）
                try:
                    response = self.model.generate_images(**batch_params)
                except Exception as e:
                    print(f"⚠️ 生成失敗，錯誤: {e}")
                    raise
                
                # 處理返回的圖像
                for i, image in enumerate(response.images):
                    image_index = batch_num * 4 + i + 1
                    
                    # 儲存圖像
                    filename = f"imagen4_{generation_id}_{image_index}_{int(time.time())}.png"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    # 儲存圖像到檔案
                    image.save(location=filepath, include_generation_parameters=False)
                    
                    generated_images.append({
                        'image_id': f"{generation_id}_{image_index}",
                        'filename': filename,
                        'filepath': filepath,
                        'url': f"/generated/images/{filename}",
                        'size': size,
                        'quality': quality,
                        'file_size': os.path.getsize(filepath),
                        'created_at': datetime.now().isoformat(),
                        'model_version': 'imagen-4',
                        'batch_number': batch_num + 1
                    })
                
                # 批次間等待（避免 API 限制）
                if batch_num < batches - 1:
                    time.sleep(1)
            
            end_time = time.time()
            generation_time = round(end_time - start_time, 2)
            
            return {
                'success': True,
                'generation_id': generation_id,
                'images': generated_images,
                'total_count': len(generated_images),
                'generation_time': generation_time,
                'parameters': params,
                'timestamp': datetime.now().isoformat(),
                'service': 'vertex_ai',
                'model_version': 'imagen-4',
                'batches_processed': batches
            }
            
        except Exception as e:
            error_message = str(e)
            print(f"❌ Vertex AI 生成失敗: {e}")
            
            # 根據錯誤類型提供更詳細的錯誤訊息
            if '429' in error_message or 'Quota exceeded' in error_message:
                error_type = 'quota_exceeded'
                user_message = '配額已用完，請稍後再試或申請增加配額。詳情請參考：https://cloud.google.com/vertex-ai/docs/generative-ai/quotas-genai'
            elif '403' in error_message or 'permission' in error_message.lower():
                error_type = 'permission_denied'
                user_message = '權限不足，請檢查 Google Cloud 專案設定和 API 啟用狀態'
            elif '404' in error_message or 'not found' in error_message.lower():
                error_type = 'model_not_found'
                user_message = '模型不存在或不可用，請檢查模型版本'
            elif 'safety' in error_message.lower():
                error_type = 'safety_filter'
                user_message = 'Prompt 被安全過濾器阻擋，請修改內容後重試'
            else:
                error_type = 'api_error'
                user_message = f'圖像生成失敗: {error_message}'
            
            return {
                'success': False,
                'error': user_message,
                'error_details': error_message,
                'generation_id': generation_id,
                'service': 'vertex_ai',
                'error_type': error_type
            }
    

    
    def _generate_images_mock(self, params: Dict[str, any], generation_id: str, start_time: float) -> Dict[str, any]:
        """模擬圖像生成（開發測試用）"""
        prompt = params['prompt']
        count = params.get('count', 1)
        quality = params.get('quality', 'standard')
        size = params.get('size', '1024x1024')
        
        generated_images = []
        
        for i in range(count):
            # 創建佔位符圖像
            filename = f"imagen4_mock_{generation_id}_{i+1}_{int(time.time())}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            self._create_placeholder_image(filepath, size, prompt, quality)
            
            generated_images.append({
                'image_id': f"{generation_id}_{i+1}",
                'filename': filename,
                'filepath': filepath,
                'url': f"/generated/images/{filename}",
                'size': size,
                'quality': quality,
                'file_size': os.path.getsize(filepath),
                'created_at': datetime.now().isoformat(),
                'model_version': 'imagen-4-mock',
                'is_mock': True
            })
            
            # 模擬生成延遲
            time.sleep(0.5)
        
        end_time = time.time()
        generation_time = round(end_time - start_time, 2)
        
        return {
            'success': True,
            'generation_id': generation_id,
            'images': generated_images,
            'total_count': len(generated_images),
            'generation_time': generation_time,
            'parameters': params,
            'timestamp': datetime.now().isoformat(),
            'service': 'mock',
            'model_version': 'imagen-4-mock'
        }
    
    def _create_placeholder_image(self, filepath: str, size: str, prompt: str, quality: str):
        """創建佔位符圖像"""
        width, height = map(int, size.split('x'))
        
        # 創建圖像
        img = Image.new('RGB', (width, height), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # 嘗試載入字體
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # 添加文字
        text_lines = [
            "🎨 Imagen 4 模擬圖像",
            f"📏 尺寸: {size}",
            f"⭐ 品質: {quality}",
            f"📝 Prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}",
            f"⏰ 生成時間: {datetime.now().strftime('%H:%M:%S')}"
        ]
        
        y_offset = 50
        for line in text_lines:
            draw.text((50, y_offset), line, fill='darkblue', font=font)
            y_offset += 40
        
        # 添加裝飾性元素
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.ellipse([x-5, y-5, x+5, y+5], fill='lightcoral')
        
        # 儲存圖像
        img.save(filepath, 'PNG')
    
    def _convert_size_to_aspect_ratio(self, size: str) -> str:
        """將尺寸轉換為 Vertex AI 支援的長寬比格式
        
        根據 Vertex AI Imagen API 文檔，支援的長寬比：
        - 1:1 (正方形)
        - 3:4 (直向全屏)
        - 4:3 (橫向全屏) 
        - 9:16 (直向)
        - 16:9 (橫向)
        """
        size_mapping = {
            '1024x1024': '1:1',      # 正方形
            '1152x896': '4:3',       # 橫向全屏（最接近 1152:896 ≈ 1.29, 4:3 ≈ 1.33）
            '896x1152': '3:4',       # 直向全屏（最接近 896:1152 ≈ 0.78, 3:4 = 0.75）
        }
        return size_mapping.get(size, '1:1')
    
    def _validate_parameters(self, params: Dict[str, any]) -> Dict[str, any]:
        """驗證生成參數"""
        if not params:
            return {
                'valid': False,
                'error': '缺少生成參數',
                'error_code': 'MISSING_PARAMS'
            }
        
        prompt = params.get('prompt', '')
        if not prompt or len(prompt.strip()) == 0:
            return {
                'valid': False,
                'error': 'Prompt 不能為空',
                'error_code': 'EMPTY_PROMPT'
            }
        
        if len(prompt) > 2000:
            return {
                'valid': False,
                'error': 'Prompt 長度不能超過 2000 個字符',
                'error_code': 'PROMPT_TOO_LONG'
            }
        
        count = params.get('count', 1)
        if not isinstance(count, int) or count < 1 or count > 10:
            return {
                'valid': False,
                'error': '圖像數量必須在 1-10 之間',
                'error_code': 'INVALID_COUNT'
            }
        
        quality = params.get('quality', 'standard')
        if quality not in self.supported_qualities:
            return {
                'valid': False,
                'error': f'不支援的品質設定: {quality}',
                'error_code': 'INVALID_QUALITY'
            }
        
        size = params.get('size', '1024x1024')
        if size not in self.supported_sizes:
            return {
                'valid': False,
                'error': f'不支援的尺寸設定: {size}',
                'error_code': 'INVALID_SIZE'
            }
        
        return {'valid': True}
    
    def get_supported_parameters(self) -> Dict[str, List[str]]:
        """獲取支援的參數列表"""
        return {
            'sizes': self.supported_sizes,
            'qualities': self.supported_qualities,
            'model_versions': list(self.model_versions.keys())
        }
    
    def estimate_generation_time(self, params: Dict[str, any]) -> int:
        """估算生成時間（秒）"""
        if self.use_mock:
            return params.get('count', 1) * 2  # 模擬模式每張 2 秒
        
        count = params.get('count', 1)
        quality = params.get('quality', 'standard')
        
        # 基礎時間估算
        base_time_per_image = {
            'standard': 10,
            'high': 15,
            'ultra': 25
        }
        
        base_time = base_time_per_image.get(quality, 10)
        batches = (count + 3) // 4  # 每批最多 4 張
        
        return base_time * batches + (batches - 1) * 5  # 加上批次間等待時間
    
    def get_generation_status(self, generation_id: str) -> Dict[str, any]:
        """獲取生成狀態"""
        return {
            'generation_id': generation_id,
            'status': 'completed',
            'message': '圖像生成已完成'
        }
    
    def delete_generated_image(self, filepath: str) -> bool:
        """刪除生成的圖像"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"刪除圖像失敗: {e}")
            return False
    
    def get_image_info(self, filepath: str) -> Dict[str, any]:
        """獲取圖像資訊"""
        if not os.path.exists(filepath):
            return {'error': '圖像檔案不存在'}
        
        try:
            with Image.open(filepath) as img:
                return {
                    'filepath': filepath,
                    'size': f"{img.width}x{img.height}",
                    'format': img.format,
                    'mode': img.mode,
                    'file_size': os.path.getsize(filepath),
                    'created_at': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                }
        except Exception as e:
            return {'error': f'無法讀取圖像資訊: {str(e)}'} 