// 調試模態視窗關閉問題的腳本

// 調試函數：檢查模態視窗狀態
function debugModalState() {
    console.log('=== 模態視窗調試信息 ===');
    
    const modal = document.getElementById('image-preview-modal');
    if (modal) {
        console.log('✅ 模態視窗元素存在');
        console.log('   display:', window.getComputedStyle(modal).display);
        console.log('   visibility:', window.getComputedStyle(modal).visibility);
        console.log('   z-index:', window.getComputedStyle(modal).zIndex);
        console.log('   classList:', Array.from(modal.classList));
    } else {
        console.log('❌ 模態視窗元素不存在');
    }
    
    const closeButton = document.querySelector('#image-preview-modal .modal-close');
    if (closeButton) {
        console.log('✅ 關閉按鈕存在');
        console.log('   onclick屬性:', closeButton.getAttribute('onclick'));
        console.log('   display:', window.getComputedStyle(closeButton).display);
        console.log('   pointer-events:', window.getComputedStyle(closeButton).pointerEvents);
        console.log('   z-index:', window.getComputedStyle(closeButton).zIndex);
    } else {
        console.log('❌ 關閉按鈕不存在');
    }
    
    // 檢查全域函數
    console.log('🔍 全域函數檢查:');
    console.log('   window.closeModal 存在:', typeof window.closeModal === 'function');
    console.log('   closeModal 存在:', typeof closeModal === 'function');
    console.log('   showModal 存在:', typeof showModal === 'function');
    
    console.log('========================');
}

// 增強的 closeModal 函數（用於調試）
function debugCloseModal(modalId) {
    console.log(`🔧 嘗試關閉模態視窗: ${modalId}`);
    
    const modal = document.getElementById(modalId);
    if (modal) {
        console.log('✅ 找到模態視窗元素');
        console.log('   關閉前 display:', window.getComputedStyle(modal).display);
        console.log('   關閉前 classList:', Array.from(modal.classList));
        
        // 執行關閉操作
        modal.classList.remove('show');
        modal.style.display = 'none';
        
        console.log('   關閉後 display:', window.getComputedStyle(modal).display);
        console.log('   關閉後 classList:', Array.from(modal.classList));
        
        // 恢復背景滾動
        document.body.style.overflow = 'auto';
        
        console.log('✅ 模態視窗應該已關閉');
    } else {
        console.error(`❌ 找不到模態視窗: ${modalId}`);
    }
}

// 手動測試函數
function testModalFunctions() {
    console.log('🧪 開始測試模態視窗功能...');
    
    // 測試開啟
    console.log('1. 測試開啟模態視窗');
    if (typeof showModal === 'function') {
        showModal('image-preview-modal');
        setTimeout(() => {
            debugModalState();
            
            // 測試關閉
            console.log('2. 測試關閉模態視窗');
            debugCloseModal('image-preview-modal');
            
            setTimeout(() => {
                debugModalState();
            }, 100);
        }, 500);
    } else {
        console.error('❌ showModal 函數不存在');
    }
}

// 監聽點擊事件的調試
function addClickDebugger() {
    const modal = document.getElementById('image-preview-modal');
    if (modal) {
        // 為整個模態視窗添加點擊監聽器
        modal.addEventListener('click', function(e) {
            console.log('🖱️ 模態視窗被點擊:', e.target);
            console.log('   點擊的元素 class:', e.target.className);
            console.log('   點擊的元素 tagName:', e.target.tagName);
            
            if (e.target.classList.contains('modal-close')) {
                console.log('✅ 點擊了關閉按鈕');
                e.preventDefault();
                debugCloseModal('image-preview-modal');
            }
        });
        
        console.log('✅ 已添加點擊調試器');
    }
}

// 頁面載入後自動執行調試
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 模態視窗調試器已載入');
    
    // 添加全域調試函數
    window.debugModalState = debugModalState;
    window.debugCloseModal = debugCloseModal;
    window.testModalFunctions = testModalFunctions;
    window.addClickDebugger = addClickDebugger;
    
    // 自動添加點擊調試器
    setTimeout(addClickDebugger, 1000);
    
    console.log('💡 可用的調試函數:');
    console.log('   debugModalState() - 檢查模態視窗狀態');
    console.log('   debugCloseModal(modalId) - 調試關閉模態視窗');
    console.log('   testModalFunctions() - 測試開啟/關閉功能');
    console.log('   addClickDebugger() - 添加點擊事件調試');
}); 