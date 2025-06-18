// Google 圖片搜尋功能 JavaScript

// 全域變數
let currentSearchQuery = '';
let currentSearchPage = 1;
let totalSearchPages = 1;
let searchResults = [];
let selectedImages = new Set();
let searchOptions = {};

// 初始化圖片搜尋功能
function initializeImageSearch() {
    console.log('Google 圖片搜尋功能已初始化');
    
    // 初始化搜尋參數事件監聽器
    const searchInput = document.getElementById('image-search-query');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(validateSearchInput, 300));
    }
    
    // 載入搜尋選項
    loadSearchOptions();
    
    // 初始化選擇框
    resetImageSelection();
}

// 驗證搜尋輸入
function validateSearchInput() {
    const query = document.getElementById('image-search-query').value.trim();
    const searchBtn = document.querySelector('.search-btn');
    
    if (query.length > 0) {
        searchBtn.disabled = false;
        searchBtn.classList.remove('disabled');
    } else {
        searchBtn.disabled = true;
        searchBtn.classList.add('disabled');
    }
}

// 搜尋圖片主函數
async function searchImages(page = 1) {
    const query = document.getElementById('image-search-query').value.trim();
    
    if (!query) {
        showNotification('請輸入搜尋關鍵字', 'warning');
        return;
    }
    
    // 獲取搜尋參數
    const orientation = document.getElementById('search-orientation')?.value || 'any';
    const size = document.getElementById('search-size')?.value || 'medium';
    const type = document.getElementById('search-type')?.value || 'photo';
    const perPage = parseInt(document.getElementById('search-per-page')?.value || '12');
    
    // 顯示載入狀態
    showSearchLoading(true);
    hideSearchEmptyState();
    
    try {
        const searchParams = {
            query: query,
            page: page,
            per_page: perPage,
            orientation: orientation,
            size: size,
            type: type
        };
        
        const response = await fetch('/api/image/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(searchParams)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSearchQuery = query;
            currentSearchPage = page;
            searchResults = data.results || [];
            totalSearchPages = Math.ceil((data.total_results || 0) / perPage);
            
            displaySearchResults(data);
            updatePaginationControls();
            resetImageSelection();
            
            showNotification(data.message || '搜尋完成', 'success');
        } else {
            throw new Error(data.error || '搜尋失敗');
        }
        
    } catch (error) {
        console.error('搜尋錯誤:', error);
        showNotification(`搜尋失敗: ${error.message}`, 'error');
        showSearchEmptyState();
    } finally {
        showSearchLoading(false);
    }
}

// 顯示搜尋結果
function displaySearchResults(data) {
    const resultsSection = document.getElementById('search-results');
    const emptyState = document.getElementById('search-empty-state');
    const resultsTitle = document.getElementById('search-results-title');
    const resultsInfo = document.getElementById('search-results-info');
    const imageGrid = document.getElementById('search-image-grid');
    
    // 隱藏空狀態，顯示結果區域
    if (emptyState) emptyState.style.display = 'none';
    if (resultsSection) resultsSection.style.display = 'block';
    
    // 更新標題和資訊
    if (resultsTitle) resultsTitle.textContent = `🔍 "${data.query}" 的搜尋結果`;
    if (resultsInfo) resultsInfo.textContent = `找到 ${data.total_results || data.results.length} 張圖片`;
    
    // 清空現有結果
    if (imageGrid) {
        imageGrid.innerHTML = '';
        
        // 生成圖片網格
        data.results.forEach((image, index) => {
            const imageItem = createSearchImageItem(image, index);
            imageGrid.appendChild(imageItem);
        });
    }
    
    // 顯示分頁控制
    const paginationContainers = document.querySelectorAll('.pagination-container');
    paginationContainers.forEach(container => {
        container.style.display = totalSearchPages > 1 ? 'flex' : 'none';
    });
}

// 建立搜尋圖片項目
function createSearchImageItem(image, index) {
    const item = document.createElement('div');
    item.className = 'search-image-item';
    item.dataset.imageId = image.id;
    item.dataset.imageIndex = index;
    
    // 使用 thumb_url 或 url 作為縮圖
    const thumbUrl = image.thumb_url || image.url;
    const title = image.title || image.description || '無標題';
    const description = image.description || '';
    const attribution = image.attribution || '';
    
    item.innerHTML = `
        <div class="image-container">
            <img 
                src="${thumbUrl}" 
                alt="${title}"
                loading="lazy"
                onclick="previewSearchImage('${image.id}')"
                onerror="this.src='https://via.placeholder.com/300x200?text=圖片載入失敗'"
            >
            <div class="image-overlay">
                <div class="image-actions">
                    <button class="btn btn-sm btn-primary" onclick="downloadSingleImage('${image.id}')">
                        📥 下載
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="previewSearchImage('${image.id}')">
                        👁️ 預覽
                    </button>
                </div>
                <div class="image-selection">
                    <input 
                        type="checkbox" 
                        id="select-${image.id}" 
                        onchange="toggleImageSelection('${image.id}')"
                    >
                    <label for="select-${image.id}">選擇</label>
                </div>
            </div>
        </div>
        <div class="image-info">
            <div class="image-details">
                <div class="image-title">${title}</div>
                <div class="image-meta">
                    ${image.width && image.height ? `<span class="image-size">${image.width} × ${image.height}</span>` : ''}
                    ${image.file_type ? `<span class="image-type">${image.file_type}</span>` : ''}
                    <span class="image-platform">📍 Google</span>
                </div>
                ${attribution ? `<div class="image-attribution">${attribution}</div>` : ''}
                ${description && description !== title ? `<div class="image-description">${description}</div>` : ''}
            </div>
        </div>
    `;
    
    return item;
}

// 切換圖片選擇狀態
function toggleImageSelection(imageId) {
    const checkbox = document.getElementById(`select-${imageId}`);
    const item = checkbox.closest('.search-image-item');
    
    if (checkbox.checked) {
        selectedImages.add(imageId);
        item.classList.add('selected');
    } else {
        selectedImages.delete(imageId);
        item.classList.remove('selected');
    }
    
    updateSelectionCounter();
}

// 重置圖片選擇
function resetImageSelection() {
    selectedImages.clear();
    document.querySelectorAll('.search-image-item').forEach(item => {
        item.classList.remove('selected');
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox) checkbox.checked = false;
    });
    updateSelectionCounter();
}

// 更新選擇計數器
function updateSelectionCounter() {
    const counter = document.getElementById('selection-counter');
    const downloadBtn = document.getElementById('download-selected-btn');
    
    if (counter) {
        counter.textContent = `已選擇 ${selectedImages.size} 張`;
    }
    
    if (downloadBtn) {
        downloadBtn.disabled = selectedImages.size === 0;
        downloadBtn.classList.toggle('disabled', selectedImages.size === 0);
    }
}

// 下載單張圖片
async function downloadSingleImage(imageId) {
    const image = searchResults.find(img => img.id === imageId);
    if (!image) {
        showNotification('找不到圖片資訊', 'error');
        return;
    }
    
    // 顯示下載loading
    showDownloadLoading(true, '正在下載圖片...');
    
    try {
        const response = await fetch('/api/image/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_url: image.download_url || image.url
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`圖片下載成功: ${data.filename}`, 'success');
            
            // 創建下載連結
            const link = document.createElement('a');
            link.href = data.download_url;
            link.download = data.filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            throw new Error(data.error || '下載失敗');
        }
        
    } catch (error) {
        console.error('下載錯誤:', error);
        showNotification(`下載失敗: ${error.message}`, 'error');
    } finally {
        // 隱藏下載loading
        showDownloadLoading(false);
    }
}

// 下載選中的圖片
async function downloadSelectedImages() {
    if (selectedImages.size === 0) {
        showNotification('請先選擇要下載的圖片', 'warning');
        return;
    }
    
    const selectedImageIds = Array.from(selectedImages);
    const selectedImageData = searchResults.filter(img => selectedImageIds.includes(img.id));
    
    // 顯示批量下載loading
    showDownloadLoading(true, `正在下載 ${selectedImageData.length} 張圖片...`);
    
    let successCount = 0;
    let failCount = 0;
    
    for (const image of selectedImageData) {
        try {
            const response = await fetch('/api/image/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_url: image.download_url || image.url
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                successCount++;
                
                // 創建下載連結
                const link = document.createElement('a');
                link.href = data.download_url;
                link.download = data.filename;
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // 短暫延遲避免瀏覽器阻擋多個下載
                await new Promise(resolve => setTimeout(resolve, 500));
            } else {
                failCount++;
                console.error(`下載失敗: ${image.title}`, data.error);
            }
            
        } catch (error) {
            failCount++;
            console.error(`下載錯誤: ${image.title}`, error);
        }
    }
    
    // 隱藏下載loading
    showDownloadLoading(false);
    
    if (successCount > 0) {
        showNotification(`成功下載 ${successCount} 張圖片${failCount > 0 ? `，${failCount} 張失敗` : ''}`, 'success');
    } else {
        showNotification('所有圖片下載失敗', 'error');
    }
    
    // 清除選擇
    resetImageSelection();
}

// 預覽搜尋圖片
function previewSearchImage(imageId) {
    const image = searchResults.find(img => img.id === imageId);
    if (!image) return;
    
    const modal = document.getElementById('image-preview-modal');
    const previewImg = document.getElementById('preview-image');
    
    if (modal && previewImg) {
        previewImg.src = image.url;
        previewImg.alt = image.title || '預覽圖片';
        
        // 儲存當前預覽的圖片資訊到全域變數
        window.currentPreviewImage = image;
        
        modal.style.display = 'flex';
    }
}

// 載入搜尋頁面
async function loadSearchPage(page) {
    if (currentSearchQuery) {
        await searchImages(page);
    }
}

// 更新分頁控制
function updatePaginationControls() {
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');
    const pageInfo = document.getElementById('page-info');
    
    if (prevBtn) {
        prevBtn.disabled = currentSearchPage <= 1;
        prevBtn.classList.toggle('disabled', currentSearchPage <= 1);
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentSearchPage >= totalSearchPages;
        nextBtn.classList.toggle('disabled', currentSearchPage >= totalSearchPages);
    }
    
    if (pageInfo) {
        pageInfo.textContent = `第 ${currentSearchPage} 頁，共 ${totalSearchPages} 頁`;
    }
}

// 快速搜尋
function quickSearch(query) {
    const searchInput = document.getElementById('image-search-query');
    if (searchInput) {
        searchInput.value = query;
        searchImages(1);
    }
}

// 清除搜尋結果
function clearSearchResults() {
    const resultsSection = document.getElementById('search-results');
    const emptyState = document.getElementById('search-empty-state');
    const imageGrid = document.getElementById('search-image-grid');
    
    if (resultsSection) resultsSection.style.display = 'none';
    if (emptyState) emptyState.style.display = 'block';
    if (imageGrid) imageGrid.innerHTML = '';
    
    currentSearchQuery = '';
    currentSearchPage = 1;
    totalSearchPages = 1;
    searchResults = [];
    resetImageSelection();
}

// 顯示/隱藏搜尋載入狀態
function showSearchLoading(show) {
    const loadingOverlay = document.getElementById('search-loading-overlay');
    const searchBtn = document.querySelector('.search-btn');
    const loadingText = document.getElementById('search-loading-text');
    const loadingDescription = document.getElementById('search-loading-description');
    const progressFill = document.getElementById('search-progress-fill');
    const progressText = document.getElementById('search-progress-text');
    
    if (show) {
        // 顯示loading overlay
        if (loadingOverlay) {
            loadingOverlay.classList.add('show');
            // 阻止頁面滾動
            document.body.style.overflow = 'hidden';
        }
        
        // 禁用搜尋按鈕
        if (searchBtn) {
            searchBtn.disabled = true;
            searchBtn.textContent = '搜尋中...';
        }
        
        // 重置進度條和文字
        if (progressFill) progressFill.style.width = '0%';
        if (loadingText) loadingText.textContent = '🔍 正在搜尋圖片...';
        if (loadingDescription) loadingDescription.textContent = '正在從Google搜尋高品質圖片，請稍候...';
        if (progressText) progressText.textContent = '正在連接伺服器...';
        
        // 開始進度條動畫
        startSearchProgress();
        
    } else {
        // 隱藏loading overlay
        if (loadingOverlay) {
            loadingOverlay.classList.remove('show');
            // 恢復頁面滾動
            document.body.style.overflow = '';
        }
        
        // 恢復搜尋按鈕
        if (searchBtn) {
            searchBtn.disabled = false;
            searchBtn.textContent = '🔍 搜尋';
        }
        
        // 停止進度條動畫
        stopSearchProgress();
    }
}

// 搜尋進度條動畫
let searchProgressInterval;
let searchProgressValue = 0;

function startSearchProgress() {
    const progressFill = document.getElementById('search-progress-fill');
    const progressText = document.getElementById('search-progress-text');
    const loadingDescription = document.getElementById('search-loading-description');
    
    searchProgressValue = 0;
    
    // 清除之前的定時器
    if (searchProgressInterval) {
        clearInterval(searchProgressInterval);
    }
    
    const progressSteps = [
        { value: 20, text: '正在連接Google搜尋服務...', description: '建立安全連線中...' },
        { value: 40, text: '正在發送搜尋請求...', description: '處理搜尋參數和關鍵字...' },
        { value: 60, text: '正在解析搜尋結果...', description: '從Google獲取圖片資訊...' },
        { value: 80, text: '正在處理圖片資料...', description: '篩選和優化圖片品質...' },
        { value: 95, text: '即將完成...', description: '準備顯示搜尋結果...' }
    ];
    
    let stepIndex = 0;
    
    searchProgressInterval = setInterval(() => {
        if (stepIndex < progressSteps.length) {
            const step = progressSteps[stepIndex];
            searchProgressValue = step.value;
            
            if (progressFill) {
                progressFill.style.width = searchProgressValue + '%';
            }
            if (progressText) {
                progressText.textContent = step.text;
            }
            if (loadingDescription) {
                loadingDescription.textContent = step.description;
            }
            
            stepIndex++;
        } else {
            // 保持在95%直到搜尋完成
            if (progressFill) {
                progressFill.style.width = '95%';
            }
            if (progressText) {
                progressText.textContent = '正在完成搜尋...';
            }
        }
    }, 800); // 每800ms更新一次進度
}

function stopSearchProgress() {
    if (searchProgressInterval) {
        clearInterval(searchProgressInterval);
        searchProgressInterval = null;
    }
    
    // 完成時設為100%
    const progressFill = document.getElementById('search-progress-fill');
    const progressText = document.getElementById('search-progress-text');
    
    if (progressFill) {
        progressFill.style.width = '100%';
    }
    if (progressText) {
        progressText.textContent = '搜尋完成！';
    }
    
    // 短暫延遲後重置
    setTimeout(() => {
        if (progressFill) {
            progressFill.style.width = '0%';
        }
    }, 500);
}

// 顯示搜尋空狀態
function showSearchEmptyState() {
    const emptyState = document.getElementById('search-empty-state');
    const resultsSection = document.getElementById('search-results');
    
    if (emptyState) emptyState.style.display = 'block';
    if (resultsSection) resultsSection.style.display = 'none';
}

// 隱藏搜尋空狀態
function hideSearchEmptyState() {
    const emptyState = document.getElementById('search-empty-state');
    if (emptyState) emptyState.style.display = 'none';
}

// 下載當前預覽的圖片
function downloadCurrentImage() {
    if (window.currentPreviewImage) {
        downloadSingleImage(window.currentPreviewImage.id);
    }
}

// 分享圖片
function shareImage() {
    if (window.currentPreviewImage) {
        const image = window.currentPreviewImage;
        const shareData = {
            title: image.title || '分享圖片',
            text: image.description || '來自Google搜尋的圖片',
            url: image.url
        };
        
        if (navigator.share) {
            navigator.share(shareData).catch(console.error);
        } else {
            // 備用方案：複製到剪貼簿
            navigator.clipboard.writeText(image.url).then(() => {
                showNotification('圖片連結已複製到剪貼簿', 'success');
            }).catch(() => {
                showNotification('無法複製連結', 'error');
            });
        }
    }
}

// 載入搜尋選項
async function loadSearchOptions() {
    try {
        const response = await fetch('/api/image/search-options');
        const data = await response.json();
        
        if (data.success) {
            searchOptions = data.options;
            updateSearchOptionsUI();
        }
    } catch (error) {
        console.error('載入搜尋選項失敗:', error);
    }
}

// 更新搜尋選項UI
function updateSearchOptionsUI() {
    // 更新尺寸選項
    const sizeSelect = document.getElementById('search-size');
    if (sizeSelect && searchOptions.sizes) {
        sizeSelect.innerHTML = searchOptions.sizes.map(size => 
            `<option value="${size.id}">${size.name}</option>`
        ).join('');
    }
    
    // 更新類型選項
    const typeSelect = document.getElementById('search-type');
    if (typeSelect && searchOptions.types) {
        typeSelect.innerHTML = searchOptions.types.map(type => 
            `<option value="${type.id}">${type.name}</option>`
        ).join('');
    }
    
    // 更新方向選項
    const orientationSelect = document.getElementById('search-orientation');
    if (orientationSelect && searchOptions.orientations) {
        orientationSelect.innerHTML = searchOptions.orientations.map(orientation => 
            `<option value="${orientation.id}">${orientation.name}</option>`
        ).join('');
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

// 顯示下載Loading
function showDownloadLoading(show, message = '正在下載...') {
    const loadingOverlay = document.getElementById('search-loading-overlay');
    const loadingText = document.getElementById('search-loading-text');
    const loadingDescription = document.getElementById('search-loading-description');
    const progressFill = document.getElementById('search-progress-fill');
    const progressText = document.getElementById('search-progress-text');
    
    if (show) {
        // 顯示loading overlay
        if (loadingOverlay) {
            loadingOverlay.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
        
        // 設置下載相關文字
        if (loadingText) loadingText.textContent = '📥 ' + message;
        if (loadingDescription) loadingDescription.textContent = '正在處理圖片下載，請稍候...';
        if (progressText) progressText.textContent = '準備下載中...';
        if (progressFill) progressFill.style.width = '50%';
        
    } else {
        // 隱藏loading overlay
        if (loadingOverlay) {
            loadingOverlay.classList.remove('show');
            document.body.style.overflow = '';
        }
    }
}

// 初始化事件監聽器
document.addEventListener('DOMContentLoaded', function() {
    initializeImageSearch();
}); 