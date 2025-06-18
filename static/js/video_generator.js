// 影片生成器類別
class VideoGenerator {
    constructor() {
        this.generatedVideos = [];
        this.currentGeneration = null;
        this.currentPreviewVideo = null;
        
        this.bindEvents();
    }
    
    // 綁定事件
    bindEvents() {
        // 參數變更事件
        const modelElement = document.getElementById('video-model');
        if (modelElement) {
            modelElement.addEventListener('change', () => {
                this.updateVideoModelOptions();
            });
        }
        
        // 原始 prompt 變更事件
        const originalPrompt = document.getElementById('video-prompt');
        if (originalPrompt) {
            originalPrompt.addEventListener('input', () => {
                this.updateFinalPrompt();
            });
        }
        
        // 初始化最終 prompt 顯示和模型選項
        setTimeout(() => {
            this.updateFinalPrompt();
            this.updateVideoModelOptions();
        }, 100);
    }
    
    // 更新影片模型選項
    updateVideoModelOptions() {
        const modelSelect = document.getElementById('video-model');
        const durationSelect = document.getElementById('video-duration');
        
        if (!modelSelect) return;
        
        const selectedModel = modelSelect.value;
        
        // 更新時長選項
        if (durationSelect) {
            const currentDuration = durationSelect.value;
            durationSelect.innerHTML = '';
            
            if (selectedModel === 'openai') {
                // OpenAI 支援的時長 (3-10秒)
                for (let i = 3; i <= 10; i++) {
                    const option = document.createElement('option');
                    option.value = i;
                    option.textContent = `${i} 秒`;
                    durationSelect.appendChild(option);
                }
            } else {
                // Veo 支援的時長 (5-8秒)
                for (let i = 5; i <= 8; i++) {
                    const option = document.createElement('option');
                    option.value = i;
                    option.textContent = `${i} 秒`;
                    durationSelect.appendChild(option);
                }
            }
            
            // 嘗試保持原來的選擇
            if ([...durationSelect.options].some(opt => opt.value === currentDuration)) {
                durationSelect.value = currentDuration;
            } else {
                // 設定預設值
                durationSelect.value = selectedModel === 'openai' ? '5' : '5';
            }
        }
        
    }
    
    // 獲取生成參數
    getGenerationParams() {
        return {
            model: document.getElementById('video-model')?.value || 'veo',
            aspectRatio: document.getElementById('video-aspect-ratio')?.value || '16:9',
            duration: parseInt(document.getElementById('video-duration')?.value || 5),
            personGeneration: document.getElementById('video-person-generation')?.value || 'allow_adult'
        };
    }
    
    // 更新最終 prompt 顯示區域
    updateFinalPrompt() {
        const originalPrompt = document.getElementById('video-prompt');
        const finalPromptDisplay = document.getElementById('final-video-prompt-display');
        
        if (!originalPrompt || !finalPromptDisplay) return;
        
        const originalText = originalPrompt.value.trim();
        
        // 直接顯示原始內容，不進行翻譯
        finalPromptDisplay.value = originalText;
    }
    
    // 優化 Prompt
    async optimizePrompt(contentType = 'video') {
        console.log('🔧 VideoGenerator.optimizePrompt 開始執行，contentType:', contentType);
        console.log('🔍 當前 this 對象:', this);
        console.log('🔍 window.videoGenerator:', window.videoGenerator);
        
        const promptTextarea = document.getElementById('video-prompt');
        console.log('📝 video-prompt 元素:', promptTextarea);
        console.log('📝 video-prompt 值:', promptTextarea?.value);
        
        // 同時檢查 image-prompt 元素（用於調試）
        const imagePromptTextarea = document.getElementById('image-prompt');
        console.log('🖼️ image-prompt 元素:', imagePromptTextarea);
        console.log('🖼️ image-prompt 值:', imagePromptTextarea?.value);
        
        if (!promptTextarea) {
            console.error('❌ 找不到 video-prompt 元素');
            showNotification('找不到輸入框元素，請重新載入頁面', 'error');
            return;
        }
        
        // 先更新最終 prompt 顯示
        this.updateFinalPrompt();
        
        const prompt = promptTextarea.value.trim();
        console.log('📄 獲取到的 prompt:', `"${prompt}"`);
        console.log('📏 prompt 長度:', prompt.length);
        
        // 也檢查最終 prompt 顯示區域
        const finalPromptDisplay = document.getElementById('final-video-prompt-display');
        if (finalPromptDisplay) {
            const finalPrompt = finalPromptDisplay.value.trim();
            console.log('📄 最終 prompt 顯示:', `"${finalPrompt}"`);
            
            // 如果原始 prompt 為空但最終 prompt 有內容，使用最終 prompt
            if (!prompt && finalPrompt) {
                console.log('📝 使用最終 prompt 顯示區域的內容');
                promptTextarea.value = finalPrompt;
                const updatedPrompt = finalPrompt;
                
                if (!updatedPrompt) {
                    console.log('⚠️ 所有 prompt 都為空，顯示警告');
                    showNotification('請先輸入 Prompt', 'warning');
                    promptTextarea.focus();
                    return;
                }
            } else if (!prompt) {
                console.log('⚠️ prompt 為空，顯示警告');
                showNotification('請先輸入 Prompt', 'warning');
                promptTextarea.focus();
                return;
            }
        } else if (!prompt) {
            console.log('⚠️ prompt 為空，顯示警告');
            showNotification('請先輸入 Prompt', 'warning');
            promptTextarea.focus();
            return;
        }
        
        console.log('✅ prompt 驗證通過，開始優化...');
        
        // 獲取最終要使用的 prompt
        const finalPrompt = promptTextarea.value.trim();
        console.log('📝 最終使用的 prompt:', `"${finalPrompt}"`);
        
        const optimizeBtn = document.getElementById('optimize-video-btn');
        if (optimizeBtn) {
            optimizeBtn.disabled = true;
            optimizeBtn.textContent = '🔧 分析中...';
        }
        
        try {
            showLoading('正在優化影片 Prompt...', false);
            
            const response = await apiRequest('/api/video/optimize-prompt', {
                method: 'POST',
                body: JSON.stringify({ prompt: finalPrompt, content_type: contentType })
            });
            
            hideLoading();
            
            if (response.error) {
                throw new Error(response.error);
            }
            
            this.displayOptimizationResults(response.optimizations);
            
        } catch (error) {
            hideLoading();
            handleError(error, 'Prompt 優化');
        } finally {
            if (optimizeBtn) {
                optimizeBtn.disabled = false;
                optimizeBtn.textContent = '🔧 優化 Prompt';
            }
        }
    }
    
    // 顯示優化選項
    displayOptimizationResults(optimizations) {
        const resultsContainer = document.getElementById('video-optimization-results');
        
        if (!resultsContainer) return;
        
        // 顯示結果容器
        resultsContainer.style.display = 'block';
        
        // 填充六個優化選項
        for (let i = 1; i <= 6; i++) {
            const optionElement = document.getElementById(`video-optimization-option-${i}`);
            const textarea = optionElement?.querySelector('.optimization-textarea');
            
            if (textarea && optimizations[i - 1]) {
                textarea.value = optimizations[i - 1];
            }
        }
        
        // 滾動到結果區域
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 選擇優化版本
    selectOptimization(optionNumber) {
        const optionElement = document.getElementById(`video-optimization-option-${optionNumber}`);
        const textarea = optionElement?.querySelector('.optimization-textarea');
        const finalPromptTextarea = document.getElementById('final-video-prompt-display');
        
        if (textarea && finalPromptTextarea) {
            // 只更新最終 prompt 顯示區域，保持原始輸入不變
            finalPromptTextarea.value = textarea.value;
            
            // 更新所有按鈕的狀態，顯示當前選擇的版本
            this.updateOptimizationButtonStates(optionNumber);
            
            // 不隱藏優化結果，讓用戶可以重複選擇
            // const resultsContainer = document.getElementById('video-optimization-results');
            // if (resultsContainer) {
            //     resultsContainer.style.display = 'none';
            // }
            
            showNotification(`已選擇優化版本 ${optionNumber}，原始 Prompt 保持不變`, 'success');
        }
    }
    
    // 更新優化按鈕狀態
    updateOptimizationButtonStates(selectedOption) {
        for (let i = 1; i <= 6; i++) {
            const button = document.querySelector(`#video-optimization-option-${i} .btn`);
            if (button) {
                if (i === selectedOption) {
                    button.classList.remove('btn-primary', 'btn-secondary', 'btn-outline');
                    button.classList.add('btn-success');
                    button.textContent = '✓ 已選擇';
                } else {
                    button.classList.remove('btn-success');
                    if (i === 1 || i === 4) {
                        button.classList.add('btn-primary');
                        button.textContent = '選擇此版本';
                    } else if (i === 2 || i === 5) {
                        button.classList.add('btn-secondary');
                        button.textContent = '選擇此版本';
                    } else {
                        button.classList.add('btn-outline');
                        button.textContent = '選擇此版本';
                    }
                }
            }
        }
    }
    
    // 關閉優化選項，保持原始 Prompt
    closeOptimization() {
        const resultsContainer = document.getElementById('video-optimization-results');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        showNotification('已保持原始 Prompt', 'success');
    }
    
    // 生成影片
    async generateVideos() {
        const finalPromptTextarea = document.getElementById('final-video-prompt-display');
        if (!finalPromptTextarea) return;
        
        let prompt = finalPromptTextarea.value.trim();
        if (!prompt) {
            showNotification('請先輸入 Prompt', 'warning');
            document.getElementById('video-prompt')?.focus();
            return;
        }
        
        const generateBtn = document.getElementById('generate-video-btn');
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.textContent = '🎬 準備中...';
        }
        
        try {
            // 檢查是否需要翻譯（包含中文字符）
            const containsChinese = /[\u4e00-\u9fff]/.test(prompt);
            
            if (containsChinese) {
                showLoading('正在使用 OpenAI 翻譯為最適合影片生成的英文...', false);
                
                try {
                    // 使用 OpenAI 翻譯 API
                    const translateResponse = await apiRequest('/api/video/translate-prompt', {
                        method: 'POST',
                        body: JSON.stringify({ prompt })
                    });
                    
                    // 隱藏翻譯載入畫面
                    hideLoading();
                    
                    if (translateResponse.success && translateResponse.translated_prompt) {
                        prompt = translateResponse.translated_prompt;
                        console.log('🌐 OpenAI 翻譯結果:', prompt);
                        showNotification('已使用 OpenAI 翻譯為英文 Prompt', 'success');
                    } else {
                        console.warn('翻譯失敗，使用原始文本:', translateResponse.error);
                        showNotification('翻譯失敗，使用原始 Prompt', 'warning');
                    }
                } catch (error) {
                    // 確保在錯誤時也隱藏載入畫面
                    hideLoading();
                    console.error('翻譯請求失敗:', error);
                    showNotification('翻譯失敗，使用原始 Prompt', 'warning');
                }
            } else {
                console.log('📝 使用英文 prompt 進行影片生成:', prompt);
            }
            
            // 驗證參數
            const params = {
                prompt,
                ...this.getGenerationParams()
            };
            
            const validation = this.validateGenerationParams(params);
            if (!validation.valid) {
                showNotification(validation.message, 'error');
                return;
            }
            
            if (generateBtn) {
                generateBtn.textContent = '🎬 生成中...';
            }
            
            showLoading('正在生成影片，這可能需要 2-3 分鐘...', true);
            
            // 模擬進度更新
            this.simulateProgress();
            
            const response = await apiRequest('/api/video/generate', {
                method: 'POST',
                body: JSON.stringify(params)
            });
            
            hideLoading();
            
            if (response.success) {
                this.currentGeneration = response;
                this.displayGenerationResults(response);
                showNotification(`成功生成影片`, 'success');
            } else {
                throw new Error(response.error || '影片生成失敗');
            }
            
        } catch (error) {
            hideLoading();
            handleError(error, '影片生成');
        } finally {
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.textContent = '🎬 生成影片';
            }
        }
    }
    
    // 模擬進度更新
    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            updateLoadingProgress(Math.floor(progress));
        }, 2000); // 較慢的進度更新，因為影片生成需要更長時間
    }
    
    // 驗證生成參數
    validateGenerationParams(params) {
        if (!params.prompt || params.prompt.length === 0) {
            return { valid: false, message: 'Prompt 不能為空' };
        }
        
        if (params.prompt.length > 2000) {
            return { valid: false, message: 'Prompt 長度不能超過 2000 字元' };
        }
        
        const validAspectRatios = ['16:9', '9:16'];
        if (!validAspectRatios.includes(params.aspectRatio)) {
            return { valid: false, message: '無效的影片比例設定' };
        }
        
        const validDurations = [5, 6, 7, 8];
        if (!validDurations.includes(params.duration)) {
            return { valid: false, message: '無效的影片長度設定 (支援5-8秒)' };
        }
        
        return { valid: true };
    }
    
    // 顯示生成結果
    displayGenerationResults(results) {
        const resultsSection = document.getElementById('video-results');
        const videoGrid = document.getElementById('video-grid');
        
        if (!resultsSection || !videoGrid) return;
        
        // 顯示結果區域
        resultsSection.style.display = 'block';
        
        // 清空現有結果
        videoGrid.innerHTML = '';
        
        // 檢查是否為錯誤結果
        if (!results.success) {
            this.displayError(results, videoGrid);
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            return;
        }
        
        // 添加影片
        if (results.videos && results.videos.length > 0) {
            results.videos.forEach((video, index) => {
                const videoItem = this.createVideoItem(video, index);
                videoGrid.appendChild(videoItem);
            });
            
            // 儲存到生成歷史
            this.generatedVideos.push(...results.videos);
        }
        
        // 滾動到結果區域
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 顯示錯誤信息
    displayError(results, container) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message-detailed';
        
        let troubleshootingHtml = '';
        if (results.troubleshooting && results.troubleshooting.length > 0) {
            troubleshootingHtml = `
                <div class="troubleshooting-steps">
                    <h4>💡 解決方案建議：</h4>
                    <ol>
                        ${results.troubleshooting.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                </div>
            `;
        }
        
        let cloudUriHtml = '';
        if (results.cloud_uri) {
            cloudUriHtml = `
                <div class="technical-details">
                    <h4>🔗 技術詳情：</h4>
                    <p><strong>影片 URI：</strong> ${results.cloud_uri}</p>
                    <p><small>影片已成功生成，但下載步驟失敗。請按照上述建議檢查權限設定。</small></p>
                </div>
            `;
        }
        
        errorDiv.innerHTML = `
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0; color: #856404;">
                <h3 style="color: #dc3545; margin-top: 0;">❌ 影片生成失敗</h3>
                <div class="error-details">
                    <p><strong>錯誤原因：</strong></p>
                    <p style="background: #f8f9fa; padding: 10px; border-radius: 4px; border-left: 4px solid #dc3545;">${results.error}</p>
                </div>
                ${troubleshootingHtml}
                ${cloudUriHtml}
                <div class="action-buttons" style="margin-top: 15px;">
                    <button class="btn btn-primary" onclick="window.open('https://console.developers.google.com/apis/api/generativelanguage.googleapis.com/overview', '_blank')">
                        🔧 前往 Google Cloud Console
                    </button>
                    <button class="btn btn-secondary" onclick="this.parentElement.parentElement.parentElement.style.display='none'">
                        ✖️ 關閉
                    </button>
                </div>
            </div>
        `;
        
        container.appendChild(errorDiv);
    }
    
    // 創建影片項目
    createVideoItem(video, index) {
        const item = document.createElement('div');
        item.className = 'video-item';
        item.innerHTML = `
            <video 
                class="video-preview"
                onclick="previewVideo('${video.url}', '${video.filename}')"
                muted
                loop
                onmouseover="this.play()"
                onmouseout="this.pause()"
            >
                <source src="${video.url}" type="video/mp4">
                您的瀏覽器不支援影片播放。
            </video>
            <div class="video-info">
                <div class="video-details">
                    <strong>${video.filename}</strong><br>
                    <small>比例: ${video.aspectRatio} | 長度: ${video.duration}秒</small><br>
                    <small>檔案大小: ${formatFileSize(video.file_size)}</small>
                </div>
                <div class="video-actions">
                    <button class="btn btn-sm btn-primary" onclick="downloadVideo('${video.url}', '${video.filename}')">
                        📥 下載
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="copyVideoUrl('${video.url}')">
                        🔗 複製連結
                    </button>
                </div>
            </div>
        `;
        
        return item;
    }
    
    // 預覽影片
    previewVideo(url, filename) {
        const modal = document.getElementById('video-preview-modal');
        const previewVideo = document.getElementById('preview-video');
        
        if (modal && previewVideo) {
            const source = previewVideo.querySelector('source');
            if (source) {
                source.src = url;
                previewVideo.load(); // 重新載入影片
                
                // 添加錯誤處理
                previewVideo.onerror = () => {
                    console.warn('影片載入失敗，這是模擬模式的預期行為');
                    // 顯示友善的錯誤訊息
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'video-error-message';
                    errorDiv.innerHTML = `
                        <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 10px 0;">
                            <h4>🎬 模擬影片預覽</h4>
                            <p>這是模擬模式生成的影片檔案</p>
                            <p><strong>檔案名稱：</strong>${filename}</p>
                            <p><small>注意：由於 Google Veo 2 API 尚未公開發布，目前顯示的是模擬檔案。<br>
                            當 API 正式發布後，此處將顯示真實的 AI 生成影片。</small></p>
                        </div>
                    `;
                    
                    // 替換影片元素
                    const container = previewVideo.parentNode;
                    container.insertBefore(errorDiv, previewVideo);
                    previewVideo.style.display = 'none';
                };
                
                // 成功載入時移除錯誤訊息
                previewVideo.onloadeddata = () => {
                    const errorMsg = modal.querySelector('.video-error-message');
                    if (errorMsg) {
                        errorMsg.remove();
                        previewVideo.style.display = 'block';
                    }
                };
            }
            
            // 設定當前預覽影片
            this.currentPreviewVideo = { url, filename };
            
            showModal('video-preview-modal');
        }
    }
    
    // 下載影片
    downloadVideo(url, filename) {
        try {
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showNotification('開始下載影片', 'success');
        } catch (error) {
            console.error('下載失敗:', error);
            showNotification('下載失敗', 'error');
        }
    }
    
    // 生成完整URL
    getFullUrl(relativePath) {
        // 如果已經是完整URL，直接返回
        if (relativePath.startsWith('http://') || relativePath.startsWith('https://')) {
            return relativePath;
        }
        
        // 構建完整URL
        const protocol = window.location.protocol;
        const host = window.location.host;
        
        // 確保相對路徑以 / 開頭
        const path = relativePath.startsWith('/') ? relativePath : '/' + relativePath;
        
        return `${protocol}//${host}${path}`;
    }
    
    // 複製影片連結
    copyVideoUrl(url) {
        const fullUrl = this.getFullUrl(url);
        copyToClipboard(fullUrl);
    }
    
    // 下載當前預覽影片
    downloadCurrentVideo() {
        if (this.currentPreviewVideo) {
            this.downloadVideo(this.currentPreviewVideo.url, this.currentPreviewVideo.filename);
        }
    }
    
    // 分享影片
    shareVideo() {
        if (this.currentPreviewVideo && navigator.share) {
            const fullUrl = this.getFullUrl(this.currentPreviewVideo.url);
            navigator.share({
                title: 'AI 生成影片',
                text: '查看這個 AI 生成的影片',
                url: fullUrl
            }).catch(error => {
                console.error('分享失敗:', error);
                // 備用方案：複製連結
                this.copyVideoUrl(this.currentPreviewVideo.url);
            });
        } else if (this.currentPreviewVideo) {
            // 備用方案：複製連結
            this.copyVideoUrl(this.currentPreviewVideo.url);
        }
    }
    
    // 下載所有影片
    downloadAll(type = 'videos') {
        if (type === 'videos' && this.generatedVideos.length > 0) {
            this.generatedVideos.forEach((video, index) => {
                setTimeout(() => {
                    this.downloadVideo(video.url, video.filename);
                }, index * 1000); // 延遲下載避免瀏覽器限制
            });
            
            showNotification(`開始下載 ${this.generatedVideos.length} 個影片`, 'success');
        } else {
            showNotification('沒有可下載的影片', 'warning');
        }
    }
    
    // 清除結果
    clearResults(type = 'video') {
        if (type === 'video') {
            const resultsSection = document.getElementById('video-results');
            const videoGrid = document.getElementById('video-grid');
            const optimizationResults = document.getElementById('video-optimization-results');
            
            if (resultsSection) {
                resultsSection.style.display = 'none';
            }
            
            if (videoGrid) {
                videoGrid.innerHTML = '';
            }
            
            if (optimizationResults) {
                optimizationResults.style.display = 'none';
            }
            
            // 清空生成歷史
            this.generatedVideos = [];
            this.currentGeneration = null;
            this.currentPreviewVideo = null;
            
            showNotification('已清除所有結果', 'success');
        }
    }
    
    // 獲取生成統計
    getGenerationStats() {
        return {
            totalVideos: this.generatedVideos.length,
            currentGeneration: this.currentGeneration,
            lastGenerationTime: this.currentGeneration?.timestamp || null
        };
    }
}

// 全域函數：選擇影片優化版本
function selectVideoOptimization(optionNumber) {
    if (window.videoGenerator) {
        window.videoGenerator.selectOptimization(optionNumber);
    }
}

// 全域函數：關閉影片優化選項
function closeVideoOptimization() {
    if (window.videoGenerator) {
        window.videoGenerator.closeOptimization();
    }
}

// 全域函數：生成影片
function generateVideos() {
    if (window.videoGenerator) {
        window.videoGenerator.generateVideos();
    }
}

// 全域函數：更新影片價格


function updateVideoModelOptions() {
    if (window.videoGenerator) {
        window.videoGenerator.updateVideoModelOptions();
    }
}

// 全域函數：預覽影片
function previewVideo(url, filename) {
    if (window.videoGenerator) {
        window.videoGenerator.previewVideo(url, filename);
    }
}

// 全域函數：下載影片
function downloadVideo(url, filename) {
    if (window.videoGenerator) {
        window.videoGenerator.downloadVideo(url, filename);
    }
}

// 全域函數：複製影片連結
function copyVideoUrl(url) {
    if (window.videoGenerator) {
        window.videoGenerator.copyVideoUrl(url);
    }
}

// 全域函數：下載當前影片
function downloadCurrentVideo() {
    if (window.videoGenerator) {
        window.videoGenerator.downloadCurrentVideo();
    }
}

// 全域函數：分享影片
function shareVideo() {
    if (window.videoGenerator) {
        window.videoGenerator.shareVideo();
    }
}



console.log('影片生成器 JavaScript 已載入'); 