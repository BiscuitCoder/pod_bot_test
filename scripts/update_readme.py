#!/usr/bin/env python3
import os
import glob

def update_readme():
    # 获取所有 pods 目录下的 .md 文件
    pod_files = glob.glob('pods/*.md')
    
    # 开始写入 README.md
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write("# Pods 目录\n\n")
        f.write("## 文件列表\n\n")
        
        for file_path in pod_files:
            file_name = os.path.basename(file_path)
            f.write(f"### {file_name}\n\n")
            
            # 读取文件内容并提取标题
            with open(file_path, 'r', encoding='utf-8') as pod_file:
                for line in pod_file:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        f.write(f"**标题**: {title}\n\n")
                        break
            
            f.write("---\n\n")

if __name__ == '__main__':
    update_readme() 