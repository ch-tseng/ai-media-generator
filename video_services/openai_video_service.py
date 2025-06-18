"""
OpenAI 影片生成服務
支援 OpenAI 影片生成模型
"""

import os
import time
import requests
import subprocess
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

class OpenAIVideoService:
    """OpenAI 影片生成服務"""
    
    def __init__(self):
        """初始化 OpenAI 影片生成服務"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_VIDEO_GEN_MODEL', 'veo-2.0-generate-001')
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
            print(f"✅ OpenAI 影片服務已初始化")
            print(f"   模型: {self.model}")
            print(f"   API Key: {'已設定' if self.api_key else '未設定'}")
            print("⚠️ 注意: OpenAI 影片生成功能目前可能尚未完全開放")
            
        except Exception as e:
            print(f"❌ OpenAI 影片服務初始化失敗: {e}")
            self.use_mock = True
    
    def generate_videos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成影片
        
        Args:
            params: 生成參數
                - prompt: 影片描述
                - aspectRatio: 影片比例 ('16:9' 或 '9:16')
                - duration: 影片長度 (5-8 秒)
                - personGeneration: 人物生成設定
        
        Returns:
            包含生成結果的字典
        """
        if self.use_mock:
            return self._generate_mock_video(params)
        
        try:
            # 驗證參數
            validation_result = self._validate_params(params)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            prompt = params['prompt']
            aspect_ratio = params.get('aspectRatio', '16:9')
            duration = params.get('duration', 5)
            person_generation = params.get('personGeneration', 'allow_adult')
            
            print(f"🎬 開始生成影片 (OpenAI)...")
            print(f"   Prompt: {prompt[:100]}...")
            print(f"   比例: {aspect_ratio}, 長度: {duration}秒")
            
            # 注意：OpenAI 的影片生成 API 可能尚未完全開放
            # 這裡使用模擬的 API 調用結構
            try:
                # 假設的 OpenAI 影片生成 API 調用
                # response = self.client.videos.generate(
                #     model=self.model,
                #     prompt=prompt,
                #     duration=duration,
                #     aspect_ratio=aspect_ratio
                # )
                
                # 由於 OpenAI 影片 API 可能尚未開放，暫時使用模擬模式
                print("⚠️ OpenAI 影片生成 API 尚未完全開放，使用模擬模式")
                return self._generate_mock_video(params)
                
            except Exception as api_error:
                print(f"❌ OpenAI 影片 API 調用失敗: {api_error}")
                print("🔄 回退到模擬模式")
                return self._generate_mock_video(params)
                
        except Exception as e:
            print(f"❌ OpenAI 影片生成錯誤: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'error': f'影片生成失敗: {str(e)}'
            }
    
    def _generate_mock_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成模擬影片（當無法使用真實 API 時）"""
        print("🎭 使用模擬模式生成影片...")
        time.sleep(3)  # 模擬處理時間
        
        prompt = params.get('prompt', '測試影片')
        aspect_ratio = params.get('aspectRatio', '16:9')
        duration = params.get('duration', 5)
        person_generation = params.get('personGeneration', 'allow_adult')
        
        # 生成模擬影片資訊
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"openai_mock_{timestamp}_{duration}s_{aspect_ratio.replace(':', 'x')}.mp4"
        
        # 創建符合標準的模擬影片檔案
        mock_video_path = self._create_standard_mock_video(filename, duration, aspect_ratio, prompt)
        
        video_info = {
            'url': f'/generated/{filename}',
            'filename': filename,
            'path': mock_video_path,
            'aspectRatio': aspect_ratio,
            'duration': duration,
            'file_size': os.path.getsize(mock_video_path) if os.path.exists(mock_video_path) else 0,
            'timestamp': datetime.now().isoformat(),
            'model': f"{self.model} (模擬)"
        }
        
        result = {
            'success': True,
            'videos': [video_info],
            'total_count': 1,
            'generation_time': '3 秒 (模擬)',
            'model': f"{self.model} (模擬)",
            'prompt': prompt,
            'parameters': {
                'aspect_ratio': aspect_ratio,
                'duration': duration,
                'person_generation': person_generation
            },
            'mock_mode': True,
            'api_type': 'OpenAI'
        }
        
        print(f"✅ 模擬生成完成")
        return result
    
    def _create_standard_mock_video(self, filename: str, duration: int, aspect_ratio: str, prompt: str) -> str:
        """創建符合標準的模擬影片檔案"""
        generated_dir = os.path.join(os.getcwd(), 'generated')
        os.makedirs(generated_dir, exist_ok=True)
        output_path = os.path.join(generated_dir, filename)
        
        # 根據比例設定解析度
        if aspect_ratio == '16:9':
            width, height = 1280, 720
        elif aspect_ratio == '9:16':
            width, height = 720, 1280
        else:
            width, height = 1280, 720
        
        print(f"🎬 創建標準 MP4 檔案")
        print(f"📐 解析度: {width}x{height} ({aspect_ratio})")
        print(f"⏱️ 長度: {duration} 秒")
        
        # 嘗試使用 FFmpeg 創建影片
        if self._create_ffmpeg_video(output_path, width, height, duration, prompt):
            print("✅ 使用 FFmpeg 創建標準 MP4 檔案")
        else:
            # 如果 FFmpeg 不可用，創建手動 MP4 檔案
            print("⚠️ FFmpeg 不可用，創建手動 MP4 檔案")
            self._create_manual_mp4(output_path, width, height, duration)
        
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        print(f"✅ 標準 MP4 檔案創建完成: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        return output_path
    
    def _create_ffmpeg_video(self, output_path: str, width: int, height: int, duration: int, prompt: str) -> bool:
        """使用 FFmpeg 創建影片"""
        try:
            # 清理 prompt 文字，移除特殊字符
            clean_prompt = prompt[:50].replace('"', "'").replace('\\', ' ').replace('\n', ' ')
            text_overlay = f"OpenAI Mock Video - {clean_prompt}"
            
            # FFmpeg 命令 - 修復 drawtext 語法
            cmd = [
                'ffmpeg', '-y',  # 覆蓋輸出檔案
                '-f', 'lavfi',   # 使用 lavfi 輸入格式
                '-i', f'color=c=blue:size={width}x{height}:duration={duration}:rate=30',  # 藍色背景
                '-vf', f"drawtext=text='{text_overlay}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2",  # 修復文字濾鏡語法
                '-c:v', 'libx264',  # 使用 H.264 編碼
                '-pix_fmt', 'yuv420p',  # 像素格式
                '-t', str(duration),  # 影片長度
                output_path
            ]
            
            print(f"🎬 執行 FFmpeg 命令: {' '.join(cmd)}")
            
            # 執行 FFmpeg 命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True
            else:
                print(f"FFmpeg 錯誤: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("FFmpeg 執行超時")
            return False
        except FileNotFoundError:
            print("找不到 FFmpeg")
            return False
        except Exception as e:
            print(f"FFmpeg 執行錯誤: {e}")
            return False
    
    def _create_manual_mp4(self, mp4_path: str, width: int, height: int, duration: int) -> None:
        """手動創建最小的 MP4 檔案"""
        try:
            fps = 30
            total_frames = duration * fps
            
            with open(mp4_path, 'wb') as f:
                # 寫入 ftyp box
                self._write_box(f, b'ftyp', b'isom\x00\x00\x02\x00isomiso2avc1mp41')
                
                # 寫入 moov box
                moov_data = self._create_moov_data(width, height, duration, total_frames)
                self._write_box(f, b'moov', moov_data)
                
                # 寫入 mdat box
                mdat_data = self._create_media_data(total_frames)
                self._write_box(f, b'mdat', mdat_data)
                
        except Exception as e:
            print(f"創建手動 MP4 失敗: {e}")
            # 創建最小檔案
            self._create_minimal_mp4(mp4_path, width, height, duration)
    
    def _write_box(self, f, box_type: bytes, data: bytes):
        """寫入 MP4 box"""
        size = len(data) + 8
        f.write(size.to_bytes(4, 'big'))
        f.write(box_type)
        f.write(data)
    
    def _create_moov_data(self, width: int, height: int, duration: int, total_frames: int) -> bytes:
        """創建 moov box 數據"""
        # 這是一個簡化的 moov box，包含基本的影片元數據
        mvhd_data = b'\x00' * 4  # version + flags
        mvhd_data += (1000).to_bytes(4, 'big')  # timescale
        mvhd_data += (duration * 1000).to_bytes(4, 'big')  # duration
        mvhd_data += b'\x00\x01\x00\x00'  # rate
        mvhd_data += b'\x01\x00\x00\x00'  # volume
        mvhd_data += b'\x00' * 10  # reserved
        mvhd_data += b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00'  # matrix
        mvhd_data += b'\x00' * 24  # preview time, preview duration, poster time, selection time, selection duration, current time
        mvhd_data += (2).to_bytes(4, 'big')  # next track ID
        
        moov_data = b''
        # mvhd box
        mvhd_size = len(mvhd_data) + 8
        moov_data += mvhd_size.to_bytes(4, 'big') + b'mvhd' + mvhd_data
        
        return moov_data
    
    def _create_media_data(self, total_frames: int) -> bytes:
        """創建媒體數據"""
        # 創建最小的媒體數據
        frame_data = b'\x00\x00\x00\x01\x67\x42\x00\x1e\x8b\x40\x50\x17\xfc\xb0\x8b\x10\x00\x00\x03\x00\x10\x00\x00\x03\x01\x42\x9c\x60'
        return frame_data * min(total_frames, 10)  # 限制數據大小
    
    def _create_minimal_mp4(self, mp4_path: str, width: int, height: int, duration: int) -> None:
        """創建最小的 MP4 檔案"""
        minimal_mp4_data = (
            b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
            b'\x00\x00\x00\x08free'
            b'\x00\x00\x00\x28mdat\x00\x00\x00\x01\x67\x42\x00\x1e'
            b'\x8b\x40\x50\x17\xfc\xb0\x8b\x10\x00\x00\x03\x00\x10'
            b'\x00\x00\x03\x01\x42\x9c\x60'
        )
        
        with open(mp4_path, 'wb') as f:
            f.write(minimal_mp4_data)
    
    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """驗證生成參數"""
        if not params.get('prompt'):
            return {'valid': False, 'error': '請提供影片描述'}
        
        prompt = params['prompt'].strip()
        if len(prompt) > 2000:
            return {'valid': False, 'error': '影片描述過長（最多2000字符）'}
        
        duration = params.get('duration', 5)
        try:
            duration = int(duration)
            if duration < 3 or duration > 10:
                return {'valid': False, 'error': '影片長度必須在3-10秒之間'}
        except (ValueError, TypeError):
            return {'valid': False, 'error': '影片長度必須是數字'}
        
        aspect_ratio = params.get('aspectRatio', '16:9')
        if aspect_ratio not in ['16:9', '9:16']:
            return {'valid': False, 'error': '不支援的影片比例'}
        
        return {'valid': True}
    
    def get_supported_aspect_ratios(self) -> List[str]:
        """獲取支援的影片比例"""
        return ['16:9', '9:16']
    
    def get_supported_durations(self) -> List[int]:
        """獲取支援的影片長度"""
        return [3, 4, 5, 6, 7, 8, 9, 10]
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型資訊"""
        return {
            'name': self.model,
            'provider': 'OpenAI',
            'type': 'video_generation',
            'max_duration': 10,
            'supported_aspect_ratios': self.get_supported_aspect_ratios(),
            'supported_durations': self.get_supported_durations(),
            'mock_mode': self.use_mock
        }
    
    def calculate_cost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """計算生成成本"""
        duration = int(params.get('duration', 5))
        aspect_ratio = params.get('aspectRatio', '16:9')
        
        # OpenAI 影片定價（假設價格，實際價格待官方公布）
        price_per_second = 0.10  # 假設每秒 $0.10
        
        total_cost = duration * price_per_second
        
        return {
            'total_cost_usd': total_cost,
            'total_cost_twd': total_cost * 31,  # 假設匯率 1 USD = 31 TWD
            'cost_per_second_usd': price_per_second,
            'cost_breakdown': {
                'duration': duration,
                'aspect_ratio': aspect_ratio,
                'price_per_second': price_per_second
            }
        }

def test_openai_video_service():
    """測試 OpenAI 影片生成服務"""
    print("🧪 測試 OpenAI 影片生成服務...")
    
    service = OpenAIVideoService()
    
    test_params = {
        'prompt': 'A beautiful sunset over a mountain landscape',
        'aspectRatio': '16:9',
        'duration': 5,
        'personGeneration': 'allow_adult'
    }
    
    result = service.generate_videos(test_params)
    
    if result['success']:
        print("✅ 測試成功")
        print(f"   生成了 {result['total_count']} 個影片")
        print(f"   模型: {result['model']}")
        print(f"   模擬模式: {result.get('mock_mode', False)}")
    else:
        print(f"❌ 測試失敗: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    test_openai_video_service() 