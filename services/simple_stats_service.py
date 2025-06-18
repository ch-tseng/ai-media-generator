import os
import json
import sqlite3
from datetime import datetime, date
from pathlib import Path

class SimpleStatsService:
    """簡單的統計記錄服務"""
    
    def __init__(self):
        # 創建數據目錄
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        
        # SQLite 數據庫路徑
        self.db_path = self.data_dir / 'stats.db'
        
        # 初始化數據庫
        self._init_database()
    
    def _init_database(self):
        """初始化數據庫表格"""
        try:
            # 確保資料庫檔案不存在損壞的情況
            if self.db_path.exists():
                # 嘗試打開檢查是否可用
                try:
                    test_conn = sqlite3.connect(self.db_path, timeout=10.0)
                    test_conn.execute('SELECT 1')
                    test_conn.close()
                except sqlite3.Error:
                    # 如果資料庫損壞，刪除重建
                    print("⚠️ 資料庫檔案可能損壞，正在重建...")
                    self.db_path.unlink()
            
            # 使用 timeout 和 check_same_thread=False 來避免鎖定問題
            conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
            conn.execute('PRAGMA journal_mode=WAL')  # 使用 WAL 模式避免鎖定
            cursor = conn.cursor()
            
            # 創建生成記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generation_type TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT,
                    generation_time REAL,
                    file_count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ 資料庫初始化完成")
            
        except sqlite3.Error as e:
            print(f"❌ 資料庫初始化失敗: {e}")
            # 如果還是失敗，嘗試移除檔案重建
            if self.db_path.exists():
                try:
                    self.db_path.unlink()
                    print("🔄 已刪除損壞的資料庫檔案，請重新啟動應用程式")
                except Exception as cleanup_error:
                    print(f"❌ 清理資料庫檔案失敗: {cleanup_error}")
            raise e
        except Exception as e:
            print(f"❌ 資料庫初始化發生未知錯誤: {e}")
            raise e
    
    def record_generation(self, generation_type, prompt, status, model_name=None, generation_time=None, file_count=0):
        """記錄生成活動"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO generations (generation_type, prompt, status, model_name, generation_time, file_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (generation_type, prompt[:500], status, model_name, generation_time, file_count))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"記錄生成活動失敗: {e}")
    
    def get_statistics(self):
        """獲取統計資訊"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
            cursor = conn.cursor()
            
            # 總生成次數
            cursor.execute('SELECT COUNT(*) FROM generations')
            total_generations = cursor.fetchone()[0]
            
            # 今日生成次數
            today = date.today().isoformat()
            cursor.execute('SELECT COUNT(*) FROM generations WHERE DATE(created_at) = ?', (today,))
            today_generations = cursor.fetchone()[0]
            
            # 圖像生成次數
            cursor.execute('SELECT COUNT(*) FROM generations WHERE generation_type = "image"')
            image_generations = cursor.fetchone()[0]
            
            # 影片生成次數
            cursor.execute('SELECT COUNT(*) FROM generations WHERE generation_type = "video"')
            video_generations = cursor.fetchone()[0]
            
            # 成功率
            cursor.execute('SELECT COUNT(*) FROM generations WHERE status = "success"')
            success_count = cursor.fetchone()[0]
            success_rate = (success_count / total_generations * 100) if total_generations > 0 else 0
            
            conn.close()
            
            return {
                'total_generations': total_generations,
                'today_generations': today_generations,
                'image_generations': image_generations,
                'video_generations': video_generations,
                'success_rate': round(success_rate, 2)
            }
        except Exception as e:
            print(f"獲取統計資訊失敗: {e}")
            return {
                'total_generations': 0,
                'today_generations': 0,
                'image_generations': 0,
                'video_generations': 0,
                'success_rate': 0
            }
    
    def get_recent_generations(self, limit=10):
        """獲取最近的生成記錄"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT generation_type, prompt, status, created_at, model_name, generation_time
                FROM generations
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            generations = []
            for row in rows:
                generations.append({
                    'generation_type': row[0],
                    'prompt': row[1],
                    'status': row[2],
                    'created_at': row[3],
                    'model_name': row[4],
                    'generation_time': row[5]
                })
            
            return generations
        except Exception as e:
            print(f"獲取生成記錄失敗: {e}")
            return []
    
    def cleanup_old_records(self, days=30):
        """清理舊記錄"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM generations 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
        except Exception as e:
            print(f"清理舊記錄失敗: {e}")
            return 0
    
    def reset_database(self):
        """重置資料庫（刪除並重建）"""
        try:
            if self.db_path.exists():
                self.db_path.unlink()
                print("✅ 已刪除舊資料庫檔案")
            
            self._init_database()
            print("✅ 資料庫重置完成")
            return True
        except Exception as e:
            print(f"❌ 資料庫重置失敗: {e}")
            return False 