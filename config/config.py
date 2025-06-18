import os

class Config:
    """應用程式配置類別"""
    
    # Flask 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Google Cloud 設定 (用於 Veo 和 Imagen)
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
    GOOGLE_CLOUD_LOCATION = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Gemini API 設定 (用於 Prompt 優化)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')  # 默認使用 gemini-2.0-flash
    
    # Google 搜尋 API 設定 (可選)
    GOOGLE_SEARCH_API_KEY = os.environ.get('GOOGLE_SEARCH_API_KEY')
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
    
    # AI 模型設定
    IMAGE_GEN_MODEL = os.environ.get('IMAGE_GEN_MODEL', 'imagen-4.0-fast-generate-preview-06-06')  # 影像生成模型
    VIDEO_GEN_MODEL = os.environ.get('VIDEO_GEN_MODEL', 'veo-3.0-generate-preview')  # 影片生成模型
    
    # 服務設定
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '30'))
    MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', '16777216'))  # 16MB
    
    # 生成限制
    MAX_IMAGE_COUNT = int(os.environ.get('MAX_IMAGE_COUNT', '10'))
    MAX_VIDEO_COUNT = int(os.environ.get('MAX_VIDEO_COUNT', '5'))
    MAX_PROMPT_LENGTH = int(os.environ.get('MAX_PROMPT_LENGTH', '2000'))
    

    
    # 檔案上傳設定
    UPLOAD_FOLDER = 'uploads'
    GENERATED_FOLDER = 'generated'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
    
    # Imagen 4 支援的參數
    SUPPORTED_IMAGE_SIZES = ['1024x1024', '1024x1792', '1792x1024']
    SUPPORTED_IMAGE_QUALITIES = ['standard', 'high', 'ultra']
    
    # Veo 影片生成支援的參數
    SUPPORTED_VIDEO_RESOLUTIONS = ['720p', '1080p', '4k']
    SUPPORTED_VIDEO_DURATIONS = [3, 5, 10]
    SUPPORTED_VIDEO_FRAMERATES = [24, 30, 60]
    
    # API 限制設定
    API_RATE_LIMITS = {
        'imagen_requests_per_minute': 60,
        'imagen_images_per_request': 4,  # Imagen 4 每次請求最多 4 張
        'veo_requests_per_minute': 10,
        'gemini_requests_per_minute': 100
    }
    
    @staticmethod
    def validate_api_keys():
        """驗證必要的 API 金鑰和配置是否已設定"""
        missing_configs = []
        warnings = []
        
        # 檢查 Google Cloud 配置
        if not Config.GOOGLE_CLOUD_PROJECT:
            missing_configs.append('GOOGLE_CLOUD_PROJECT')
        
        if not Config.GOOGLE_APPLICATION_CREDENTIALS:
            warnings.append('GOOGLE_APPLICATION_CREDENTIALS 未設定，將嘗試使用預設認證')
        
        # 檢查 Gemini API Key（可選，可以使用 Vertex AI）
        if not Config.GEMINI_API_KEY:
            warnings.append('GEMINI_API_KEY 未設定，將使用 Vertex AI 的 Gemini')
        
        if missing_configs:
            raise ValueError(f"缺少必要的環境變數: {', '.join(missing_configs)}")
        
        if warnings:
            print("⚠️ 警告:")
            for warning in warnings:
                print(f"  - {warning}")
        
        return True
    
    @staticmethod
    def get_model_info():
        """獲取模型資訊"""
        return {
            'imagen': Config.IMAGE_GEN_MODEL,
            'veo': Config.VIDEO_GEN_MODEL,
            'gemini': Config.GEMINI_MODEL,
            'api_limits': Config.API_RATE_LIMITS
        }
    
    @staticmethod
    def get_supported_parameters():
        """獲取所有支援的參數"""
        return {
            'image': {
                'sizes': Config.SUPPORTED_IMAGE_SIZES,
                'qualities': Config.SUPPORTED_IMAGE_QUALITIES,
                'max_count': Config.MAX_IMAGE_COUNT
            },
            'video': {
                'resolutions': Config.SUPPORTED_VIDEO_RESOLUTIONS,
                'durations': Config.SUPPORTED_VIDEO_DURATIONS,
                'framerates': Config.SUPPORTED_VIDEO_FRAMERATES,
                'max_count': Config.MAX_VIDEO_COUNT
            },
            'limits': {
                'max_prompt_length': Config.MAX_PROMPT_LENGTH,
                'max_upload_size': Config.MAX_UPLOAD_SIZE
            }
        } 