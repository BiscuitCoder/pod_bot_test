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

        # 提取基础信息
        basic_info = {}
        funding_info = {}
        milestones = []
        start_date = None
        end_date = None
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            
            # 检测当前部分
            if line.startswith('## '):
                current_section = line[3:].strip()
                continue
                
            # 解析基础信息
            if current_section == '1. 基础信息':
                if line.startswith('- 项目名称：'):
                    basic_info['project_name'] = line[7:].strip()
                elif line.startswith('- 负责人：'):
                    basic_info['owner'] = line[6:].strip()
                elif line.startswith('- 关联主线：'):
                    basic_info['related_line'] = line[7:].strip()
                    
            # 解析资金申请
            elif current_section == '3. 资金申请':
                if line.startswith('- 联系方式：'):
                    funding_info['contact'] = line[7:].strip()
                elif line.startswith('- 申请金额：'):
                    amount_str = line[7:].strip().replace(' USDT', '')
                    try:
                        funding_info['amount'] = int(amount_str)
                    except ValueError:
                        funding_info['amount'] = 0
                elif line.startswith('- 资金用途说明：'):
                    funding_info['usage'] = line[9:].strip()
                    
            # 解析Milestone计划
            elif current_section == '4. Milestone 计划':
                if '|' in line and '时间节点' not in line and '---' not in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        date = parts[1].strip()
                        goal = parts[2].strip()
                        amount_str = parts[3].strip()
                        try:
                            amount = int(amount_str)
                        except ValueError:
                            amount = 0
                            
                        milestone = {
                            'date': date,
                            'goal': goal,
                            'amount': amount
                        }
                        milestones.append(milestone)
                        
                        # 更新起止时间
                        if not start_date or date < start_date:
                            start_date = date
                        if not end_date or date > end_date:
                            end_date = date
                
        return {
            'title': title,
            'content': content,
            'basic_info': basic_info,
            'funding': funding_info,
            'milestones': milestones,
            'timeline': {
                'start_date': start_date,
                'end_date': end_date
            }
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
        # 过滤掉template.md
        if file_name == 'template.md':
            continue
            
        file_data = parse_markdown_file(file_path)
        
        if file_data:
            pods_data.append({
                'file': file_name,
                'title': file_data['title'],
                'content': file_data['content'],
                'basic_info': file_data['basic_info'],
                'funding': file_data['funding'],
                'milestones': file_data['milestones'],
                'timeline': file_data['timeline']
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
        },
        'total_funding': sum(pod['funding']['amount'] for pod in pods_data),
        'milestone_stats': {
            'total_milestones': sum(len(pod['milestones']) for pod in pods_data),
            'avg_milestone_amount': sum(
                sum(m['amount'] for m in pod['milestones'])
                for pod in pods_data
            ) / sum(len(pod['milestones']) for pod in pods_data)
            if pods_data else 0
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
        os.makedirs('docs', exist_ok=True)
        with open('docs/data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def load_data():
    """从 data.json 加载数据"""
    try:
        with open('docs/data.json', 'r', encoding='utf-8') as f:
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