// AI 內容生成器 - 主要 JavaScript 功能

// 全域變數
let currentModal = null;
let currentSection = 'image-generator';

// DOM 載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI 內容生成器已初始化');
    
    // 初始化事件監聽器
    initializeEventListeners();
    
    // 初始化價格計算
    updateImagePrice();
});

// 初始化事件監聽器
function initializeEventListeners() {
    // 導航選單事件
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href').substring(1);
            showSection(sectionId);
        });
    });
    
    // 模態視窗關閉事件
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target.id);
        }
    });
    
    // ESC 鍵關閉模態視窗
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && currentModal) {
            closeModal(currentModal);
        }
    });
}

// 切換頁面區域
function showSection(sectionId) {
    // 隱藏所有區域
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // 顯示指定區域
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // 更新導航狀態
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`[href="#${sectionId}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    currentSection = sectionId;
    console.log(`切換到: ${sectionId}`);
}

// 切換手機版選單
function toggleMobileMenu() {
    const nav = document.querySelector('.main-nav');
    nav.style.display = nav.style.display === 'block' ? 'none' : 'block';
}

// 更新字數統計
function updateCharCount(textareaId, counterId) {
    const textarea = document.getElementById(textareaId);
    const counter = document.getElementById(counterId);
    
    if (textarea && counter) {
        const currentLength = textarea.value.length;
        const maxLength = textarea.getAttribute('maxlength') || 2000;
        counter.textContent = currentLength;
        
        // 根據字數百分比變更顏色
        const percentage = (currentLength / maxLength) * 100;
        if (percentage > 90) {
            counter.style.color = '#dc2626'; // 紅色
        } else if (percentage > 70) {
            counter.style.color = '#d97706'; // 橙色
        } else {
            counter.style.color = '#64748b'; // 灰色
        }
    }
}

// 顯示 Prompt 撰寫建議
function showPromptTips(contentType) {
    const modal = document.getElementById('prompt-tips-modal');
    const content = document.getElementById('prompt-tips-content');
    
    if (!modal || !content) return;
    
    // 載入提示內容
    loadPromptTips(contentType, content);
    
    // 顯示模態視窗
    showModal('prompt-tips-modal');
}

// 載入 Prompt 提示內容
function loadPromptTips(contentType, container) {
    // 顯示載入狀態
    container.innerHTML = '<div class="loading-spinner"></div><p>載入中...</p>';
    
    // 模擬 API 調用
    setTimeout(() => {
        if (contentType === 'image') {
            container.innerHTML = `
                <div class="prompt-tips-section">
                    <div class="tip-category">
                        <h4>🎭 角色描述</h4>
                        <ul class="tip-list">
                            <li onclick="insertPromptTip(this)">一位優雅的年輕女性，長髮飄逸</li>
                            <li onclick="insertPromptTip(this)">友善微笑的中年男性，穿著商務服裝</li>
                            <li onclick="insertPromptTip(this)">天真可愛的小孩，眼神清澈</li>
                            <li onclick="insertPromptTip(this)">慈祥的老年人，臉上布滿歲月痕跡</li>
                        </ul>
                    </div>
                    
                    <div class="tip-category">
                        <h4>🏞️ 背景場景</h4>
                        <ul class="tip-list">
                            <li onclick="insertPromptTip(this)">櫻花盛開的公園，陽光透過樹葉灑下</li>
                            <li onclick="insertPromptTip(this)">繁華的城市夜景，霓虹燈光閃爍</li>
                            <li onclick="insertPromptTip(this)">溫馨的咖啡廳，溫暖的燈光氛圍</li>
                            <li onclick="insertPromptTip(this)">壯麗的海邊夕陽，波浪輕撫沙灘</li>
                        </ul>
                    </div>
                    
                    <div class="tip-category">
                        <h4>📷 攝影技巧</h4>
                        <ul class="tip-list">
                            <li onclick="insertPromptTip(this)">使用 85mm 鏡頭，淺景深背景虛化</li>
                            <li onclick="insertPromptTip(this)">廣角鏡頭拍攝，展現遼闊的全景</li>
                            <li onclick="insertPromptTip(this)">微距攝影，捕捉細膩的紋理細節</li>
                            <li onclick="insertPromptTip(this)">逆光拍攝，營造夢幻的輪廓光</li>
                        </ul>
                    </div>
                    
                    <div class="tip-category">
                        <h4>🎨 藝術風格</h4>
                        <ul class="tip-list">
                            <li onclick="insertPromptTip(this)">超寫實風格，細節豐富層次分明</li>
                            <li onclick="insertPromptTip(this)">印象派藝術風格，色彩豐富筆觸明顯</li>
                            <li onclick="insertPromptTip(this)">復古膠片風格，溫暖色調懷舊質感</li>
                            <li onclick="insertPromptTip(this)">現代簡約風格，乾淨線條極簡構圖</li>
                        </ul>
                    </div>
                </div>
            `;
        } else if (contentType === 'video') {
            container.innerHTML = `
                <div class="prompt-tips-section">
                    <div class="tip-category">
                        <h4>🎬 動作場景</h4>
                        <ul class="tip-list">
                            <li onclick="insertVideoPromptTip(this)">一隻可愛的小貓在陽光下慢慢伸懶腰</li>
                            <li onclick="insertVideoPromptTip(this)">海浪輕柔地拍打著沙灘，泡沫緩緩消散</li>
                            <li onclick="insertVideoPromptTip(this)">櫻花花瓣在微風中輕舞飛揚</li>
                            <li onclick="insertVideoPromptTip(this)">雲朵在藍天中緩緩飄移變化</li>
                        </ul>
                    </div>
                    
                    <div class="tip-category">
                        <h4>📹 鏡頭運動</h4>
                        <ul class="tip-list">
                            <li onclick="insertVideoPromptTip(this)">廣角鏡頭緩慢推進，展現場景細節</li>
                            <li onclick="insertVideoPromptTip(this)">攝影機平移跟隨主體移動</li>
                            <li onclick="insertVideoPromptTip(this)">從高空俯視，鏡頭逐漸拉近</li>
                            <li onclick="insertVideoPromptTip(this)">360度環繞拍攝，展現全方位視角</li>
                        </ul>
                    </div>
                    
                    <div class="tip-category">
                        <h4>🌅 光線氛圍</h4>
                        <ul class="tip-list">
                            <li onclick="insertVideoPromptTip(this)">溫暖的黃金時刻光線，營造溫馨氛圍</li>
                            <li onclick="insertVideoPromptTip(this)">柔和的晨光透過窗戶灑入室內</li>
                            <li onclick="insertVideoPromptTip(this)">夕陽西下，天空呈現漸層色彩</li>
                            <li onclick="insertVideoPromptTip(this)">月光下的寧靜夜景，星光點點</li>
                        </ul>
                    </div>
                    
                    <div class="tip-category">
                        <h4>🎭 情感表達</h4>
                        <ul class="tip-list">
                            <li onclick="insertVideoPromptTip(this)">歡樂的笑聲，眼神中充滿喜悅</li>
                            <li onclick="insertVideoPromptTip(this)">深情的凝視，情感真摯動人</li>
                            <li onclick="insertVideoPromptTip(this)">寧靜的沉思，內心平和安詳</li>
                            <li onclick="insertVideoPromptTip(this)">驚喜的表情，眼中閃爍著興奮</li>
                        </ul>
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="prompt-tips-section">
                    <div class="tip-category">
                        <h4>💡 提示</h4>
                        <p>請選擇正確的內容類型以獲取相關建議。</p>
                    </div>
                </div>
            `;
        }
    }, 500);
}

// 插入 Prompt 提示
function insertPromptTip(element) {
    const tipText = element.textContent;
    const promptTextarea = document.getElementById('image-prompt');
    
    if (promptTextarea) {
        const currentValue = promptTextarea.value;
        const newValue = currentValue ? `${currentValue}, ${tipText}` : tipText;
        promptTextarea.value = newValue;
        
        // 更新字數統計
        updateCharCount('image-prompt', 'image-char-count');
        
        // 顯示成功通知
        showNotification('已添加提示詞', 'success');
    }
    
    // 關閉模態視窗
    closeModal('prompt-tips-modal');
}

// 插入影片 Prompt 提示
function insertVideoPromptTip(element) {
    const tipText = element.textContent;
    const promptTextarea = document.getElementById('video-prompt');
    
    if (promptTextarea) {
        const currentValue = promptTextarea.value;
        const newValue = currentValue ? `${currentValue}, ${tipText}` : tipText;
        promptTextarea.value = newValue;
        
        // 更新字數統計
        updateCharCount('video-prompt', 'video-char-count');
        
        // 更新最終 prompt 顯示
        if (window.videoGenerator) {
            window.videoGenerator.updateFinalPrompt();
        }
        
        // 顯示成功通知
        showNotification('已添加影片提示詞', 'success');
    }
    
    // 關閉模態視窗
    closeModal('prompt-tips-modal');
}

// 全域變數存儲原始 prompt
let originalPrompts = {
    image: '',
    video: ''
};

// 優化 Prompt（全域函數）
function optimizePrompt(contentType = 'image') {
    console.log('🔧 main.js optimizePrompt 被調用，contentType:', contentType);
    
    // 保存原始 prompt
    const promptTextarea = document.getElementById(contentType === 'video' ? 'video-prompt' : 'image-prompt');
    if (promptTextarea && promptTextarea.value.trim()) {
        saveOriginalPrompt(contentType, promptTextarea.value.trim());
    }
    
    try {
        if (contentType === 'video') {
            console.log('📹 處理影片優化請求');
            console.log('🔍 檢查 window.videoGenerator:', window.videoGenerator);
            console.log('🔍 VideoGenerator 類別是否存在:', typeof VideoGenerator);
            console.log('🔍 所有全域 window 屬性:', Object.keys(window).filter(key => key.includes('video') || key.includes('Video') || key.includes('Generator')));
            
            // 如果 videoGenerator 不存在，嘗試重新初始化
            if (!window.videoGenerator && typeof VideoGenerator !== 'undefined') {
                console.log('🔄 嘗試重新初始化影片生成器...');
                try {
                    window.videoGenerator = new VideoGenerator();
                    console.log('✅ 影片生成器重新初始化成功');
                } catch (initError) {
                    console.error('❌ 影片生成器重新初始化失敗:', initError);
                }
            }
            
            if (window.videoGenerator && typeof window.videoGenerator.optimizePrompt === 'function') {
                console.log('✅ 調用 videoGenerator.optimizePrompt');
                window.videoGenerator.optimizePrompt(contentType);
            } else {
                console.error('❌ 影片生成器未正確初始化');
                console.log('🔍 window.videoGenerator 狀態:', window.videoGenerator);
                console.log('🔍 optimizePrompt 方法存在:', typeof window.videoGenerator?.optimizePrompt);
                console.log('🔍 VideoGenerator 原型方法:', VideoGenerator?.prototype ? Object.getOwnPropertyNames(VideoGenerator.prototype) : 'VideoGenerator不存在');
                
                // 更詳細的錯誤資訊
                if (typeof VideoGenerator === 'undefined') {
                    showNotification('VideoGenerator 類別未載入，請檢查 video_generator.js 檔案', 'error');
                } else if (!window.videoGenerator) {
                    showNotification('影片生成器實例未創建，正在嘗試重新初始化...', 'warning');
                    // 最後一次嘗試
                    try {
                        window.videoGenerator = new VideoGenerator();
                        console.log('🔄 最後一次初始化嘗試成功');
                        window.videoGenerator.optimizePrompt(contentType);
                        return;
                    } catch (finalError) {
                        console.error('🚨 最後一次初始化嘗試失敗:', finalError);
                        showNotification(`影片生成器初始化失敗: ${finalError.message}`, 'error');
                    }
                } else {
                    showNotification('影片生成器缺少 optimizePrompt 方法，請重新載入頁面', 'error');
                }
            }
        } else if (contentType === 'image') {
            console.log('🖼️ 處理圖片優化請求');
            console.log('🔍 檢查 window.imageGenerator:', window.imageGenerator);
            
            if (window.imageGenerator && typeof window.imageGenerator.optimizePrompt === 'function') {
                console.log('✅ 調用 imageGenerator.optimizePrompt');
                window.imageGenerator.optimizePrompt(contentType);
            } else {
                console.error('❌ 圖像生成器未正確初始化');
                console.log('🔍 window.imageGenerator 狀態:', window.imageGenerator);
                console.log('🔍 optimizePrompt 方法存在:', typeof window.imageGenerator?.optimizePrompt);
                showNotification('圖像生成器未正確初始化，請重新載入頁面', 'error');
            }
        } else {
            console.error('❌ 未知的內容類型:', contentType);
            showNotification('未知的內容類型', 'error');
        }
    } catch (error) {
        console.error('❌ 優化 Prompt 時發生錯誤:', error);
        showNotification('優化功能發生錯誤，請重新載入頁面', 'error');
    }
}

// 摺疊/展開優化建議
function toggleOptimization(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        // 找到優化選項的內容區域
        const optionsContainer = container.querySelector('.optimization-options');
        const button = container.querySelector('.btn-outline');
        
        if (optionsContainer && button) {
            const isCollapsed = optionsContainer.style.display === 'none';
            
            if (isCollapsed) {
                // 展開
                optionsContainer.style.display = 'grid';
                button.innerHTML = '📁 摺疊優化建議';
            } else {
                // 摺疊
                optionsContainer.style.display = 'none';
                button.innerHTML = '📂 展開優化建議';
            }
            
            const contentType = containerId.includes('video') ? '影片' : '圖像';
            showNotification(isCollapsed ? `已展開${contentType}優化建議` : `已摺疊${contentType}優化建議`, 'info');
        }
    }
}

// 恢復原始 Prompt
function resetToOriginalPrompt(contentType) {
    if (contentType === 'image') {
        const promptTextarea = document.getElementById('image-prompt');
        const finalPromptTextarea = document.getElementById('final-prompt-display');
        
        if (promptTextarea && finalPromptTextarea) {
            // 使用目前原始輸入框的內容來更新最終顯示區域
            const currentOriginalPrompt = promptTextarea.value.trim();
            if (currentOriginalPrompt) {
                finalPromptTextarea.value = currentOriginalPrompt;
                
                // 重置所有按鈕狀態
                resetOptimizationButtonStates('optimization-option');
                
                showNotification('已將最終 Prompt 恢復為原始輸入內容', 'success');
            } else {
                showNotification('原始 Prompt 為空', 'warning');
            }
        } else {
            showNotification('找不到相關元素', 'warning');
        }
    } else if (contentType === 'video') {
        const promptTextarea = document.getElementById('video-prompt');
        const finalPromptTextarea = document.getElementById('final-video-prompt-display');
        
        if (promptTextarea && finalPromptTextarea) {
            // 使用目前原始輸入框的內容來更新最終顯示區域
            const currentOriginalPrompt = promptTextarea.value.trim();
            if (currentOriginalPrompt) {
                finalPromptTextarea.value = currentOriginalPrompt;
                
                // 重置所有按鈕狀態
                resetOptimizationButtonStates('video-optimization-option');
                
                showNotification('已將最終 Prompt 恢復為原始輸入內容', 'success');
            } else {
                showNotification('原始 Prompt 為空', 'warning');
            }
        } else {
            showNotification('找不到相關元素', 'warning');
        }
    }
}

// 重置優化按鈕狀態
function resetOptimizationButtonStates(optionPrefix) {
    for (let i = 1; i <= 6; i++) {
        const button = document.querySelector(`#${optionPrefix}-${i} .btn`);
        if (button) {
            button.classList.remove('btn-success');
            button.textContent = '選擇此版本';
            
            if (i === 1 || i === 4) {
                button.classList.add('btn-primary');
            } else if (i === 2 || i === 5) {
                button.classList.add('btn-secondary');
            } else {
                button.classList.add('btn-outline');
            }
        }
    }
}

// 保存原始 Prompt（在優化前調用）
function saveOriginalPrompt(contentType, prompt) {
    originalPrompts[contentType] = prompt;
}

// 顯示模態視窗
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        modal.style.display = 'flex';
        currentModal = modalId;
        
        // 防止背景滾動
        document.body.style.overflow = 'hidden';
        
        // 添加點擊背景關閉功能
        addModalBackdropHandler(modal, modalId);
        
        // 添加 ESC 鍵關閉功能
        addEscapeKeyHandler(modalId);
    }
}

// 關閉模態視窗
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
        currentModal = null;
        
        // 恢復背景滾動
        document.body.style.overflow = 'auto';
        
        // 移除事件監聽器
        removeModalEventHandlers(modal);
        
        // 如果是圖像預覽模態框，重置狀態
        if (modalId === 'image-preview-modal') {
            resetImagePreviewModal();
        }
    }
}

// 重置圖像預覽模態框狀態
function resetImagePreviewModal() {
    // 重置標題
    const modalHeader = document.querySelector('#image-preview-modal .modal-header h3');
    if (modalHeader) {
        modalHeader.innerHTML = '🖼️ 圖像預覽';
    }
    
    // 重置預覽容器
    const previewContainer = document.querySelector('#image-preview-modal .preview-container');
    if (previewContainer) {
        previewContainer.innerHTML = '<img id="preview-image" src="" alt="Preview">';
        previewContainer.style.minHeight = '';
        previewContainer.style.maxHeight = '';
    }
}

// 添加模態視窗背景點擊關閉處理
function addModalBackdropHandler(modal, modalId) {
    const backdropHandler = function(e) {
        // 如果點擊的是模態視窗背景（不是內容區域）
        if (e.target === modal) {
            closeModal(modalId);
        }
    };
    
    modal.addEventListener('click', backdropHandler);
    modal._backdropHandler = backdropHandler; // 保存引用以便後續移除
}

// 添加 ESC 鍵關閉處理
function addEscapeKeyHandler(modalId) {
    const escapeHandler = function(e) {
        if (e.key === 'Escape' && currentModal === modalId) {
            closeModal(modalId);
        }
    };
    
    document.addEventListener('keydown', escapeHandler);
    document._escapeHandler = escapeHandler; // 保存引用以便後續移除
}

// 移除模態視窗事件處理器
function removeModalEventHandlers(modal) {
    if (modal._backdropHandler) {
        modal.removeEventListener('click', modal._backdropHandler);
        delete modal._backdropHandler;
    }
    
    if (document._escapeHandler) {
        document.removeEventListener('keydown', document._escapeHandler);
        delete document._escapeHandler;
    }
}

// 顯示載入動畫
function showLoading(message = '處理中...', showProgress = false) {
    const overlay = document.getElementById('loading-overlay');
    const messageEl = document.getElementById('loading-message');
    const progressEl = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    if (overlay && messageEl) {
        messageEl.textContent = message;
        overlay.style.display = 'flex';
        
        if (showProgress) {
            progressEl.style.width = '0%';
            progressText.textContent = '0%';
        }
    }
}

// 更新載入進度
function updateLoadingProgress(percentage) {
    const progressEl = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    if (progressEl && progressText) {
        progressEl.style.width = `${percentage}%`;
        progressText.textContent = `${percentage}%`;
    }
}

// 隱藏載入動畫
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// 顯示通知
function showNotification(message, type = 'info', duration = 3000) {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // 自動移除通知
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, duration);
}

// 複製文字到剪貼板
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('已複製到剪貼板', 'success');
        }).catch(err => {
            console.error('複製失敗:', err);
            showNotification('複製失敗', 'error');
        });
    } else {
        // 備用方法
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showNotification('已複製到剪貼板', 'success');
            } else {
                showNotification('複製失敗', 'error');
            }
        } catch (err) {
            console.error('複製失敗:', err);
            showNotification('複製失敗', 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

// 複製 Prompt 到輸入框
function copyToPrompt(sourceId, targetId) {
    const source = document.getElementById(sourceId);
    const target = document.getElementById(targetId);
    
    if (source && target) {
        target.value = source.value;
        updateCharCount(targetId, targetId.replace('prompt', 'char-count'));
        showNotification('已套用 Prompt', 'success');
    }
}

// 格式化檔案大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化時間
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
        return `${minutes}分${remainingSeconds}秒`;
    } else {
        return `${remainingSeconds}秒`;
    }
}

// API 請求封裝
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API 請求失敗:', error);
        throw error;
    }
}

// 防抖函數
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 節流函數
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 驗證輸入
function validateInput(value, type, options = {}) {
    switch (type) {
        case 'prompt':
            if (!value || value.trim().length === 0) {
                return { valid: false, message: 'Prompt 不能為空' };
            }
            if (value.length > (options.maxLength || 2000)) {
                return { valid: false, message: `Prompt 長度不能超過 ${options.maxLength || 2000} 字元` };
            }
            return { valid: true };
            
        case 'number':
            const num = parseInt(value);
            if (isNaN(num)) {
                return { valid: false, message: '請輸入有效數字' };
            }
            if (options.min && num < options.min) {
                return { valid: false, message: `數值不能小於 ${options.min}` };
            }
            if (options.max && num > options.max) {
                return { valid: false, message: `數值不能大於 ${options.max}` };
            }
            return { valid: true };
            
        default:
            return { valid: true };
    }
}

// 錯誤處理
function handleError(error, context = '') {
    console.error(`錯誤 ${context}:`, error);
    
    let message = '發生未知錯誤';
    let duration = 5000;
    
    if (error.message) {
        message = error.message;
    } else if (typeof error === 'string') {
        message = error;
    }
    
    // 檢查是否為內容政策違規錯誤
    if (message.includes('內容政策') || message.includes('content_policy') || message.includes('敏感')) {
        // 對於內容政策錯誤，顯示更長時間和更詳細的建議
        duration = 8000;
        
        // 如果錯誤訊息很短，添加建議
        if (!message.includes('建議') && !message.includes('優化')) {
            message += '\n\n💡 建議：請使用「🎨 優化 Prompt」功能獲得安全的替代方案。';
        }
    }
    
    showNotification(message, 'error', duration);
}

// 工具函數：檢查是否為移動設備
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// 工具函數：檢查網路狀態
function checkNetworkStatus() {
    return navigator.onLine;
}

// 匯出主要函數（如果需要模組化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showSection,
        toggleMobileMenu,
        updateCharCount,
        showPromptTips,
        showModal,
        closeModal,
        showLoading,
        hideLoading,
        showNotification,
        copyToClipboard,
        copyToPrompt,
        apiRequest,
        debounce,
        throttle,
        validateInput,
        handleError
    };
}

console.log('Main JavaScript 已載入'); 