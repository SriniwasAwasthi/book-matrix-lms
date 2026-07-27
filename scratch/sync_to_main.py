import os
import shutil

def sync_to_main():
    src_dir = r"e:\W c One Drive\MY THINKING\DBMS\library-system-BACKUP-2026-05-11_22-39"
    dst_dir = r"e:\W c One Drive\MY THINKING\DBMS\MAIN\library-system-BACKUP-2026-05-11_22-39"
    
    print(f"Synchronizing codebase from: {src_dir}")
    print(f"Synchronizing codebase to: {dst_dir}")
    
    if not os.path.exists(src_dir):
        print("Source path does not exist!")
        return
        
    os.makedirs(dst_dir, exist_ok=True)
    
    # 1. Sync backend
    src_backend = os.path.join(src_dir, 'backend')
    dst_backend = os.path.join(dst_dir, 'backend')
    os.makedirs(dst_backend, exist_ok=True)
    for item in os.listdir(src_backend):
        if item != '__pycache__':
            try:
                shutil.copy2(os.path.join(src_backend, item), os.path.join(dst_backend, item))
                print(f"Synced Backend File: {item}")
            except Exception as e:
                print(f"Error copying backend file {item}: {e}")
            
    # 2. Sync frontend (individual files)
    src_frontend = os.path.join(src_dir, 'frontend')
    dst_frontend = os.path.join(dst_dir, 'frontend')
    os.makedirs(dst_frontend, exist_ok=True)
    for item in os.listdir(src_frontend):
        src_file = os.path.join(src_frontend, item)
        dst_file = os.path.join(dst_frontend, item)
        if os.path.isfile(src_file):
            try:
                shutil.copy2(src_file, dst_file)
                print(f"Synced Frontend File: {item}")
            except Exception as e:
                print(f"Error copying frontend file {item}: {e}")
        elif os.path.isdir(src_file) and item != '__pycache__':
            # recursive copy if there's any subfolder in frontend
            try:
                shutil.copytree(src_file, dst_file, dirs_exist_ok=True)
                print(f"Synced Frontend Subfolder: {item}")
            except Exception as e:
                print(f"Error copying frontend subfolder {item}: {e}")
    
    # 3. Sync database
    src_db_dir = os.path.join(src_dir, 'database')
    dst_db_dir = os.path.join(dst_dir, 'database')
    os.makedirs(dst_db_dir, exist_ok=True)
    for item in os.listdir(src_db_dir):
        if item != 'backups':
            try:
                shutil.copy2(os.path.join(src_db_dir, item), os.path.join(dst_db_dir, item))
                print(f"Synced Database File: {item}")
            except Exception as e:
                print(f"Error copying database file {item}: {e}")
            
    print("\nCodebase sync to MAIN completed successfully!")

if __name__ == '__main__':
    sync_to_main()
