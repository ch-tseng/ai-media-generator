# AI Dataset Generator

一個可透過OpenAI與Google服務來生成影像與影片的生成工具。
[![IMAGE ALT TEXT](https://github.com/ch-tseng/ai-media-generator/blob/3a4a6722d4926725420ce894fafe04e503ab5cf4/data/youtube-pic.png)](https://www.youtube.com/watch?v=76qn5nVtHhA "影片生成示範")

---

## 目錄

1. [專案簡介](#專案簡介)
2. [專案展示](#專案展示)
3. [Logo 更換說明](#logo-更換說明)
4. [安裝說明](#安裝說明)
5. [API Key 及 JSON Key 取得教學](#api-key-及-json-key-取得教學)
6. [管理區（Admin）登入與使用](#管理區admin登入與使用)
7. [影像搜尋操作教學](#影像搜尋操作教學)
8. [常見問題與故障排除](#常見問題與故障排除)
9. [貢獻方式](#貢獻方式)
10. [授權](#授權)
11. [聯絡方式](#聯絡方式)

---

## 專案簡介

- **多模態 AI 生成**：支援文字、圖片、影片的 AI 生成。
- **多模型支援**：OpenAI DALL-E 3、Google Imagen 4.0、Google Veo 3.0、Gemini 2.5 Flash。
- **Web 介面**：開箱即用，無需登入認證。
- **管理功能**：簡易管理員系統，支援統計與生成記錄查詢。
- **批量生成、風格多樣、格式多元**。

---

## 專案展示

### Logo 示意

static/images/logo.png
> 您可將 `logo.png` 替換為自己的品牌 Logo，讓系統更具個人化風格。

---

## Logo 更換說明

- 請將您的 logo 圖片命名為 `logo.png`，並放置於專案根目錄或 `static/` 目錄下（依前端引用路徑）。
- 建議尺寸：256x256 或 512x512，PNG 格式。

---

## 安裝說明

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd AI-Dataset-Generator
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定環境變數**
   - 請參考 `.env.example` 或下方 [API Key 及 JSON Key 取得教學](#api-key-及-json-key-取得教學)。
   - 建議複製 `.env.example` 為 `.env` 並填入對應資訊。

4. **安裝 FFmpeg（影片生成功能建議安裝）**
   - Windows: `choco install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt install ffmpeg`

5. **啟動應用程式**
   ```bash
   python app_ai_generate.py
   ```
   - 預設網址：http://localhost:5001

---

## API Key 及 JSON Key 取得教學

### 1. Google Cloud API 金鑰與服務帳戶 JSON

- **Google Cloud Console**：[https://console.cloud.google.com/](https://console.cloud.google.com/)
- 建立專案 → 啟用 Vertex AI、Custom Search API 等服務
- 建立服務帳戶，下載 JSON 憑證，並於 `.env` 設定 `GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json`
- 取得 Project ID，填入 `GOOGLE_CLOUD_PROJECT`

### 2. OpenAI API Key

- [OpenAI 會員中心](https://platform.openai.com/api-keys)
- 產生 API Key，填入 `.env` 的 `OPENAI_API_KEY`

### 3. Gemini API Key

- [Google AI Studio](https://aistudio.google.com/app/apikey)
- 產生 Gemini API Key，填入 `.env` 的 `GEMINI_API_KEY`

### 4. Google Custom Search API Key（圖片搜尋）

- [Google Custom Search API](https://developers.google.com/custom-search/v1/overview)
- 建立搜尋引擎，取得 API Key 與 Search Engine ID，填入 `.env`

---

## 管理區（Admin）登入與使用

- 點擊首頁右上角「⚙️ 管理區」進入管理後台。
- 預設帳號密碼：
  - 帳號：admin
  - 密碼：admin123
- 管理區功能：
  - 查看系統統計、生成記錄
  - 用戶管理（啟用/停用）
  - 下載生成的圖片/影片
- **建議：** 正式部署請修改 `.env` 內的管理員帳號密碼。
[![IMAGE ALT TEXT](https://github.com/ch-tseng/ai-media-generator/blob/6f02fcb3e822fe2c918327963330e15014bb888b/data/manage_admin.png)]
---

## 影像生成與影片生成操作教學

### 影像生成

1. 輸入圖片描述（Prompt）
2. 選擇圖片比例（1:1、16:9、9:16、4:3、3:4）
3. 選擇藝術風格
4. 設定人物生成選項
5. 點擊「生成圖片」即可

### 影片生成

1. 輸入影片描述
2. 選擇影片比例（16:9 或 9:16）
3. 選擇影片長度（5-8 秒）
4. 選擇影片風格
5. 設定人物生成選項
6. 點擊「生成影片」即可

---

## 影像搜尋操作教學

1. 輸入搜尋關鍵字（如：風景、動物）
2. 選擇搜尋平台（Google 圖片搜尋等）
3. 設定篩選條件（方向、尺寸、排序）
4. 瀏覽搜尋結果，點擊圖片可預覽或下載
5. 支援單張或批量下載

---

## 常見問題與故障排除

- **API Key 設定錯誤**：請確認 `.env` 內容正確，無多餘空格。
- **影片無法播放**：請確認已安裝 FFmpeg，或嘗試不同播放器。
- **配額超限**：請參考 [Google Cloud 配額頁面](https://console.cloud.google.com/iam-admin/quotas) 申請提升。
- **資料庫鎖定**：請執行 `python init_database.py` 初始化資料庫。

---

## 貢獻方式

1. Fork 本專案
2. 建立功能分支
3. 提交 Pull Request
4. 歡迎報告錯誤、建議新功能、改善文件

---

## 授權

本專案採用 MIT 授權條款，歡迎自由使用與修改。

---

## 聯絡方式

- [GitHub Issues](https://github.com/your-username/ai-media-generator/issues)
- [Discussions](https://github.com/your-username/ai-media-generator/discussions)

---

⭐ 如果本專案對您有幫助，請給我們一個 Star！

---

### 備註

- 操作示範影片請見 `generated/20250618_120006.mp4`
- Logo 可自訂，請參考 [Logo 更換說明](#logo-更換說明)

## 功能特色

### 🤖 多模態 AI 生成
- **文字生成**: 使用 Google Gemini 2.5 Flash 模型
- **圖片生成**: 
  - **OpenAI DALL-E 3** (預設) - 高品質創意圖像，支援多種風格
  - **Google Imagen 4.0** - Google 的圖像生成模型
  - 智能模型切換，支援不同尺寸和品質選項
- **圖片搜尋**: 支援 Google 圖片搜尋，提供豐富的圖片資源
- **影片生成**: 
  - **OpenAI Video** (實驗性) - 支援 3-10 秒影片生成
  - **Google Veo 3.0** - 高品質影片生成，支援 5-8 秒
  - 自動配額管理和優雅降級

### 🔐 簡化使用
- **直接使用**: 開啟即用，無需登入認證
- **即時生成**: 快速生成各種AI內容
- **Web介面**: 直觀易用的網頁操作介面
- **管理功能**: 簡單的管理員系統，可查看使用統計和生成記錄

### 🎯 智能化功能
- **自動提示詞優化**: 智能增強用戶輸入的提示詞
- **批量生成**: 支援一次生成多個內容
- **多種風格**: 支援不同的藝術風格和影片風格
- **格式多樣**: 支援多種輸出格式和解析度

### 🔧 技術特點
- **模組化設計**: 每個 AI 服務獨立封裝，便於維護和擴展
- **錯誤處理**: 完善的錯誤處理和日誌記錄
- **配置靈活**: 支援多種配置方式
- **Web 介面**: 直觀的網頁操作介面
- **配額管理**: 智能配額監控和自動模型切換
- **優雅降級**: API 限制時自動切換到備用方案

## 系統要求

- Python 3.8+
- Google API 金鑰
- Google Cloud 專案 (用於 Imagen 和 Veo 服務)
- FFmpeg (可選，用於更好的影片生成)

## 技術規格

### Gemini 文字生成
- **模型**: gemini-2.5-flash-preview-05-20
- **最大輸出長度**: 8192 tokens
- **支援語言**: 多語言，包括繁體中文

### Imagen 圖片生成
- **模型**: imagen-4.0-fast-generate-preview-06-06
- **支援解析度**: 
  - 1:1 (1024x1024)
  - 9:16 (768x1344) 
  - 16:9 (1344x768)
  - 4:3 (1152x896)
  - 3:4 (896x1152)
- **輸出格式**: PNG
- **最大提示詞長度**: 2000 字元

### Google 圖片搜尋
- **API**: Google Custom Search API v1 (可選)
- **搜尋模式**: 
  - **API 模式**: 使用 Google Custom Search API，搜尋結果更穩定
  - **Web Scraping 模式**: 當無 API 金鑰時的備用方案
  - **示例模式**: 提供示例圖片作為最後備援
- **支援類型**: 
  - 照片、美工圖案、線條圖、人臉
- **支援尺寸**: 
  - 任何尺寸、大尺寸、中等尺寸、圖示
- **支援方向**: 
  - 任何方向、橫向、直向
- **搜尋功能**: 關鍵字搜尋、類型篩選、尺寸篩選、方向篩選
- **下載功能**: 單張下載、批量下載、自動檔案命名
- **支援格式**: JPG, PNG, WebP, GIF

### Veo 影片生成 (官方 Google GenAI SDK)
- **模型**: veo-2.0-generate-001
- **API**: Google GenAI SDK (官方)
- **支援解析度**: 
  - 16:9 (1280x720) - 720p HD
  - 9:16 (720x1280) - 垂直 HD
- **影片長度**: 5-8 秒
- **幀率**: 30 FPS
- **輸出格式**: MP4 (H.264)
- **最大提示詞長度**: 2000 字元
- **運行模式**: 
  - **真實 API 模式**: 使用 Google Veo 2.0 AI 模型生成真實影片
  - **模擬模式**: 當 API 不可用時自動切換，生成測試用 MP4 檔案
- **增強功能**: 支援自動提示詞增強和風格調整

### 影片生成技術細節
- **官方 SDK**: 使用 `google-genai` 套件進行 API 調用
- **長時間操作**: 支援輪詢機制，最多等待 2 小時
- **自動下載**: 從 Google Cloud Storage 自動下載生成的影片
- **錯誤處理**: 完整的 API 錯誤處理和詳細錯誤報告
- **進度追蹤**: 即時顯示生成進度和狀態訊息
- **模擬模式備援**: 
  - FFmpeg 整合：優先使用 FFmpeg 生成真實的 MP4 檔案
  - 手動 MP4 生成：當 FFmpeg 不可用時，使用手動 MP4 結構生成
  - 標準 MP4 格式：包含 ftyp、moov、mdat boxes
  - H.264 模擬：包含 SPS、PPS、IDR、P 和 B 幀模擬

## 專案結構

```
AI-Dataset-Generator/
├── app.py                 # Flask 主應用程式
├── config.ini            # 配置檔案
├── requirements.txt      # Python 依賴
├── README.md            # 專案說明
├── services/            # AI 服務模組
│   ├── gemini_service.py    # Gemini 文字生成服務
│   ├── imagen_service.py    # Imagen 圖片生成服務
│   └── veo_service.py       # Veo 影片生成服務 (官方 Google GenAI SDK)
├── image_services/      # 圖片相關服務
│   ├── imagen_service.py    # Imagen AI 圖片生成服務
│   └── google_search_service.py  # Google 圖片搜尋服務
├── libChatLLM/          # OpenLLM 整合
│   └── libChatLLM.ini      # OpenLLM API 配置
├── static/              # 靜態檔案
│   ├── css/
│   ├── js/
│   └── generated/          # 生成的檔案
├── templates/           # HTML 模板
└── generated/           # 影片檔案輸出目錄
```

## API 參考

### Gemini 服務
```python
from services.gemini_service import GeminiService

service = GeminiService(api_key="your_key")
result = service.generate_text({
    'prompt': '寫一個關於貓的故事',
    'max_output_tokens': 1000,
    'temperature': 0.7
})
```

### Imagen 服務
```python
from image_services.imagen_service import ImagenService

service = ImagenService(api_key="your_key", project_id="your_project")
result = service.generate_images({
    'prompt': '一隻可愛的小貓在花園裡玩耍',
    'aspectRatio': '1:1',
    'style': 'photographic'
})
```

### 圖片搜尋服務
```python
from image_services.google_search_service import GoogleImageSearchService

# 初始化 Google 圖片搜尋服務
service = GoogleImageSearchService()

# 搜尋圖片
result = service.search_images(
    query="風景",
    page=1,
    per_page=12,
    orientation="landscape",  # all, landscape, portrait, squarish
    size="regular",           # thumb, small, regular, full, raw
    order_by="relevant"       # relevant, latest, oldest, popular
)

# 檢查搜尋結果
if result['success']:
    print(f"找到 {result['total']} 張圖片")
    for image in result['results']:
        print(f"圖片: {image['description']}")
        print(f"作者: {image['author']['name']}")
        print(f"尺寸: {image['width']}x{image['height']}")
        
        # 下載圖片
        download_result = service.download_image(
            image_url=image['download_url'],
            filename=f"{image['id']}.jpg"
        )
        
        if download_result['success']:
            print(f"下載成功: {download_result['download_url']}")
else:
    print(f"搜尋失敗: {result['error']}")
```

### Veo 服務 (官方 Google GenAI SDK)
```python
from services.veo_service import VeoService

# 初始化服務 (會自動檢測是否可使用真實 API)
service = VeoService(api_key="your_google_api_key")

# 生成影片
result = service.generate_videos({
    'prompt': '一隻可愛的小貓在陽光花園裡玩耍',
    'aspectRatio': '16:9',
    'duration': 5,
    'personGeneration': 'disallow',
    'style': 'cinematic'
})

# 檢查結果
if result['success']:
    print(f"生成成功！模擬模式: {result.get('mock_mode', False)}")
    for video in result['videos']:
        print(f"影片檔案: {video['filename']}")
        print(f"檔案大小: {video['file_size']} bytes")
        if 'cloud_uri' in video:
            print(f"雲端 URI: {video['cloud_uri']}")
else:
    print(f"生成失敗: {result['error']}")
```

## 錯誤處理

應用程式包含完善的錯誤處理機制：

- **API 錯誤**: 自動重試和錯誤回報
- **檔案錯誤**: 檔案讀寫錯誤處理
- **網路錯誤**: 網路連接問題處理
- **配置錯誤**: 配置檔案驗證

## 成本估算

### Imagen 定價 (預估)
- 每張圖片約 $0.04 USD

### Veo 定價 (根據官方文檔)
- 5 秒影片: $2.50 USD
- 6-8 秒影片: $5.00 USD

### Gemini 定價
- 根據 token 使用量計費

## 故障排除

### 常見問題

1. **API 金鑰錯誤**
   - 檢查 `config.ini` 和 `libChatLLM/libChatLLM.ini` 中的 API 金鑰
   - 確認 Google Cloud 專案設定正確

2. **影片無法播放**
   - 確認已安裝 FFmpeg
   - 檢查生成的 MP4 檔案大小 (應該 > 32 bytes)
   - 嘗試使用不同的媒體播放器

3. **生成失敗**
   - 檢查網路連接
   - 確認 API 配額未超限
   - 查看控制台錯誤訊息

4. **Veo API 響應問題**
   - 如果遇到「操作完成但未返回任何影片數據」錯誤：
     - 檢查 Google GenAI SDK 版本是否最新
     - 運行 `python test_veo_debug.py` 獲取詳細調試資訊
     - 查看控制台中的 API 響應結構分析
     - 確認 API 金鑰具有 Veo 模型訪問權限
   - 系統會自動提供詳細的故障排除建議

5. **影片下載問題**
   - 如果遇到 400 Bad Request 或其他下載錯誤：
     - 系統會自動嘗試多種下載方法（SDK 內建、多種 HTTP 認證）
     - 優先使用 Google GenAI SDK 的內建下載功能
     - 備用多種 HTTP 認證方案（X-Goog-Api-Key, Authorization header 等）
     - 查看控制台中的詳細下載診斷資訊
     - 確保已安裝最新版本：`pip install --upgrade google-genai google-ai-generativelanguage`

5. **FFmpeg 相關問題**
   - 確認 FFmpeg 已正確安裝並在 PATH 中
   - Windows 用戶可能需要重新啟動命令提示字元

### 日誌檢查
應用程式會在控制台輸出詳細的日誌訊息，包括：
- API 調用狀態
- 檔案生成進度
- 錯誤詳情和堆疊追蹤

## 更新日誌

### v2.0.0 (最新)
- 🎬 **重大更新**: Veo 服務完全重構，符合 Google Cloud Vertex AI 官方標準
- 🔧 **FFmpeg 整合**: 支援使用 FFmpeg 生成真實的 MP4 影片檔案
- 📐 **標準解析度**: 16:9 (1280x720) 和 9:16 (720x1280) HD 解析度
- ⏱️ **擴展時長**: 支援 5-8 秒影片生成 (符合官方規格)
- 🎨 **智能顏色**: 根據提示詞內容自動選擇影片顏色
- 📦 **完整 MP4 結構**: 包含 ftyp、moov、mdat boxes 的標準 MP4 格式
- 🔄 **回退機制**: FFmpeg 不可用時自動使用手動 MP4 生成
- 📊 **檔案大小**: 從 32 bytes 提升到 300-600KB 的真實影片檔案
- 🌐 **API 準備**: 為實際 Google Cloud Vertex AI API 調用做好準備

### v1.0.0
- ✨ 初始版本發布
- 🤖 支援 Gemini、Imagen、Veo 三種 AI 服務
- 🌐 Web 介面實作
- 📁 模組化架構設計

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 推送到分支
5. 創建 Pull Request

## 授權

本專案採用 MIT 授權條款。

## 聯絡資訊

## 🤝 貢獻

我們歡迎所有形式的貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何參與專案。

### 如何貢獻
- 🐛 報告錯誤
- 💡 建議新功能  
- 🔧 提交程式碼
- 📝 改善文檔
- ⭐ 給我們一個星星

## 📄 授權

本專案採用 MIT 授權條款 - 查看 [LICENSE](LICENSE) 檔案了解詳情。

## 🙏 致謝

感謝以下服務提供商：
- [OpenAI](https://openai.com/) - DALL-E 3 圖像生成和 GPT 模型
- [Google Cloud](https://cloud.google.com/) - Imagen 4 圖像生成和 Veo 影片生成
- [Google AI](https://ai.google.dev/) - Gemini 語言模型

## 📞 支援

如有問題或建議，請透過以下方式聯絡：
- 📧 [GitHub Issues](https://github.com/your-username/ai-media-generator/issues)
- 💬 [Discussions](https://github.com/your-username/ai-media-generator/discussions)

---

⭐ 如果這個專案對您有幫助，請給我們一個星星！ 
