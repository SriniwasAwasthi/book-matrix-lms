import os
import shutil

def sync():
    src = r"e:\W c One Drive\MY THINKING\DBMS\library-system-BACKUP-2026-05-11_22-39"
    dst = r"E:\W c One Drive\ADA\1. 1st priority"
    
    print(f"Synchronizing from: {src}")
    print(f"Synchronizing to: {dst}")
    
    if not os.path.exists(src):
        print("Source path does not exist!")
        return
        
    os.makedirs(dst, exist_ok=True)
    
    ignore_patterns = shutil.ignore_patterns('__pycache__', '.git', '*.pyc', 'sync_files.py', 'migrate_db.py')
    
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        
        # Don't copy scratch scripts that are specific to sync
        if item in ['sync_to_1_1st_priority.py']:
            continue
            
        if os.path.isdir(s):
            # If directory exists in destination, remove it first to do a clean sync
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d, ignore=ignore_patterns)
            print(f"Synced Directory: {item}")
        else:
            shutil.copy2(s, d)
            print(f"Synced File: {item}")
                
    print("Codebase synchronization to '1. 1st priority' completed successfully!")

if __name__ == '__main__':
    sync()
