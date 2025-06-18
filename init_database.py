#!/usr/bin/env python3
"""
資料庫初始化腳本
如果遇到 "database is locked" 錯誤，可以運行此腳本來修復
"""

import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

from services.simple_stats_service import SimpleStatsService

def main():
    """主函數"""
    print("🔄 開始初始化資料庫...")
    
    try:
        # 創建服務實例（這會自動初始化資料庫）
        stats_service = SimpleStatsService()
        print("✅ 資料庫初始化成功！")
        
        # 測試資料庫功能
        stats = stats_service.get_statistics()
        print(f"📊 資料庫狀態: {stats}")
        
    except Exception as e:
        print(f"❌ 資料庫初始化失敗: {e}")
        print("\n🔧 嘗試重置資料庫...")
        
        try:
            # 嘗試強制重置
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / 'stats.db'
            
            if db_path.exists():
                db_path.unlink()
                print("✅ 已刪除損壞的資料庫檔案")
            
            # 重新初始化
            stats_service = SimpleStatsService()
            print("✅ 資料庫重置成功！")
            
        except Exception as reset_error:
            print(f"❌ 資料庫重置也失敗了: {reset_error}")
            print("\n💡 請檢查:")
            print("  1. 檔案權限是否正確")
            print("  2. data/ 目錄是否可寫")
            print("  3. 是否有其他程序正在使用資料庫")
            sys.exit(1)

if __name__ == "__main__":
    main() 