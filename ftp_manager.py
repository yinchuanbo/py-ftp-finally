import os
import sys
import json
import subprocess
import hashlib
import pysftp
import tqdm
import re
from pathlib import Path
from dotenv import load_dotenv
import io

# Global Configuration
GLOBAL_PATH = "D:\\PROJECT\\"

# Language Configuration
LANGUAGES = {
    "ar": "ar.makevideoclip.com",
    "it": "it.makevideoclip.com",
    "es": "es.makevideoclip.com",
    "fr": "fr.makevideoclip.com",
    "jp": "jp.makevideoclip.com",
    "pt": "pt.makevideoclip.com",
    "de": "de.makevideoclip.com",
    "en": "pc.makevideoclip.com",
    "tw": "tw.makevideoclip.com",
    "kr": "kr.makevideoclip.com",
}

# Path Configuration
PREVIEW = "\\preview\\"
TEMPLATES = "\\templates\\new-template\\"

# Build Path Configuration
local_paths = {}
local_list_test = {}
local_list_pro = {}
test_folder_list = {}
pro_folder_list = {}

for key, value in LANGUAGES.items():
    local_paths[key] = f"{GLOBAL_PATH}{value}"
    local_list_test[key] = f"{GLOBAL_PATH}{value}{PREVIEW}"
    local_list_pro[key] = f"{GLOBAL_PATH}{value}{TEMPLATES}"
    test_folder_list[key] = f"/html/{key}-test.vidnoz.com/"
    if key == "en":
        pro_folder_list[key] = "/html/manage.vidnoz.com/templates/new-template/"
    else:
        pro_folder_list[key] = f"/html/manage-{key}.vidnoz.com/templates/new-template/"

# Connection Configuration
TEST_CONN = {
    "host": "3.237.60.56",
    "port": 22,
    "username": "ftpuser",
    "password": "zhm8JMWwPQDLc0aG"
}

PRO_CONN = {
    "host": "manage.vidnoz.com",
    "port": 22,
    "username": "ftpuser",
    "password": "kIEmTPdyhIdnjJ2s"
}

# Calculate file hash
def file_hash(file_path=None, file_content=None):
    """Calculate file hash value"""
    h = hashlib.sha256()
    
    if file_path:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
    elif file_content:
        h.update(file_content)
    
    return h.hexdigest()

# Scan folder
def scan_folder_sync(folder_path):
    """Recursively scan folder, return list of all files"""
    files_arr = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if "\\img\\" in file_path:
                p = file_path.split("\\img\\")[1]
                p = f"img\\{p}"
                p = p.replace("\\", "/")
                files_arr.append(p)
    return files_arr

# Get Git commit file names
def get_all_commit_names(commit_list=None, lan_path=None, last=None):
    """Get file list from specified commits or recent commits"""
    file_names_arr = []
    
    if commit_list:
        for commit in commit_list:
            try:
                cmd = f'git -C {lan_path} log -1 {commit} --name-only --pretty=format:'
                stdout = subprocess.check_output(cmd, shell=True).decode('utf-8')
                
                for file_name in stdout.split('\n'):
                    if not file_name or "/Dev/" in file_name:
                        continue
                        
                    is_test = (os.environ.get('NODE_ENV', '').strip() == 'test')
                    
                    if is_test and "lan.json" in file_name:
                        continue
                    
                    if is_test and "tpl/" in file_name:
                        fn = file_name.split("tpl/")[1]
                        file_name = fn.replace(".tpl", ".html")
                    
                    file_name = file_name.replace("templates/new-template/", "")
                    file_names_arr.append(file_name)
            except Exception as e:
                print(f"Error executing Git command: {str(e)}")
    else:
        try:
            # Check staging area changes
            cmd = f'git -C {lan_path} diff --cached --name-only'
            stdout = subprocess.check_output(cmd, shell=True).decode('utf-8')
            
            # If no changes in staging area, check recent commits
            if not stdout.strip():
                cmd = f'git -C {lan_path} log {last} --name-only --pretty=format:'
                stdout = subprocess.check_output(cmd, shell=True).decode('utf-8')
            
            for file_name in stdout.split('\n'):
                if not file_name or "/Dev/" in file_name:
                    continue
                    
                is_test = (os.environ.get('NODE_ENV', '').strip() == 'test')
                
                if is_test and "lan.json" in file_name:
                    continue
                
                if is_test and "tpl/" in file_name:
                    fn = file_name.split("tpl/")[1]
                    file_name = fn.replace(".tpl", ".html")
                
                file_name = file_name.replace("templates/new-template/", "")
                file_names_arr.append(file_name)
        except Exception as e:
            print(f"Error executing Git command: {str(e)}")
    
    return file_names_arr

# Get file list
def get_files():
    """Get list of files to upload and save to output.py file"""
    # Determine environment
    env_file = '.env.pro'
    if os.environ.get('NODE_ENV', '').strip() == 'test':
        env_file = '.env.test'
    
    # Load environment variables
    load_dotenv(env_file)
    
    # Get configuration for specific languages
    only_lan = []
    if os.environ.get('onlyLan'):
        only_lan = [lang.strip() for lang in os.environ.get('onlyLan').split(',') if lang.strip()]
    
    # Collect all data
    all_data = {}
    
    for lan_name, lan_path in local_paths.items():
        # Skip if language specified and current language not in list
        if only_lan and lan_name not in only_lan:
            continue
        
        lan_commit = f"{lan_name}commit"
        commit_list = []
        last = -1
        
        cur_commit = os.environ.get(lan_commit)
        if cur_commit:
            if '-' in cur_commit:
                last = int(cur_commit)
            else:
                commit_list = cur_commit.split(',')
                all_data[lan_name] = get_all_commit_names(commit_list, lan_path)
                continue
        
        all_data[lan_name] = get_all_commit_names(None, lan_path, last)
    
    # Filter duplicate items
    if os.environ.get('isFilter') == 'true':
        for key in all_data:
            all_data[key] = list(set(all_data[key]))
    
    # Save to file
    with open('output.py', 'w') as f:
        f.write(f"# Auto-generated file list\n\nOUTPUT = {json.dumps(all_data, indent=2)}")
    
    print("Data successfully written to output.py file")
    return all_data

# Upload files
def upload_files(output_data=None):
    """Upload files to FTP server"""
    # Determine environment and configuration
    is_test = (os.environ.get('NODE_ENV', '').strip() == 'test')
    conn = TEST_CONN if is_test else PRO_CONN
    local_list = local_list_test if is_test else local_list_pro
    dev_list = test_folder_list if is_test else pro_folder_list
    
    # If output data not provided, try to import from output file
    if output_data is None:
        try:
            from output import OUTPUT
            output_data = OUTPUT
        except ImportError:
            print("Output file not found, please run get_files() first")
            return

    # Initialize SFTP client (disable host key checking to simplify process)
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None  # Disable host key checking
    
    upload_success = True
    file_not_found_errors = []
    
    try:
        with pysftp.Connection(
            host=conn['host'],
            port=conn['port'],
            username=conn['username'], 
            password=conn['password'],
            cnopts=cnopts
        ) as sftp:
            img_has_path = []
            
            # Upload regular files
            if output_data:
                for key, vals in output_data.items():
                    if not vals:
                        continue
                    
                    print(f"Uploading files for {key}...")
                    with tqdm.tqdm(total=len(vals), desc=f"Upload progress for {key}") as pbar:
                        for file_path in vals:
                            try:
                                local_file_path = f"{local_list[key]}{file_path.replace('/', os.path.sep)}"
                                remote_file_path = f"{dev_list[key]}{file_path}"
                                
                                # Check if local file exists
                                if not os.path.exists(local_file_path):
                                    file_not_found_errors.append(local_file_path)
                                    print(f"Error: File not found - {local_file_path}")
                                    pbar.update(1)
                                    upload_success = False
                                    continue
                                
                                # Check and create remote folder
                                remote_dir = os.path.dirname(remote_file_path)
                                if remote_dir not in img_has_path:
                                    try:
                                        sftp.makedirs(remote_dir)
                                        img_has_path.append(remote_dir)
                                    except Exception:
                                        # Directory may already exist
                                        pass
                                
                                # Upload file
                                sftp.put(local_file_path, remote_file_path)
                                
                                # Verify file size
                                remote_size = sftp.stat(remote_file_path).st_size
                                local_size = os.path.getsize(local_file_path)
                                
                                if remote_size != local_size:
                                    print(f"File uploaded but size mismatch, need to re-upload - {local_file_path}")
                                    upload_success = False
                                else:
                                    # Validate content for specific file types
                                    file_ext = os.path.splitext(local_file_path)[1].lower()
                                    if file_ext in ['.js', '.css', '.scss', '.tpl', '.html', '.json']:
                                        local_hash = file_hash(file_path=local_file_path)
                                        
                                        # Get remote file content for hash comparison
                                        with sftp.open(remote_file_path, 'rb') as f:
                                            remote_content = f.read()
                                        remote_hash = file_hash(file_content=remote_content)
                                        
                                        if local_hash != remote_hash:
                                            print(f"File uploaded but content mismatch, need to re-upload - {local_file_path}")
                                            upload_success = False
                            
                            except Exception as e:
                                print(f"Error uploading file: {str(e)} - {local_file_path}")
                                upload_success = False
                            
                            pbar.update(1)
            
            if upload_success and not file_not_found_errors:
                print("All files uploaded successfully")
            elif not upload_success and file_not_found_errors:
                print("Upload completed with errors. Some files were not found:")
                for file in file_not_found_errors[:5]:  # Show first 5 errors
                    print(f"  - {file}")
                if len(file_not_found_errors) > 5:
                    print(f"  ... and {len(file_not_found_errors) - 5} more")
                print("\nPlease check if the files exist in the specified paths.")
            else:
                print("Upload completed with some errors")
    
    except Exception as e:
        print(f"Failed to connect to FTP server: {str(e)}")
        print("Upload failed")

# Main function
def main():
    """Main function, execute operation based on parameters"""
    if len(sys.argv) < 2:
        print("Usage: python ftp_manager.py [get|upload] [test|pro]")
        print("  get:    Get file list")
        print("  upload: Upload files")
        print("  test:   Test environment")
        print("  pro:    Production environment")
        return
    
    # Set environment
    if len(sys.argv) > 2:
        os.environ['NODE_ENV'] = sys.argv[2]
    
    # Execute operation
    if sys.argv[1] == 'get':
        get_files()
    elif sys.argv[1] == 'upload':
        upload_files()
    else:
        print(f"Unknown operation: {sys.argv[1]}")

if __name__ == "__main__":
    main() 