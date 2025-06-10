#!/usr/bin/env python3
import os
import json
import glob
import subprocess
from datetime import datetime
from collections import defaultdict

def get_git_info():
    """获取 Git 信息"""
    try:
        # 获取当前分支
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
        
        # 获取最新提交信息
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        commit_date = subprocess.check_output(['git', 'log', '-1', '--format=%cd']).decode().strip()
        commit_author = subprocess.check_output(['git', 'log', '-1', '--format=%an']).decode().strip()
        
        return {
            'branch': branch,
            'commit': commit_hash,
            'date': commit_date,
            'author': commit_author
        }
    except Exception as e:
        print(f"Error getting git info: {e}")
        return None

def parse_markdown_file(file_path):
    """解析 Markdown 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取标题
        title = None
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break
                
        return {
            'title': title,
            'content': content
        }
    except Exception as e:
        print(f"Error parsing markdown file {file_path}: {e}")
        return None

def collect_pods_data():
    """收集所有 Pods 数据"""
    pods_data = []
    pod_files = glob.glob('pods/*.md')
    
    for file_path in pod_files:
        file_name = os.path.basename(file_path)
        file_data = parse_markdown_file(file_path)
        
        if file_data:
            pods_data.append({
                'file': file_name,
                'title': file_data['title'],
                'content': file_data['content']
            })
    
    return pods_data

def calculate_statistics(pods_data):
    """计算统计数据"""
    stats = {
        'total_pods': len(pods_data),
        'last_updated': datetime.now().isoformat(),
        'pod_list': [pod['file'] for pod in pods_data],
        'titles': [pod['title'] for pod in pods_data if pod['title']],
        'content_lengths': {
            pod['file']: len(pod['content'])
            for pod in pods_data
        }
    }
    
    # 计算内容长度统计
    if stats['content_lengths']:
        lengths = list(stats['content_lengths'].values())
        stats['content_stats'] = {
            'min_length': min(lengths),
            'max_length': max(lengths),
            'avg_length': sum(lengths) / len(lengths)
        }
    
    return stats

def save_data(data):
    """保存数据到 data.json"""
    try:
        os.makedirs('dist', exist_ok=True)
        with open('dist/data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def load_data():
    """从 data.json 加载数据"""
    try:
        with open('dist/data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def update_data():
    """更新数据文件"""
    # 获取 Git 信息
    git_info = get_git_info()
    
    # 收集 Pods 数据
    pods_data = collect_pods_data()
    
    # 计算统计数据
    stats = calculate_statistics(pods_data)
    
    # 合并所有数据
    data = {
        'git': git_info,
        'pods': pods_data,
        'stats': stats,
        'last_updated': datetime.now().isoformat()
    }
    
    # 保存数据
    return save_data(data)

if __name__ == '__main__':
    update_data() 