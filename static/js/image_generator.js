// AI 內容生成器 - 圖像生成功能

// 圖像生成器類別
class ImageGenerator {
    constructor() {
        this.currentGeneration = null;
        this.generatedImages = [];
        this.priceCache = {};
        
        // 綁定事件
        this.bindEvents();
        
        console.log('圖像生成器已初始化');
    }
    
    // 綁定事件監聽器
    bindEvents() {
        // 參數變更事件
        const parameterElements = [
            'image-model', 'image-count', 'image-quality', 'image-size', 'image-style'
        ];
        
        // 只綁定模型變更事件來更新選項
        const modelElement = document.getElementById('image-model');
        if (modelElement) {
            modelElement.addEventListener('change', () => this.updateImageModelOptions());
        }
        
        // 原始 prompt 變更事件
        const originalPrompt = document.getElementById('image-prompt');
        if (originalPrompt) {
            originalPrompt.addEventListener('input', () => {
                this.updateFinalPrompt();
            });
        }
        
        // 初始化最終 prompt 顯示
        setTimeout(() => {
            this.updateFinalPrompt();
            this.updateImageModelOptions();
        }, 100);
    }
    
    // 更新圖像模型選項
    updateImageModelOptions() {
        const modelSelect = document.getElementById('image-model');
        const styleGroup = document.getElementById('image-style-group');
        const sizeSelect = document.getElementById('image-size');
        const qualitySelect = document.getElementById('image-quality');
        const countSelect = document.getElementById('image-count');
        
        if (!modelSelect) return;
        
        const selectedModel = modelSelect.value;
        
        // 根據模型顯示/隱藏風格選項
        if (styleGroup) {
            if (selectedModel === 'dall-e-3' || selectedModel === 'openai') {
                styleGroup.style.display = 'block';
            } else {
                styleGroup.style.display = 'none';
            }
        }
        
        // 更新生成數量選項
        if (countSelect) {
            countSelect.innerHTML = '';
            if (selectedModel === 'dall-e-3' || selectedModel === 'openai') {
                countSelect.innerHTML = `<option value="1" selected>1 張</option>`;
                countSelect.value = '1';
            } else {
                countSelect.innerHTML = `
                    <option value="1">1 張</option>
                    <option value="2">2 張</option>
                    <option value="3">3 張</option>
                    <option value="4" selected>4 張</option>
                `;
                countSelect.value = '4';
            }
        }
        
        // 更新尺寸選項
        if (sizeSelect) {
            const currentSize = sizeSelect.value;
            sizeSelect.innerHTML = '';
            
            if (selectedModel === 'dall-e-3' || selectedModel === 'openai') {
                // DALL-E 3 支援的尺寸
                sizeSelect.innerHTML = `
                    <option value="1024x1024" selected>1024×1024 (正方形)</option>
                    <option value="1024x1792">1024×1792 (直向)</option>
                    <option value="1792x1024">1792×1024 (橫向)</option>
                `;
            } else {
                // Imagen 支援的尺寸（基於 Vertex AI 支援的長寬比）
                sizeSelect.innerHTML = `
                    <option value="1024x1024" selected>1024×1024 (正方形 1:1)</option>
                    <option value="1152x896">1152×896 (橫向 4:3)</option>
                    <option value="896x1152">896×1152 (直向 3:4)</option>
                `;
            }
            
            // 嘗試保持原來的選擇
            if ([...sizeSelect.options].some(opt => opt.value === currentSize)) {
                sizeSelect.value = currentSize;
            } else {
                sizeSelect.value = '1024x1024';
            }
        }
        
        // 更新品質選項
        if (qualitySelect) {
            const currentQuality = qualitySelect.value;
            qualitySelect.innerHTML = '';
            
            if (selectedModel === 'dall-e-3' || selectedModel === 'openai') {
                // DALL-E 3 品質選項
                qualitySelect.innerHTML = `
                    <option value="standard">標準品質 (Standard)</option>
                    <option value="hd">高清品質 (HD)</option>
                `;
                // 嘗試保持原來的選擇，如果是有效的 DALL-E 3 品質
                if (['standard', 'hd'].includes(currentQuality)) {
                    qualitySelect.value = currentQuality;
                } else {
                    qualitySelect.value = 'standard';
                }
            } else {
                // Imagen 品質選項
                qualitySelect.innerHTML = `
                    <option value="standard" selected>標準 (快速)</option>
                    <option value="high">高品質</option>
                    <option value="ultra">超高品質</option>
                `;
                // 嘗試保持原來的選擇，如果是有效的 Imagen 品質
                if (['standard', 'high', 'ultra'].includes(currentQuality)) {
                    qualitySelect.value = currentQuality;
                } else {
                    qualitySelect.value = 'standard';
                }
            }
        }
    }
    
    // 獲取品質文字
    getQualityText(quality) {
        const modelSelect = document.getElementById('image-model');
        const selectedModel = modelSelect?.value || 'dall-e-3';
        
        if (selectedModel === 'dall-e-3' || selectedModel === 'openai') {
            // DALL-E 3 品質對應
            const qualityMap = {
                'standard': '標準品質',
                'hd': '高清品質'
            };
            return qualityMap[quality] || '標準品質';
        } else {
            // Imagen 品質對應
            const qualityMap = {
                'standard': '標準品質',
                'high': '高品質',
                'ultra': '超高品質'
            };
            return qualityMap[quality] || '標準品質';
        }
    }
    
    // 獲取生成參數
    getGenerationParams() {
        return {
            model: document.getElementById('image-model')?.value || 'dall-e-3',
            count: parseInt(document.getElementById('image-count')?.value || 4),
            quality: document.getElementById('image-quality')?.value || 'standard',
            size: document.getElementById('image-size')?.value || '1024x1024',
            style: document.getElementById('image-style')?.value || 'vivid'
        };
    }
    
    // 更新最終 prompt 顯示區域
    updateFinalPrompt() {
        const originalPrompt = document.getElementById('image-prompt');
        const finalPromptDisplay = document.getElementById('final-prompt-display');
        
        if (!originalPrompt || !finalPromptDisplay) return;
        
        const originalText = originalPrompt.value.trim();
        
        // 直接顯示原始內容，不進行翻譯
        finalPromptDisplay.value = originalText;
    }
    
    // 使用優化後的 prompt（已棄用 - 現在在生成時才翻譯）
    async useOptimizedPrompt(optimizedPrompt) {
        console.log('🔄 useOptimizedPrompt 開始執行，optimizedPrompt:', optimizedPrompt);
        
        const finalPromptDisplay = document.getElementById('final-prompt-display');
        console.log('📝 final-prompt-display 元素:', finalPromptDisplay);
        
        if (!finalPromptDisplay || !optimizedPrompt) {
            console.error('❌ 元素或 prompt 為空');
            return;
        }
        
        const trimmedPrompt = optimizedPrompt.trim();
        console.log('✂️ 處理後的 prompt:', trimmedPrompt);
        
        // 檢查是否需要翻譯（包含中文字符）
        const containsChinese = /[\u4e00-\u9fff]/.test(trimmedPrompt);
        console.log('🔍 是否包含中文:', containsChinese);
        
        if (containsChinese) {
            // 顯示翻譯中的狀態
            finalPromptDisplay.value = '🔄 正在轉換為最適合圖像生成的英文...';
            console.log('🔄 開始翻譯...');
            
            try {
                // 調用翻譯 API
                console.log('📡 調用翻譯 API...');
                const response = await apiRequest('/api/image/translate-prompt', {
                    method: 'POST',
                    body: JSON.stringify({ prompt: trimmedPrompt })
                });
                
                console.log('📡 翻譯 API 回應:', response);
                
                if (response.success && response.translated_prompt) {
                    console.log('✅ 翻譯成功:', response.translated_prompt);
                    finalPromptDisplay.value = response.translated_prompt;
                    showNotification('已更新最終生成 Prompt（已轉換為英文）', 'success');
                } else {
                    // 翻譯失敗，使用原始文本
                    console.warn('⚠️ 翻譯失敗，使用原始文本:', response.error);
                    finalPromptDisplay.value = trimmedPrompt;
                    showNotification('已更新最終生成 Prompt', 'success');
                }
            } catch (error) {
                // 翻譯出錯，使用原始文本
                console.error('❌ 翻譯請求失敗:', error);
                finalPromptDisplay.value = trimmedPrompt;
                showNotification('已更新最終生成 Prompt', 'success');
            }
        } else {
            // 如果是英文或其他語言，直接使用原始文本
            console.log('📝 直接使用原始文本（非中文）');
            finalPromptDisplay.value = trimmedPrompt;
            showNotification('已更新最終生成 Prompt', 'success');
        }
        
        console.log('✅ useOptimizedPrompt 執行完成');
    }
    
    // 優化 Prompt
    async optimizePrompt(contentType = 'image') {
        console.log('🔧 ImageGenerator.optimizePrompt 開始執行，contentType:', contentType);
        console.log('🔍 當前 this 對象:', this);
        console.log('🔍 window.imageGenerator:', window.imageGenerator);
        
        const promptTextarea = document.getElementById('image-prompt');
        console.log('📝 image-prompt 元素:', promptTextarea);
        console.log('📝 image-prompt 值:', promptTextarea?.value);
        
        // 同時檢查 video-prompt 元素（用於調試）
        const videoPromptTextarea = document.getElementById('video-prompt');
        console.log('🎬 video-prompt 元素:', videoPromptTextarea);
        console.log('🎬 video-prompt 值:', videoPromptTextarea?.value);
        
        if (!promptTextarea) {
            console.error('❌ 找不到 image-prompt 元素');
            showNotification('找不到輸入框元素，請重新載入頁面', 'error');
            return;
        }
        
        const prompt = promptTextarea.value.trim();
        if (!prompt) {
            showNotification('請先輸入 Prompt', 'warning');
            return;
        }
        
        const optimizeBtn = document.getElementById('optimize-image-btn');
        if (optimizeBtn) {
            optimizeBtn.disabled = true;
            optimizeBtn.textContent = '🔧 分析中...';
        }
        
        try {
            showLoading('正在分析 Prompt 安全性...', false);
            
            const response = await apiRequest('/api/image/optimize-prompt', {
                method: 'POST',
                body: JSON.stringify({ prompt, content_type: contentType })
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
        const resultsContainer = document.getElementById('optimization-results');
        
        if (!resultsContainer) return;
        
        // 顯示結果容器
        resultsContainer.style.display = 'block';
        
        // 填充六個優化選項
        for (let i = 1; i <= 6; i++) {
            const optionElement = document.getElementById(`optimization-option-${i}`);
            const textarea = optionElement?.querySelector('.optimization-textarea');
            
            if (textarea && optimizations[i - 1]) {
                textarea.value = optimizations[i - 1];
            }
        }
        
        // 滾動到結果區域
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 顯示安全優化結果
    displaySafeOptimization(results, container) {
        const optimizedTextarea = container.querySelector('#optimized-prompt-safe');
        const improvementsList = container.querySelector('#improvements-list');
        
        if (optimizedTextarea) {
            optimizedTextarea.value = results.optimized_prompt || results.original_prompt;
        }
        
        if (improvementsList && results.improvements) {
            improvementsList.innerHTML = '';
            results.improvements.forEach(improvement => {
                const li = document.createElement('li');
                li.textContent = improvement;
                improvementsList.appendChild(li);
            });
        }
    }
    
    // 顯示不安全優化結果
    displayUnsafeOptimization(results, container) {
        const riskAnalysis = container.querySelector('#risk-analysis');
        
        if (riskAnalysis) {
            riskAnalysis.textContent = results.risk_analysis || '檢測到可能的安全性問題';
        }
        
        if (results.suggestions) {
            this.displaySuggestions(results.suggestions, container);
        }
    }
    
    // 顯示建議選項
    displaySuggestions(suggestions, container) {
        const suggestionElements = ['suggestion-a', 'suggestion-b', 'suggestion-c'];
        const optionKeys = ['option_a', 'option_b', 'option_c'];
        
        suggestionElements.forEach((elementId, index) => {
            const suggestionEl = container.querySelector(`#${elementId}`);
            const optionKey = optionKeys[index];
            
            if (suggestionEl && suggestions[optionKey]) {
                const textarea = suggestionEl.querySelector('.suggestion-textarea');
                const description = suggestionEl.querySelector('.suggestion-description');
                
                if (textarea) {
                    textarea.value = suggestions[optionKey].prompt || '';
                }
                
                if (description) {
                    description.textContent = suggestions[optionKey].description || '';
                }
            }
        });
    }
    
    // 選擇優化版本
    async selectOptimization(optionNumber) {
        console.log('🔧 selectOptimization 開始執行，optionNumber:', optionNumber);
        
        const optionElement = document.getElementById(`optimization-option-${optionNumber}`);
        const textarea = optionElement?.querySelector('.optimization-textarea');
        
        console.log('📝 找到的元素:', { optionElement, textarea });
        console.log('📝 textarea 內容:', textarea?.value);
        
        if (textarea) {
            const optimizedText = textarea.value.trim();
            
            // 直接將優化版本的原文（不翻譯）放到最終prompt區域
            const finalPromptDisplay = document.getElementById('final-prompt-display');
            if (finalPromptDisplay) {
                finalPromptDisplay.value = optimizedText;
                console.log('📝 已將優化版本直接設定為最終prompt（未翻譯）:', optimizedText);
            }
            
            // 更新所有按鈕的狀態，顯示當前選擇的版本
            this.updateOptimizationButtonStates(optionNumber);
            
            showNotification(`已選擇優化版本 ${optionNumber}，將在生成時自動翻譯`, 'success');
        } else {
            console.error('❌ 找不到對應的 textarea 元素');
        }
    }

    // 使用建議版本 (用於不安全優化結果的建議選項)
    async useSuggestion(suggestionType, contentType) {
        console.log('🔧 useSuggestion 開始執行，suggestionType:', suggestionType, 'contentType:', contentType);
        
        // 只處理圖像相關的建議
        if (contentType !== 'image') {
            console.log('⚠️ contentType 不是 image，跳過處理');
            return;
        }
        
        const suggestionElement = document.getElementById(`suggestion-${suggestionType}`);
        const textarea = suggestionElement?.querySelector('.suggestion-textarea');
        
        console.log('📝 找到的建議元素:', { suggestionElement, textarea });
        console.log('📝 建議內容:', textarea?.value);
        
        if (textarea) {
            const suggestionText = textarea.value.trim();
            
            // 直接將建議版本的原文（不翻譯）放到最終prompt區域
            const finalPromptDisplay = document.getElementById('final-prompt-display');
            if (finalPromptDisplay) {
                finalPromptDisplay.value = suggestionText;
                console.log('📝 已將建議版本直接設定為最終prompt（未翻譯）:', suggestionText);
            }
            
            showNotification(`已使用建議 ${suggestionType.toUpperCase()}，將在生成時自動翻譯`, 'success');
        } else {
            console.error('❌ 找不到對應的建議 textarea 元素');
        }
    }
    
    // 更新優化按鈕狀態
    updateOptimizationButtonStates(selectedOption) {
        for (let i = 1; i <= 6; i++) {
            const button = document.querySelector(`#optimization-option-${i} .btn`);
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
        const resultsContainer = document.getElementById('optimization-results');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        showNotification('已保持原始 Prompt', 'success');
    }
    
    // 生成圖像
    async generateImages() {
        const finalPromptTextarea = document.getElementById('final-prompt-display');
        if (!finalPromptTextarea) return;
        
        let prompt = finalPromptTextarea.value.trim();
        if (!prompt) {
            showNotification('請先輸入 Prompt', 'warning');
            document.getElementById('image-prompt')?.focus();
            return;
        }
        
        const generateBtn = document.getElementById('generate-image-btn');
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.textContent = '🎨 準備中...';
        }
        
        try {
            // 檢查是否需要翻譯（包含中文字符）
            const containsChinese = /[\u4e00-\u9fff]/.test(prompt);
            
            if (containsChinese) {
                showLoading('正在使用 OpenAI 翻譯為最適合圖像生成的英文...', false);
                
                try {
                    // 使用 OpenAI 翻譯 API
                    const translateResponse = await apiRequest('/api/image/translate-prompt', {
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
                console.log('🎨 使用英文 prompt 進行圖像生成:', prompt);
            }
            
            // 驗證參數
            const params = {
                prompt,
                ...this.getGenerationParams()
            };
            
            // 添加調試資訊
            console.log('🔍 準備發送的生成參數:', params);
            
            const validation = this.validateGenerationParams(params);
            if (!validation.valid) {
                console.error('❌ 參數驗證失敗:', validation.message);
                showNotification(validation.message, 'error');
                return;
            }
            
            if (generateBtn) {
                generateBtn.textContent = '🎨 生成中...';
            }
            
            showLoading('正在生成圖像...', true);
            
            // 模擬進度更新
            this.simulateProgress();
            
            const response = await apiRequest('/api/image/generate', {
                method: 'POST',
                body: JSON.stringify(params)
            });
            
            hideLoading();
            
            if (response.success) {
                this.currentGeneration = response;
                this.displayGenerationResults(response);
                showNotification(`成功生成 ${response.total_count} 張圖像`, 'success');
            } else {
                throw new Error(response.error || '圖像生成失敗');
            }
            
        } catch (error) {
            hideLoading();
            handleError(error, '圖像生成');
        } finally {
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.textContent = '🎨 生成影像';
            }
        }
    }
    
    // 模擬進度更新
    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            updateLoadingProgress(Math.floor(progress));
        }, 500);
    }
    
    // 驗證生成參數
    validateGenerationParams(params) {
        if (!params.prompt || params.prompt.length === 0) {
            return { valid: false, message: 'Prompt 不能為空' };
        }
        
        if (params.prompt.length > 2000) {
            return { valid: false, message: 'Prompt 長度不能超過 2000 字元' };
        }
        
        if (params.count < 1 || params.count > 10) {
            return { valid: false, message: '圖像數量必須在 1-10 之間' };
        }
        
        // 根據模型驗證品質設定
        const model = params.model || 'dall-e-3';
        let validQualities;
        
        if (model === 'dall-e-3' || model === 'openai') {
            // DALL-E 3 支援的品質
            validQualities = ['standard', 'hd'];
        } else {
            // Imagen 支援的品質
            validQualities = ['standard', 'high', 'ultra'];
        }
        
        if (!validQualities.includes(params.quality)) {
            return { 
                valid: false, 
                message: `無效的品質設定: ${params.quality}，支援的選項: ${validQualities.join(', ')}` 
            };
        }
        
        // 根據模型驗證尺寸設定
        let validSizes;
        
        if (model === 'dall-e-3' || model === 'openai') {
            // DALL-E 3 支援的尺寸
            validSizes = ['1024x1024', '1024x1792', '1792x1024'];
        } else {
            // Imagen 支援的尺寸（基於 Vertex AI 支援的長寬比）
            validSizes = ['1024x1024', '1152x896', '896x1152', '1792x1024', '1024x1792'];
        }
        
        if (!validSizes.includes(params.size)) {
            return { 
                valid: false, 
                message: `無效的尺寸設定: ${params.size}，支援的選項: ${validSizes.join(', ')}` 
            };
        }
        
        return { valid: true };
    }
    
    // 顯示生成結果
    displayGenerationResults(results) {
        const resultsSection = document.getElementById('image-results');
        const imageGrid = document.getElementById('image-grid');
        
        if (!resultsSection || !imageGrid) return;
        
        // 顯示結果區域
        resultsSection.style.display = 'block';
        
        // 清空現有結果
        imageGrid.innerHTML = '';
        
        // 添加圖像
        if (results.images && results.images.length > 0) {
            results.images.forEach((image, index) => {
                const imageItem = this.createImageItem(image, index);
                imageGrid.appendChild(imageItem);
            });
            
            // 儲存到生成歷史
            this.generatedImages.push(...results.images);
        }
        
        // 滾動到結果區域
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 創建圖像項目
    createImageItem(image, index) {
        const item = document.createElement('div');
        item.className = 'image-item';
        item.innerHTML = `
            <img 
                src="${image.url}" 
                alt="Generated Image ${index + 1}" 
                class="image-preview"
                onclick="previewImage('${image.url}', '${image.filename}')"
                onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
            >
            <div class="image-error" style="display: none;">
                <div class="error-placeholder">
                    <div class="error-icon">🖼️</div>
                    <div class="error-text">圖像載入失敗</div>
                    <div class="error-filename">${image.filename}</div>
                </div>
            </div>
            <div class="image-info">
                <div class="image-details">
                    <strong>${image.filename}</strong><br>
                    <small>尺寸: ${image.size} | 品質: ${image.quality}</small><br>
                    <small>檔案大小: ${formatFileSize(image.file_size)}</small>
                </div>
                <div class="image-actions">
                    <button class="btn btn-sm btn-primary" onclick="downloadImage('${image.url}', '${image.filename}')">
                        📥 下載
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="copyImageUrl('${image.url}')">
                        🔗 複製連結
                    </button>
                </div>
            </div>
        `;
        
        return item;
    }
    
    // 預覽圖像
    previewImage(url, filename) {
        const modal = document.getElementById('image-preview-modal');
        const previewContainer = modal?.querySelector('.preview-container');
        const previewImg = document.getElementById('preview-image');
        
        if (modal && previewContainer && previewImg) {
            // 先設定當前預覽圖像（重要：在載入前設定）
            this.currentPreviewImage = { url, filename };
            console.log('🔧 設定當前預覽圖像:', this.currentPreviewImage);
            
            // 添加載入狀態類
            previewContainer.classList.add('loading');
            previewImg.style.display = 'none';
            
            // 顯示載入狀態（不破壞按鈕）
            let loadingDiv = previewContainer.querySelector('.preview-loading');
            if (!loadingDiv) {
                loadingDiv = document.createElement('div');
                loadingDiv.className = 'preview-loading';
                loadingDiv.innerHTML = `
                    <div class="loading-spinner"></div>
                    <p>載入圖像中...</p>
                `;
                previewContainer.appendChild(loadingDiv);
            }
            loadingDiv.style.display = 'flex';
            
            // 創建新的圖像元素進行預載
            const img = new Image();
            img.onload = () => {
                // 圖像載入成功，更新預覽圖像
                previewImg.src = url;
                previewImg.alt = filename;
                previewImg.style.display = 'block';
                
                // 隱藏載入狀態
                previewContainer.classList.remove('loading');
                loadingDiv.style.display = 'none';
                
                // 根據圖像尺寸調整預覽容器
                this.adjustPreviewSize(previewImg, img.naturalWidth, img.naturalHeight);
                
                console.log(`🖼️ 圖像載入成功: ${filename} (${img.naturalWidth}x${img.naturalHeight})`);
                console.log('✅ 當前預覽圖像狀態:', this.currentPreviewImage);
            };
            
            img.onerror = () => {
                // 圖像載入失敗
                previewContainer.classList.remove('loading');
                loadingDiv.innerHTML = `
                    <div class="error-icon">❌</div>
                    <p>圖像載入失敗</p>
                    <small>${filename}</small>
                `;
                console.error('❌ 圖像載入失敗:', url);
            };
            
            // 開始載入圖像
            img.src = url;
            
            // 顯示模態框
            showModal('image-preview-modal');
        }
    }

    // 調整預覽尺寸
    adjustPreviewSize(imgElement, originalWidth, originalHeight) {
        const container = imgElement.parentElement;
        if (!container) return;
        
        // 計算圖像的長寬比
        const aspectRatio = originalWidth / originalHeight;
        
        // 重置所有內聯樣式，讓CSS規則完全生效
        container.removeAttribute('style');
        imgElement.removeAttribute('style');
        
        // 確保圖像類別和ID正確
        imgElement.id = 'preview-image';
        
        // 添加圖像資訊到模態框標題
        const modalHeader = document.querySelector('#image-preview-modal .modal-header h3');
        if (modalHeader) {
            const aspectRatioText = aspectRatio > 1.5 ? '橫向' : aspectRatio < 0.75 ? '直向' : '方形';
            modalHeader.innerHTML = `🖼️ 圖像預覽 <small style="font-weight: normal; color: var(--text-secondary);">(${originalWidth}×${originalHeight} - ${aspectRatioText})</small>`;
        }
        
        console.log(`📐 調整預覽尺寸: ${originalWidth}×${originalHeight}, 長寬比: ${aspectRatio.toFixed(2)} (${aspectRatio > 1.5 ? '橫向' : aspectRatio < 0.75 ? '直向' : '方形'})`);
        console.log('🔍 圖像元素狀態:', {
            width: imgElement.clientWidth,
            height: imgElement.clientHeight,
            naturalWidth: imgElement.naturalWidth,
            naturalHeight: imgElement.naturalHeight
        });
    }
    
    // 下載圖像
    downloadImage(url, filename) {
        try {
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showNotification('開始下載圖像', 'success');
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
    
    // 複製圖像連結
    copyImageUrl(url) {
        console.log('🔧 copyImageUrl 被調用, URL:', url);
        try {
            const fullUrl = this.getFullUrl(url);
            console.log('📝 完整URL:', fullUrl);
            copyToClipboard(fullUrl);
            console.log('✅ 圖像連結已複製');
            showNotification('圖像連結已複製到剪貼簿', 'success');
        } catch (error) {
            console.error('❌ 複製連結失敗:', error);
            showNotification('複製連結失敗', 'error');
        }
    }
    
    // 下載當前預覽圖像
    downloadCurrentImage() {
        console.log('🔧 ImageGenerator.downloadCurrentImage 被調用');
        console.log('📝 當前預覽圖像狀態:', this.currentPreviewImage);
        console.log('📝 this 對象:', this);
        
        if (this.currentPreviewImage) {
            console.log('✅ 開始下載圖像:', this.currentPreviewImage.filename);
            console.log('📝 下載URL:', this.currentPreviewImage.url);
            try {
                this.downloadImage(this.currentPreviewImage.url, this.currentPreviewImage.filename);
                console.log('✅ downloadImage 調用成功');
            } catch (error) {
                console.error('❌ downloadImage 調用失敗:', error);
                showNotification('下載失敗', 'error');
            }
        } else {
            console.error('❌ 沒有設定當前預覽圖像');
            showNotification('沒有可下載的圖像', 'error');
        }
    }
    
    // 分享圖像
    shareImage() {
        console.log('🔧 ImageGenerator.shareImage 被調用');
        console.log('📝 當前預覽圖像狀態:', this.currentPreviewImage);
        console.log('📝 navigator.share 支援:', !!navigator.share);
        console.log('📝 this 對象:', this);
        
        if (this.currentPreviewImage && navigator.share) {
            console.log('✅ 使用原生分享功能');
            const fullUrl = this.getFullUrl(this.currentPreviewImage.url);
            console.log('📝 分享完整URL:', fullUrl);
            navigator.share({
                title: 'AI 生成圖像',
                text: '查看這張 AI 生成的圖像',
                url: fullUrl
            }).catch(error => {
                console.error('分享失敗:', error);
                // 備用方案：複製連結
                console.log('🔄 使用備用方案：複製連結');
                this.copyImageUrl(this.currentPreviewImage.url);
            });
        } else if (this.currentPreviewImage) {
            // 備用方案：複製連結
            console.log('🔄 使用備用方案：複製連結');
            try {
                this.copyImageUrl(this.currentPreviewImage.url);
                console.log('✅ copyImageUrl 調用成功');
            } catch (error) {
                console.error('❌ copyImageUrl 調用失敗:', error);
                showNotification('複製連結失敗', 'error');
            }
        } else {
            console.error('❌ 沒有設定當前預覽圖像');
            showNotification('沒有可分享的圖像', 'error');
        }
    }
    
    // 下載所有圖像
    downloadAll(type = 'images') {
        if (type === 'images' && this.generatedImages.length > 0) {
            this.generatedImages.forEach((image, index) => {
                setTimeout(() => {
                    this.downloadImage(image.url, image.filename);
                }, index * 500); // 延遲下載避免瀏覽器限制
            });
            
            showNotification(`開始下載 ${this.generatedImages.length} 張圖像`, 'success');
        } else {
            showNotification('沒有可下載的圖像', 'warning');
        }
    }
    
    // 清除結果
    clearResults(type = 'image') {
        if (type === 'image') {
            const resultsSection = document.getElementById('image-results');
            const imageGrid = document.getElementById('image-grid');
            const optimizationResults = document.getElementById('optimization-results');
            
            if (resultsSection) {
                resultsSection.style.display = 'none';
            }
            
            if (imageGrid) {
                imageGrid.innerHTML = '';
            }
            
            if (optimizationResults) {
                optimizationResults.style.display = 'none';
            }
            
            // 清空生成歷史
            this.generatedImages = [];
            this.currentGeneration = null;
            this.currentPreviewImage = null;
            
            showNotification('已清除所有結果', 'success');
        }
    }
    
    // 獲取生成統計
    getGenerationStats() {
        return {
            totalImages: this.generatedImages.length,
            currentGeneration: this.currentGeneration,
            lastGenerationTime: this.currentGeneration?.timestamp || null
        };
    }
}

// 全域函數（用於 HTML onclick 事件）
// 注意：optimizePrompt 函數已移至 main.js 進行統一路由處理

function generateImages() {
    if (window.imageGenerator) {
        window.imageGenerator.generateImages();
    }
}

// 全域函數：選擇優化版本
async function selectOptimization(optionNumber) {
    if (window.imageGenerator) {
        await window.imageGenerator.selectOptimization(optionNumber);
    }
}

// 全域函數：關閉優化選項
function closeOptimization() {
    if (window.imageGenerator) {
        window.imageGenerator.closeOptimization();
    }
}

async function useSuggestion(suggestionType, contentType) {
    if (window.imageGenerator) {
        await window.imageGenerator.useSuggestion(suggestionType, contentType);
    }
}



function updateImageModelOptions() {
    if (window.imageGenerator) {
        window.imageGenerator.updateImageModelOptions();
    }
}

function previewImage(url, filename) {
    if (window.imageGenerator) {
        window.imageGenerator.previewImage(url, filename);
    }
}

function downloadImage(url, filename) {
    if (window.imageGenerator) {
        window.imageGenerator.downloadImage(url, filename);
    }
}

function copyImageUrl(url) {
    if (window.imageGenerator) {
        window.imageGenerator.copyImageUrl(url);
    }
}

function downloadCurrentImage() {
    console.log('🔧 全域 downloadCurrentImage 函數被調用');
    console.log('📝 window.imageGenerator 存在:', !!window.imageGenerator);
    console.log('📝 window.imageGenerator 類型:', typeof window.imageGenerator);
    
    if (window.imageGenerator) {
        console.log('📝 調用 window.imageGenerator.downloadCurrentImage()');
        try {
            window.imageGenerator.downloadCurrentImage();
            console.log('✅ downloadCurrentImage 調用完成');
        } catch (error) {
            console.error('❌ downloadCurrentImage 調用錯誤:', error);
            showNotification('下載功能執行錯誤', 'error');
        }
    } else {
        console.error('❌ window.imageGenerator 不存在');
        showNotification('圖像生成器未初始化', 'error');
    }
}

function shareImage() {
    console.log('🔧 全域 shareImage 函數被調用');
    console.log('📝 window.imageGenerator 存在:', !!window.imageGenerator);
    console.log('📝 window.imageGenerator 類型:', typeof window.imageGenerator);
    
    if (window.imageGenerator) {
        console.log('📝 調用 window.imageGenerator.shareImage()');
        try {
            window.imageGenerator.shareImage();
            console.log('✅ shareImage 調用完成');
        } catch (error) {
            console.error('❌ shareImage 調用錯誤:', error);
            showNotification('分享功能執行錯誤', 'error');
        }
    } else {
        console.error('❌ window.imageGenerator 不存在');
        showNotification('圖像生成器未初始化', 'error');
    }
}

function downloadAll(type) {
    if (window.imageGenerator) {
        window.imageGenerator.downloadAll(type);
    }
}

function clearResults(type) {
    if (window.imageGenerator) {
        window.imageGenerator.clearResults(type);
    }
}

async function useOptimizedPromptFromSafe() {
    console.log('🔧 useOptimizedPromptFromSafe 開始執行');
    
    const optimizedTextarea = document.getElementById('optimized-prompt-safe');
    const originalTextarea = document.getElementById('image-prompt');
    const finalPromptDisplay = document.getElementById('final-prompt-display');
    
    console.log('📝 找到的元素:', { optimizedTextarea, originalTextarea, finalPromptDisplay });
    
    if (optimizedTextarea && originalTextarea && finalPromptDisplay) {
        const optimizedText = optimizedTextarea.value.trim();
        console.log('📝 優化後的文字:', optimizedText);
        
        if (optimizedText) {
            // 更新原始 prompt
            originalTextarea.value = optimizedText;
            updateCharCount('image-prompt', 'image-char-count');
            
            // 直接將優化版本的原文（不翻譯）放到最終prompt區域
            finalPromptDisplay.value = optimizedText;
            console.log('📝 已將優化版本直接設定為最終prompt（未翻譯）:', optimizedText);
            
            showNotification('已使用安全優化版本，將在生成時自動翻譯', 'success');
        }
    } else {
        console.error('❌ 找不到必要的元素');
    }
}

console.log('圖像生成器 JavaScript 已載入'); 