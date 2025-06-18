# Google Custom Search API 設定教學

## 📋 前置需求
- Google 帳戶
- Google Cloud 專案（可選，但建議）

## 🚀 設定步驟

### 步驟 1：建立 Google Cloud 專案（建議）
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊「新增專案」
3. 輸入專案名稱，例如：`ai-media-generator-search`
4. 點擊「建立」

### 步驟 2：啟用 Custom Search API
1. 在 Google Cloud Console 中，前往「API 和服務」→「程式庫」
2. 搜尋「Custom Search API」
3. 點擊「Custom Search API」
4. 點擊「啟用」

### 步驟 3：建立 API 金鑰
1. 前往「API 和服務」→「憑證」
2. 點擊「+ 建立憑證」→「API 金鑰」
3. 複製產生的 API 金鑰
4. **重要**：點擊「限制金鑰」
5. 在「API 限制」中選擇「限制金鑰」
6. 選擇「Custom Search API」
7. 點擊「儲存」

### 步驟 4：建立程式化搜尋引擎
1. 前往 [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. 點擊「開始使用」並登入
3. 點擊「新增」
4. 填寫搜尋引擎設定：
   - **搜尋引擎名稱**：例如 `AI Media Generator Search`
   - **要搜尋的網站**：選擇「搜尋整個網路」
   - **搜尋設定**：
     - ✅ 圖片搜尋：開啟
     - ✅ SafeSearch：開啟（建議）
5. 點擊「建立」
6. 複製「搜尋引擎 ID」（格式類似：`017576662512468239146:omuauf_lfve`）

### 步驟 5：設定環境變數
編輯您的 `.env` 檔案：

```env
# Google搜尋 API 設定
GOOGLE_SEARCH_API_KEY=您的API金鑰
GOOGLE_SEARCH_ENGINE_ID=您的搜尋引擎ID
```

## 💰 費用說明
- **免費額度**：每天 100 次搜尋查詢
- **付費方案**：超過免費額度後，每 1000 次查詢 $5 美元
- **每日上限**：最多 10,000 次查詢

## 🔧 測試設定
設定完成後，重新啟動應用程式，搜尋"狗"應該會返回高品質的相關圖片。

## ⚠️ 注意事項
1. **保護 API 金鑰**：不要將 API 金鑰提交到版本控制系統
2. **監控使用量**：在 Google Cloud Console 中監控 API 使用情況
3. **設定配額**：可以在 Google Cloud Console 中設定每日配額限制

## 🆘 常見問題

### Q: 是否一定要設定 Google Cloud 專案？
A: 不是必須的，但強烈建議。這樣可以更好地管理 API 金鑰和監控使用情況。

### Q: 可以搜尋特定網站嗎？
A: 可以！在建立程式化搜尋引擎時，可以指定特定網站或網域。

### Q: 如何提升搜尋品質？
A: 使用 Google Custom Search API 後，搜尋品質會大幅提升，因為使用的是 Google 官方搜尋算法。

## 📞 技術支援
如果在設定過程中遇到問題，請參考：
- [Google Custom Search API 文件](https://developers.google.com/custom-search/v1/overview)
- [Programmable Search Engine 說明](https://support.google.com/programmable-search/) 