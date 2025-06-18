from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

# 載入環境變數（使用當前目錄的 .env 檔案）
try:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    env_loaded = load_dotenv(env_path)
    print(f"🔄 環境變數載入結果: {env_loaded}")
    print(f"📁 .env 文件路徑: {env_path}")
    print(f"🔍 GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")

    # 如果載入失敗，嘗試使用 find_dotenv
    if not env_loaded:
        print("⚠️ 使用絕對路徑載入失敗，嘗試 find_dotenv...")
        env_path = find_dotenv()
        env_loaded = load_dotenv(env_path)
        print(f"🔄 find_dotenv 結果: {env_loaded}")
        print(f"📁 find_dotenv 路徑: {env_path}")
        print(f"🔍 GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
        
    # 如果還是失敗，手動設定（請替換為您的實際值）
    if not os.environ.get('GOOGLE_CLOUD_PROJECT'):
        print("⚠️ 環境變數載入失敗，使用預設設定...")
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-google-cloud-project'
        os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
        os.environ['GEMINI_API_KEY'] = 'your-gemini-api-key'
        # 確保各模型使用 .env 中的設定，如果沒有則使用預設值
        if not os.environ.get('GEMINI_MODEL'):
            os.environ['GEMINI_MODEL'] = 'gemini-2.0-flash'
        if not os.environ.get('IMAGE_GEN_MODEL'):
            os.environ['IMAGE_GEN_MODEL'] = 'imagen-4.0-fast-generate-preview-06-06'
        if not os.environ.get('VIDEO_GEN_MODEL'):
            os.environ['VIDEO_GEN_MODEL'] = 'veo-3.0-generate-preview'
        # Google搜尋設定 (可選)
        if not os.environ.get('GOOGLE_SEARCH_API_KEY'):
            os.environ['GOOGLE_SEARCH_API_KEY'] = ''
        if not os.environ.get('GOOGLE_SEARCH_ENGINE_ID'):
            os.environ['GOOGLE_SEARCH_ENGINE_ID'] = ''
        print("✅ 手動設定環境變數完成")
        
except Exception as e:
    print(f"❌ 環境變數載入異常: {e}")
    # 設定基本環境變數以確保應用程式能啟動
    # 設定預設的環境變數（請替換為您的實際值）
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-google-cloud-project'
    os.environ['GEMINI_API_KEY'] = 'your-gemini-api-key'
    # 確保各模型有正確的設定
    if not os.environ.get('GEMINI_MODEL'):
        os.environ['GEMINI_MODEL'] = 'gemini-2.0-flash'
    if not os.environ.get('IMAGE_GEN_MODEL'):
        os.environ['IMAGE_GEN_MODEL'] = 'imagen-4.0-fast-generate-preview-06-06'
    if not os.environ.get('VIDEO_GEN_MODEL'):
        os.environ['VIDEO_GEN_MODEL'] = 'veo-3.0-generate-preview'

# 匯入自定義模組
from config.config import Config
from llm_services.gemini_service import GeminiService
from llm_services.openai_llm_service import OpenAILLMService
from image_services.imagen_service import ImagenService
from image_services.openai_service import OpenAIImageService
from image_services.google_search_service import GoogleImageSearchService
from services.veo_service import VeoService
from video_services.openai_video_service import OpenAIVideoService
from services.simple_admin_service import SimpleAdminService
from services.simple_stats_service import SimpleStatsService
from prompt_optimizer.prompt_analyzer import PromptAnalyzer
from pricing_calculator.price_calculator import PriceCalculator

# 建立 Flask 應用程式
app = Flask(__name__)
app.config.from_object(Config)

# 會話配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# 啟用 CORS
CORS(app)

# 除錯資訊：確認 GEMINI_MODEL 設定
print(f"🔍 除錯資訊 - GEMINI_MODEL 環境變數: {os.environ.get('GEMINI_MODEL')}")
print(f"🔍 除錯資訊 - app.config['GEMINI_MODEL']: {app.config['GEMINI_MODEL']}")

# 初始化服務
gemini_service = GeminiService(
    api_key=app.config['GEMINI_API_KEY'],
    model_name=app.config['GEMINI_MODEL']
)
# 初始化 OpenAI LLM 服務用於 prompt 優化
openai_llm_service = OpenAILLMService()
# 檢查 Google Cloud 專案設定
google_cloud_project = app.config.get('GOOGLE_CLOUD_PROJECT')
if google_cloud_project:
    print(f"✅ Google Cloud 專案 ID: {google_cloud_project}")
    use_imagen_mock = False
else:
    print("⚠️ 未設定 Google Cloud 專案 ID")
    print("🔧 使用 Imagen 模擬模式")
    use_imagen_mock = True

imagen_service = ImagenService(
    project_id=google_cloud_project,
    location=app.config.get('GOOGLE_CLOUD_LOCATION', 'us-central1'),
    use_mock=use_imagen_mock,
    model_name=app.config.get('IMAGE_GEN_MODEL')
)
openai_image_service = OpenAIImageService()
image_search_service = GoogleImageSearchService()
veo_service = VeoService(
    project_id=google_cloud_project,
    location=app.config.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
)
openai_video_service = OpenAIVideoService()
prompt_analyzer = PromptAnalyzer(openai_llm_service)
price_calculator = PriceCalculator()

# 初始化管理服務
admin_service = SimpleAdminService()
stats_service = SimpleStatsService()

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

# 管理功能路由
@app.route('/admin/login')
def admin_login():
    """管理員登入頁面"""
    if admin_service.is_admin_authenticated():
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    """管理區首頁"""
    if not admin_service.is_admin_authenticated():
        return redirect(url_for('admin_login'))
    
    admin_username = admin_service.get_admin_username()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('admin.html', 
                         admin_username=admin_username,
                         current_time=current_time)

# 管理 API 路由
@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    """管理員登入 API"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': '請提供帳戶和密碼'}), 400
    
    username = data['username'].strip()
    password = data['password']
    
    if not username or not password:
        return jsonify({'success': False, 'message': '帳戶和密碼不能為空'}), 400
    
    # 執行管理員認證
    result = admin_service.authenticate_admin(username, password)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 401

@app.route('/api/admin/logout')
def api_admin_logout():
    """管理員登出 API"""
    admin_service.logout_admin()
    return redirect(url_for('index'))

@app.route('/api/admin/statistics', methods=['GET'])
def api_admin_statistics():
    """獲取統計資訊 API（管理員專用）"""
    if not admin_service.is_admin_authenticated():
        return jsonify({'error': '需要管理員權限'}), 403
    
    stats = stats_service.get_statistics()
    return jsonify({'success': True, 'statistics': stats})

@app.route('/api/admin/recent-generations', methods=['GET'])
def api_admin_recent_generations():
    """獲取最近生成記錄 API（管理員專用）"""
    if not admin_service.is_admin_authenticated():
        return jsonify({'error': '需要管理員權限'}), 403
    
    limit = request.args.get('limit', 20, type=int)
    generations = stats_service.get_recent_generations(limit)
    return jsonify({'success': True, 'generations': generations})

@app.route('/api/image/optimize-prompt', methods=['POST'])
def optimize_image_prompt():
    """優化圖像生成的 prompt - 提供六種風格化建議"""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': '請提供有效的 prompt'}), 400
    
    prompt = data['prompt'].strip()
    if not prompt:
        return jsonify({'error': 'Prompt 不能為空'}), 400
    
    if len(prompt) > app.config['MAX_PROMPT_LENGTH']:
        return jsonify({'error': f'Prompt 長度不能超過 {app.config["MAX_PROMPT_LENGTH"]} 字元'}), 400
    
    try:
        # 使用 OpenAI LLM 服務生成六種不同風格的優化版本
        optimization_prompt = f"""
請為以下圖像生成 prompt 提供六種不同風格的優化版本：

原始 prompt：
{prompt}

請提供六種風格優化版本，每個版本都要保持原意，但應用不同的視覺風格：

1. 自然清新風 (Natural & Clean)：提升整體亮度與對比度，強化綠色與藍色的飽和度，柔化膚色、減少雜訊，適合風景照或日光人像
2. 電影感風格 (Cinematic Look)：壓低高光、拉深陰影，添加冷色調或橙青對比色分級，加入黑邊或 21:9 膠片比例遮幅，適合街景、情感人像、夜景
3. 復古懷舊風 (Vintage/Retro)：降低飽和度，添加黃色或綠色色調，模擬底片顆粒與雜訊，使用色調曲線模擬舊照片褪色感，適合文青風或老街場景
4. 高質感商業風 (High-End Editorial)：精準膚色校正，銳化重點細節（如眼睛、配飾），背景去雜，控制景深或加柔焦，適合人像特寫或商品攝影
5. 黑白極簡風 (Monochrome Minimalism)：轉為黑白灰階，加強光影對比與形狀線條表現，清除雜點與背景干擾，適合強調情緒或幾何結構
6. 夢幻光影風 (Soft Dreamy)：加入柔焦/光暈效果，使用粉色、紫色、淡藍作色調分級，降低清晰度，強調柔和過渡，適合婚紗、日落、森林漫步類主題

請按以下格式返回，每個版本用 "---" 分隔：

版本1：[自然清新風格的優化 prompt]
---
版本2：[電影感風格的優化 prompt]
---
版本3：[復古懷舊風格的優化 prompt]
---
版本4：[高質感商業風格的優化 prompt]
---
版本5：[黑白極簡風格的優化 prompt]
---
版本6：[夢幻光影風格的優化 prompt]
"""
        
        response = openai_llm_service.generate_content(optimization_prompt)
        
        if response and 'content' in response:
            content = response['content'].strip()
            
            # 解析六個版本
            versions = content.split('---')
            optimizations = []
            
            for i, version in enumerate(versions):
                version = version.strip()
                # 移除版本標籤（如 "版本1："）
                if '：' in version:
                    version = version.split('：', 1)[1].strip()
                elif ':' in version:
                    version = version.split(':', 1)[1].strip()
                
                if version:
                    optimizations.append(version)
            
            # 確保有六個版本
            style_names = [
                "自然清新風 (Natural & Clean)",
                "電影感風格 (Cinematic Look)", 
                "復古懷舊風 (Vintage/Retro)",
                "高質感商業風 (High-End Editorial)",
                "黑白極簡風 (Monochrome Minimalism)",
                "夢幻光影風 (Soft Dreamy)"
            ]
            
            while len(optimizations) < 6:
                optimizations.append(prompt)  # 如果解析失敗，使用原始 prompt
            
            return jsonify({
                'success': True,
                'original_prompt': prompt,
                'optimizations': optimizations[:6],  # 只取前六個
                'style_names': style_names
            })
        else:
            return jsonify({'error': '優化服務暫時不可用'}), 500
            
    except Exception as e:
        print(f"❌ Prompt 優化失敗: {e}")
        return jsonify({'error': f'優化失敗: {str(e)}'}), 500

@app.route('/api/image/calculate-price', methods=['POST'])
def calculate_image_price():
    """價格計算功能已停用"""
    return jsonify({'error': '價格計算功能已停用'}), 404

@app.route('/api/image/translate-prompt', methods=['POST'])
def translate_prompt():
    """將中文 prompt 翻譯為適合圖像生成的英文"""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': '請提供有效的 prompt'}), 400
    
    prompt = data['prompt'].strip()
    if not prompt:
        return jsonify({'error': 'Prompt 不能為空'}), 400
    
    try:
        # 使用 OpenAI LLM 服務進行翻譯和優化
        translation_prompt = f"""
請將以下中文圖像描述翻譯成最適合 AI 圖像生成的英文 prompt。要求：

1. 保持原意的同時，使用 AI 圖像生成模型容易理解的詞彙
2. 添加適當的攝影術語和藝術描述詞
3. 結構清晰，描述具體
4. 適合 Imagen、DALL-E 等模型使用
5. 只返回翻譯後的英文 prompt，不要其他說明

原始中文描述：
{prompt}

請直接返回優化後的英文 prompt：
"""
        
        response = openai_llm_service.generate_content(translation_prompt)
        
        if response and 'content' in response:
            translated_prompt = response['content'].strip()
            
            return jsonify({
                'success': True,
                'original_prompt': prompt,
                'translated_prompt': translated_prompt,
                'language': 'en'
            })
        else:
            return jsonify({'error': '翻譯服務暫時不可用'}), 500
            
    except Exception as e:
        print(f"❌ Prompt 翻譯失敗: {e}")
        return jsonify({'error': f'翻譯失敗: {str(e)}'}), 500

@app.route('/api/image/generate', methods=['POST'])
def generate_image():
    """生成圖像"""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': '請提供有效的 prompt'}), 400
    
    prompt = data['prompt'].strip()
    if not prompt:
        return jsonify({'error': 'Prompt 不能為空'}), 400
    
    # 驗證參數
    params = {
        'prompt': prompt,
        'count': data.get('count', 1),
        'quality': data.get('quality', 'standard'),
        'size': data.get('size', '1024x1024'),
        'style': data.get('style', 'vivid')  # 新增 OpenAI DALL-E 風格參數
    }
    
    # 獲取模型選擇（預設為 DALL-E）
    model_choice = data.get('model', 'dall-e-3').lower()
    
    # 添加調試資訊
    print(f"🔍 收到的生成請求參數:")
    print(f"   模型: {model_choice}")
    print(f"   Prompt: {prompt[:100]}...")
    print(f"   數量: {params['count']}")
    print(f"   品質: {params['quality']}")
    print(f"   尺寸: {params['size']}")
    print(f"   風格: {params['style']}")
    print(f"   原始請求數據: {data}")
    
    # 驗證數量
    if params['count'] < 1 or params['count'] > app.config['MAX_IMAGE_COUNT']:
        return jsonify({'error': f'圖像數量必須在 1-{app.config["MAX_IMAGE_COUNT"]} 之間'}), 400
    
    # 記錄生成開始時間
    start_time = time.time()
    
    try:
        # 根據模型選擇使用不同的服務
        if model_choice == 'dall-e-3' or model_choice == 'openai':
            # 使用 OpenAI DALL-E 服務生成圖像
            result = openai_image_service.generate_images(params)
        else:
            # 使用 Imagen 服務生成圖像
            result = imagen_service.generate_images(params)
        
        # 計算生成時間
        generation_time = time.time() - start_time
        model_display_name = 'DALL-E 3' if model_choice in ['dall-e-3', 'openai'] else 'Imagen 4'
        
        # 記錄生成結果
        if result.get('success'):
            file_count = len(result.get('images', []))
            stats_service.record_generation('image', prompt, 'success', model_display_name, generation_time, file_count)
        else:
            stats_service.record_generation('image', prompt, 'failed', model_display_name, generation_time, 0)
        
        print(f"✅ 圖像生成完成，耗時: {generation_time:.2f} 秒")
        
        return jsonify(result)
        
    except Exception as e:
        generation_time = time.time() - start_time
        error_message = str(e)
        model_display_name = 'DALL-E 3' if model_choice in ['dall-e-3', 'openai'] else 'Imagen 4'
        
        # 記錄失敗的生成
        stats_service.record_generation('image', prompt, 'failed', model_display_name, generation_time, 0)
        
        print(f"❌ 圖像生成失敗，耗時: {generation_time:.2f} 秒，錯誤: {error_message}")
        
        return jsonify({'error': f'生成失敗: {error_message}'}), 500

@app.route('/api/image/search', methods=['POST'])
def search_images():
    """搜尋圖片"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': '請提供搜尋關鍵字'}), 400
    
    query = data['query'].strip()
    if not query:
        return jsonify({'error': '搜尋關鍵字不能為空'}), 400
    
    if len(query) > 100:
        return jsonify({'error': '搜尋關鍵字長度不能超過 100 字元'}), 400
    
    try:
        # 獲取搜尋參數
        page = data.get('page', 1)
        per_page = data.get('per_page', 12)
        orientation = data.get('orientation', 'any')
        size = data.get('size', 'medium')
        image_type = data.get('type', 'photo')
        
        # 驗證參數
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 30:
            per_page = 12
        
        # 準備搜尋參數
        search_params = {
            'orientation': orientation,
            'size': size,
            'type': image_type
        }
        
        # 使用Google搜尋
        result = image_search_service.search_images(
            query=query,
            page=page,
            per_page=per_page,
            **search_params
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ 圖片搜尋失敗: {e}")
        return jsonify({
            'success': False,
            'error': f'搜尋失敗: {str(e)}',
            'message': '圖片搜尋服務發生錯誤'
        }), 500

@app.route('/api/image/download', methods=['POST'])
def download_image():
    """下載圖片"""
    data = request.get_json()
    
    if not data or 'image_url' not in data:
        return jsonify({'error': '請提供圖片 URL'}), 400
    
    image_url = data['image_url'].strip()
    if not image_url:
        return jsonify({'error': '圖片 URL 不能為空'}), 400
    
    try:
        # 獲取下載參數
        filename = data.get('filename', None)
        
        # 使用Google圖片搜尋服務下載圖片
        result = image_search_service.download_image(
            image_url=image_url,
            filename=filename
        )
        
        if result['success']:
            print(f"✅ 成功下載Google圖片: {result.get('filename', 'unknown')}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ 圖片下載失敗: {e}")
        return jsonify({
            'success': False,
            'error': f'下載失敗: {str(e)}',
            'message': '圖片下載發生錯誤'
        }), 500

@app.route('/api/image/search-options', methods=['GET'])
def get_search_options():
    """獲取圖片搜尋選項"""
    try:
        return jsonify({
            'success': True,
            'platform': 'google',
            'options': image_search_service.get_search_options()
        })
    except Exception as e:
        print(f"❌ 獲取搜尋選項失敗: {e}")
        return jsonify({
            'success': False,
            'error': f'獲取選項失敗: {str(e)}'
        }), 500

@app.route('/api/image/model-options', methods=['GET'])
def get_image_model_options():
    """獲取圖像生成模型選項"""
    return jsonify({
        'models': [
            {
                'id': 'dall-e-3',
                'name': 'DALL-E 3',
                'description': 'OpenAI 最新圖像生成模型，高品質創意圖像',
                'provider': 'OpenAI',
                'max_images': 4,
                'supported_sizes': ['1024x1024', '1024x1792', '1792x1024'],
                'supported_qualities': ['standard', 'hd'],
                'supported_styles': ['vivid', 'natural'],
                'default': True
            },
            {
                'id': 'imagen',
                'name': 'Imagen 4',
                'description': 'Google 高品質圖像生成模型',
                'provider': 'Google',
                'max_images': 4,
                'supported_sizes': ['1024x1024', '1152x896', '896x1152'],
                'supported_qualities': ['fast', 'standard'],
                'supported_styles': [],
                'default': False
            }
        ]
    })

@app.route('/api/video/model-options', methods=['GET'])
def get_video_model_options():
    """獲取影片生成模型選項"""
    return jsonify({
        'models': [
            {
                'id': 'openai',
                'name': 'OpenAI Video',
                'description': 'OpenAI 影片生成模型（實驗性）',
                'provider': 'OpenAI',
                'max_duration': 10,
                'supported_aspect_ratios': ['16:9', '9:16'],
                'supported_durations': [3, 4, 5, 6, 7, 8, 9, 10],
                'default': True
            },
            {
                'id': 'veo',
                'name': 'Veo 3.0',
                'description': 'Google Veo 高品質影片生成模型',
                'provider': 'Google',
                'max_duration': 8,
                'supported_aspect_ratios': ['16:9', '9:16'],
                'supported_durations': [5, 6, 7, 8],
                'default': False
            }
        ]
    })

@app.route('/api/video/optimize-prompt', methods=['POST'])
def optimize_video_prompt():
    """優化影片生成的 prompt - 提供六種風格化建議"""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': '請提供有效的 prompt'}), 400
    
    prompt = data['prompt'].strip()
    if not prompt:
        return jsonify({'error': 'Prompt 不能為空'}), 400
    
    if len(prompt) > app.config['MAX_PROMPT_LENGTH']:
        return jsonify({'error': f'Prompt 長度不能超過 {app.config["MAX_PROMPT_LENGTH"]} 字元'}), 400
    
    try:
        # 使用 OpenAI LLM 服務生成六種不同風格的影片優化版本
        optimization_prompt = f"""
請為以下影片生成 prompt 提供六種不同風格的優化版本：

原始 prompt：
{prompt}

請提供六種風格優化版本，每個版本都要保持原意，但應用不同的視覺風格和動態效果：

1. 自然清新風 (Natural & Clean)：提升整體亮度與對比度，強化自然色彩，清晰流暢的動作，適合戶外場景或生活記錄
2. 電影感風格 (Cinematic Look)：電影級攝影技巧，戲劇性燈光，深度景深，慢動作或特殊鏡頭運動，適合敘事性影片
3. 復古懷舊風 (Vintage/Retro)：復古色調和濾鏡效果，模擬舊時代影片質感，添加顆粒感和色彩偏移，適合懷舊主題
4. 高質感商業風 (High-End Editorial)：專業級色彩校正，精緻的光影處理，商業廣告級別的視覺品質，適合產品展示或品牌影片
5. 黑白極簡風 (Monochrome Minimalism)：黑白灰階處理，強調光影對比和構圖線條，極簡主義美學，適合藝術表達
6. 夢幻光影風 (Soft Dreamy)：柔和的光暈效果，夢幻般的色彩分級，輕柔的動作過渡，適合浪漫或幻想主題

請按以下格式返回，每個版本用 "---" 分隔：

版本1：[自然清新風格的優化 prompt]
---
版本2：[電影感風格的優化 prompt]
---
版本3：[復古懷舊風格的優化 prompt]
---
版本4：[高質感商業風格的優化 prompt]
---
版本5：[黑白極簡風格的優化 prompt]
---
版本6：[夢幻光影風格的優化 prompt]
"""
        
        response = openai_llm_service.generate_content(optimization_prompt)
        
        if response and 'content' in response:
            content = response['content'].strip()
            
            # 解析六個版本
            versions = content.split('---')
            optimizations = []
            
            for i, version in enumerate(versions):
                version = version.strip()
                # 移除版本標籤（如 "版本1："）
                if '：' in version:
                    version = version.split('：', 1)[1].strip()
                elif ':' in version:
                    version = version.split(':', 1)[1].strip()
                
                if version:
                    optimizations.append(version)
            
            # 確保有六個版本
            style_names = [
                "自然清新風 (Natural & Clean)",
                "電影感風格 (Cinematic Look)", 
                "復古懷舊風 (Vintage/Retro)",
                "高質感商業風 (High-End Editorial)",
                "黑白極簡風 (Monochrome Minimalism)",
                "夢幻光影風 (Soft Dreamy)"
            ]
            
            while len(optimizations) < 6:
                optimizations.append(prompt)  # 如果解析失敗，使用原始 prompt
            
            return jsonify({
                'success': True,
                'original_prompt': prompt,
                'optimizations': optimizations[:6],  # 只取前六個
                'style_names': style_names
            })
        else:
            return jsonify({'error': '優化服務暫時不可用'}), 500
            
    except Exception as e:
        print(f"❌ 影片 Prompt 優化失敗: {e}")
        return jsonify({'error': f'優化失敗: {str(e)}'}), 500

@app.route('/api/video/translate-prompt', methods=['POST'])
def translate_video_prompt():
    """將中文影片 prompt 翻譯為適合影片生成的英文"""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': '請提供有效的 prompt'}), 400
    
    prompt = data['prompt'].strip()
    if not prompt:
        return jsonify({'error': 'Prompt 不能為空'}), 400
    
    try:
        # 使用 OpenAI LLM 服務進行翻譯和優化
        translation_prompt = f"""
請將以下中文影片描述翻譯成最適合 AI 影片生成的英文 prompt。要求：

1. 保持原意的同時，使用 AI 影片生成模型容易理解的詞彙
2. 添加適當的攝影術語和動態描述詞
3. 強調動作、運動和時間流程
4. 適合 Veo、Runway 等影片生成模型使用
5. 只返回翻譯後的英文 prompt，不要其他說明

原始中文描述：
{prompt}

請直接返回優化後的英文 prompt：
"""
        
        response = openai_llm_service.generate_content(translation_prompt)
        
        if response and 'content' in response:
            translated_prompt = response['content'].strip()
            
            return jsonify({
                'success': True,
                'original_prompt': prompt,
                'translated_prompt': translated_prompt,
                'language': 'en'
            })
        else:
            return jsonify({'error': '翻譯服務暫時不可用'}), 500
            
    except Exception as e:
        print(f"❌ 影片 Prompt 翻譯失敗: {e}")
        return jsonify({'error': f'翻譯失敗: {str(e)}'}), 500

@app.route('/api/video/calculate-price', methods=['POST'])
def calculate_video_price():
    """價格計算功能已停用"""
    return jsonify({'error': '價格計算功能已停用'}), 404

@app.route('/api/video/generate', methods=['POST'])
def generate_video():
    """生成影片"""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': '請提供有效的 prompt'}), 400
    
    prompt = data['prompt'].strip()
    if not prompt:
        return jsonify({'error': 'Prompt 不能為空'}), 400
    
    # 驗證參數
    params = {
        'prompt': prompt,
        'aspectRatio': data.get('aspectRatio', '16:9'),
        'duration': data.get('duration', 5),
        'personGeneration': data.get('personGeneration', 'allow_adult')
    }
    
    # 獲取模型選擇（預設為 Veo）
    model_choice = data.get('model', 'veo').lower()
    
    # 驗證參數
    if params['aspectRatio'] not in ['16:9', '9:16']:
        return jsonify({'error': '無效的影片比例設定'}), 400
    
    if params['duration'] not in [5, 6, 7, 8]:
        return jsonify({'error': '無效的影片長度設定 (支援5-8秒)'}), 400
    
    # 記錄生成開始時間
    start_time = time.time()
    
    try:
        # 根據模型選擇使用不同的服務
        if model_choice == 'openai':
            # 使用 OpenAI 影片服務生成影片
            result = openai_video_service.generate_videos(params)
        else:
            # 使用 Veo 服務生成影片
            result = veo_service.generate_videos(params)
        
        # 計算生成時間
        generation_time = time.time() - start_time
        model_display_name = 'OpenAI Video' if model_choice == 'openai' else 'Veo 3.0'
        
        # 記錄生成結果
        if result.get('success'):
            file_count = len(result.get('videos', []))
            stats_service.record_generation('video', prompt, 'success', model_display_name, generation_time, file_count)
        else:
            stats_service.record_generation('video', prompt, 'failed', model_display_name, generation_time, 0)
        
        print(f"✅ 影片生成完成，耗時: {generation_time:.2f} 秒")
        
        return jsonify(result)
        
    except Exception as e:
        generation_time = time.time() - start_time
        error_message = str(e)
        model_display_name = 'OpenAI Video' if model_choice == 'openai' else 'Veo 3.0'
        
        # 記錄失敗的生成
        stats_service.record_generation('video', prompt, 'failed', model_display_name, generation_time, 0)
        
        print(f"❌ 影片生成失敗，耗時: {generation_time:.2f} 秒，錯誤: {error_message}")
        
        return jsonify({'error': f'生成失敗: {error_message}'}), 500

@app.route('/generated/<path:filename>')
def serve_generated_file(filename):
    """提供生成的檔案"""
    try:
        return send_file(os.path.join('generated', filename))
    except FileNotFoundError:
        return jsonify({'error': '檔案不存在'}), 404

@app.route('/api/prompt-tips', methods=['GET'])
def get_prompt_tips():
    """獲取 prompt 撰寫建議"""
    content_type = request.args.get('type', 'image')
    
    if content_type == 'image':
        tips = {
            'characters': [
                '年輕女性，長髮飄逸',
                '中年男性，友善微笑',
                '可愛小孩，天真表情',
                '老年人，慈祥面容'
            ],
            'backgrounds': [
                '自然風景，山川河流',
                '城市街景，繁華夜景',
                '室內場景，溫馨家居',
                '海邊夕陽，浪漫氛圍'
            ],
            'photography': [
                '淺景深，背景虛化',
                '廣角鏡頭，全景拍攝',
                '微距攝影，細節突出',
                '逆光拍攝，輪廓清晰'
            ],
            'styles': [
                '寫實風格，細節豐富',
                '藝術風格，創意表現',
                '復古風格，懷舊色調',
                '未來風格，科技感強'
            ]
        }
    else:
        tips = {
            'actions': [
                '人物走路，自然步態',
                '揮手動作，友善招呼',
                '跳躍動作，活力四射',
                '舞蹈動作，優雅流暢'
            ],
            'camera_movements': [
                '鏡頭推進，突出主體',
                '鏡頭拉遠，展現全景',
                '左右搖擺，跟隨動作',
                '上下俯仰，變換視角'
            ],
            'environments': [
                '自然環境，風吹草動',
                '城市環境，車水馬龍',
                '室內環境，光影變化',
                '水下環境，波光粼粼'
            ],
            'effects': [
                '慢動作效果，細膩展現',
                '快動作效果，節奏感強',
                '景深變化，焦點轉移',
                '色調變化，情緒表達'
            ]
        }
    
    return jsonify({
        'type': content_type,
        'tips': tips
    })

if __name__ == '__main__':
    # 建立必要的目錄
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('generated', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5001) 