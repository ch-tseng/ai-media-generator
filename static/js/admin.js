// 管理區 JavaScript 功能

class AdminManager {
    constructor() {
        this.currentTab = 'users';
        this.users = [];
        this.records = [];
        this.statistics = {};
        this.init();
    }

    init() {
        // 綁定事件
        this.bindEvents();
        
        // 頁面載入時檢查是否在管理區
        if (window.location.pathname === '/admin') {
            this.loadAdminData();
        }
    }

    bindEvents() {
        // 管理區選項卡
        window.showAdminTab = (tab) => this.showAdminTab(tab);
        window.goToAdmin = () => this.goToAdmin();
        
        // 刷新按鈕
        window.refreshUsers = () => this.loadRecords();
        window.refreshRecords = () => this.loadRecords();
        window.refreshStatistics = () => this.loadStatistics();
        
        // 篩選功能
        window.filterRecords = () => this.filterRecords();
    }

    goToAdmin() {
        // 直接跳轉到管理員登入頁面
        window.location.href = '/admin/login';
    }

    async loadAdminData() {
        // 載入當前選項卡的數據
        switch (this.currentTab) {
            case 'statistics':
                this.loadStatistics();
                break;
            case 'records':
                this.loadRecords();
                break;
            default:
                this.loadStatistics();
        }
    }

    showAdminTab(tab) {
        // 更新選項卡狀態
        document.querySelectorAll('.admin-tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const targetBtn = document.querySelector(`[onclick="showAdminTab('${tab}')"]`);
        if (targetBtn) {
            targetBtn.classList.add('active');
        }
        
        // 顯示對應內容
        document.querySelectorAll('.admin-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        const targetContent = document.getElementById(`admin-${tab}`);
        if (targetContent) {
            targetContent.classList.add('active');
        }
        
        this.currentTab = tab;
        
        // 載入對應數據
        switch (tab) {
            case 'records':
                this.loadRecords();
                break;
            case 'statistics':
                this.loadStatistics();
                break;
        }
    }

    async loadRecords() {
        try {
            const response = await fetch('/api/admin/recent-generations');
            const data = await response.json();
            
            if (data.success) {
                this.records = data.generations;
                this.renderRecordsTable();
            } else {
                throw new Error(data.error || '載入生成記錄失敗');
            }
        } catch (error) {
            console.error('載入生成記錄失敗:', error);
            this.showError('載入生成記錄失敗: ' + error.message);
        }
    }

    renderRecordsTable() {
        const tbody = document.getElementById('records-table-body');
        if (!tbody) return;
        
        if (this.records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="no-data">暫無生成記錄</td></tr>';
            return;
        }
        
        tbody.innerHTML = this.records.map(record => `
            <tr>
                <td>系統用戶</td>
                <td>
                    <span class="type-badge ${record.generation_type}">
                        ${record.generation_type === 'image' ? '🖼️ 圖像' : '🎬 影片'}
                    </span>
                </td>
                <td>${this.escapeHtml(record.model_name || 'Unknown')}</td>
                <td title="${this.escapeHtml(record.prompt)}">
                    ${this.truncateText(record.prompt, 50)}
                </td>
                <td>
                    <span class="status-badge ${record.status}">
                        ${this.getStatusText(record.status)}
                    </span>
                </td>
                <td>${record.generation_time ? record.generation_time.toFixed(2) + 's' : '-'}</td>
                <td>${this.formatDateTime(record.created_at)}</td>
                <td>-</td>
                <td>-</td>
            </tr>
        `).join('');
    }

    filterRecords() {
        const filter = document.getElementById('records-filter')?.value || 'all';
        
        if (filter === 'all') {
            this.renderRecordsTable();
            return;
        }
        
        const filteredRecords = this.records.filter(record => record.generation_type === filter);
        const tbody = document.getElementById('records-table-body');
        if (!tbody) return;
        
        if (filteredRecords.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="no-data">無符合條件的記錄</td></tr>';
            return;
        }
        
        tbody.innerHTML = filteredRecords.map(record => `
            <tr>
                <td>系統用戶</td>
                <td>
                    <span class="type-badge ${record.generation_type}">
                        ${record.generation_type === 'image' ? '🖼️ 圖像' : '🎬 影片'}
                    </span>
                </td>
                <td>${this.escapeHtml(record.model_name || 'Unknown')}</td>
                <td title="${this.escapeHtml(record.prompt)}">
                    ${this.truncateText(record.prompt, 50)}
                </td>
                <td>
                    <span class="status-badge ${record.status}">
                        ${this.getStatusText(record.status)}
                    </span>
                </td>
                <td>${record.generation_time ? record.generation_time.toFixed(2) + 's' : '-'}</td>
                <td>${this.formatDateTime(record.created_at)}</td>
                <td>-</td>
                <td>-</td>
            </tr>
        `).join('');
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/admin/statistics');
            const data = await response.json();
            
            if (data.success) {
                this.statistics = data.statistics;
                this.renderStatistics();
            } else {
                throw new Error(data.error || '載入統計信息失敗');
            }
        } catch (error) {
            console.error('載入統計信息失敗:', error);
            this.showError('載入統計信息失敗: ' + error.message);
        }
    }

    renderStatistics() {
        const stats = this.statistics;
        
        this.updateStatCard('stat-total-generations', stats.total_generations || 0);
        this.updateStatCard('stat-image-generations', stats.image_generations || 0);
        this.updateStatCard('stat-video-generations', stats.video_generations || 0);
        this.updateStatCard('stat-today-generations', stats.today_generations || 0);
        this.updateStatCard('stat-success-rate', (stats.success_rate || 0) + '%');
        
        // 移除用戶相關統計（因為不再有用戶管理）
        this.updateStatCard('stat-active-users', 'N/A');
    }

    updateStatCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    formatDateTime(dateString) {
        if (!dateString) return '-';
        try {
            return new Date(dateString).toLocaleString('zh-TW');
        } catch (error) {
            return dateString;
        }
    }

    getStatusText(status) {
        switch (status) {
            case 'success':
                return '✅ 成功';
            case 'failed':
                return '❌ 失敗';
            default:
                return '❓ 未知';
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${this.escapeHtml(message)}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // 自動移除通知
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// 初始化管理器
let adminManager;
document.addEventListener('DOMContentLoaded', function() {
    adminManager = new AdminManager();
}); 