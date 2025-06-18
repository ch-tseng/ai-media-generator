import os
from flask import session
import hashlib

class SimpleAdminService:
    """簡單的管理員認證服務"""
    
    def __init__(self):
        # 從環境變數獲取管理員帳戶設定
        self.admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        self.admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
    def authenticate_admin(self, username, password):
        """驗證管理員登入"""
        if username == self.admin_username and password == self.admin_password:
            # 設定管理員會話
            session['is_admin'] = True
            session['admin_username'] = username
            session.permanent = True
            return {
                'success': True,
                'message': '管理員登入成功',
                'redirect': '/admin'
            }
        else:
            return {
                'success': False,
                'message': '帳戶或密碼錯誤'
            }
    
    def is_admin_authenticated(self):
        """檢查是否已經以管理員身份登入"""
        return session.get('is_admin', False)
    
    def get_admin_username(self):
        """獲取當前管理員用戶名"""
        return session.get('admin_username', None)
    
    def logout_admin(self):
        """管理員登出"""
        session.pop('is_admin', None)
        session.pop('admin_username', None)
        return {
            'success': True,
            'message': '已成功登出'
        }
    
    def require_admin_auth(self):
        """裝飾器：要求管理員認證"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.is_admin_authenticated():
                    from flask import redirect, url_for
                    return redirect(url_for('admin_login'))
                return func(*args, **kwargs)
            wrapper.__name__ = func.__name__
            return wrapper
        return decorator 