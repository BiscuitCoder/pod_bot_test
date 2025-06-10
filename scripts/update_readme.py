#!/usr/bin/env python3
import os
import glob
import json
from datetime import datetime

def get_pod_info(file_path):
    """获取Pod的详细信息"""
    info = {
        'title': '',
        'owner': '',
        'related_line': '',
        'funding': 0,
        'start_date': '',
        'end_date': ''
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        
        current_section = None
        for line in lines:
            line = line.strip()
            
            # 检测当前部分
            if line.startswith('## '):
                current_section = line[3:].strip()
                continue
                
            # 提取标题
            if line.startswith('# '):
                info['title'] = line[2:].strip()
                
            # 提取基础信息
            elif current_section == '1. 基础信息':
                if line.startswith('- 项目名称：'):
                    info['title'] = line[7:].strip()
                elif line.startswith('- 负责人：'):
                    info['owner'] = line[6:].strip()
                elif line.startswith('- 关联主线：'):
                    info['related_line'] = line[7:].strip()
                    
            # 提取资金申请
            elif current_section == '3. 资金申请':
                if line.startswith('- 申请金额：'):
                    amount_str = line[7:].strip().replace(' USDT', '')
                    try:
                        info['funding'] = int(amount_str)
                    except ValueError:
                        info['funding'] = 0
                        
            # 提取时间线
            elif current_section == '4. Milestone 计划':
                if '|' in line and '时间节点' not in line and '---' not in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        date = parts[1].strip()
                        if not info['start_date'] or date < info['start_date']:
                            info['start_date'] = date
                        if not info['end_date'] or date > info['end_date']:
                            info['end_date'] = date
    
    return info

def update_readme():
    """更新README.md文件中的动态内容"""
    # 获取所有pods目录下的.md文件
    pod_files = glob.glob('pods/*.md')
    
    # 过滤掉template.md
    pod_files = [f for f in pod_files if os.path.basename(f) != 'template.md']
    
    # 收集所有Pod信息
    pods_info = []
    for file_path in pod_files:
        pod_info = get_pod_info(file_path)
        pod_info['file'] = os.path.basename(file_path)
        pods_info.append(pod_info)
    
    # 按申请金额排序
    pods_info.sort(key=lambda x: x['funding'], reverse=True)
    
    # 读取现有的README.md
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成统计信息
    total_pods = len(pods_info)
    total_funding = sum(p['funding'] for p in pods_info)
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    stats_content = f"""- 总 Pod 数量：{total_pods}
- 总申请资金：{total_funding} USDT
- 最后更新：{last_update}"""
    
    # 生成表格内容
    table_content = """| 项目名称 | 负责人 | 关联主线 | 申请资金 | 项目周期 | 文件 |
|---------|--------|----------|----------|----------|------|"""
    
    for pod in pods_info:
        table_content += f"\n| {pod['title']} | {pod['owner']} | {pod['related_line']} | {pod['funding']} USDT | {pod['start_date']} ~ {pod['end_date']} | [{pod['file']}](pods/{pod['file']}) |"
    
    # 更新内容
    content = content.replace(
        content[content.find('<!-- BEGIN_STATS -->'):content.find('<!-- END_STATS -->') + len('<!-- END_STATS -->')],
        f'<!-- BEGIN_STATS -->\n{stats_content}\n<!-- END_STATS -->'
    )
    
    content = content.replace(
        content[content.find('<!-- BEGIN_TABLE -->'):content.find('<!-- END_TABLE -->') + len('<!-- END_TABLE -->')],
        f'<!-- BEGIN_TABLE -->\n{table_content}\n<!-- END_TABLE -->'
    )
    
    # 写回文件
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_readme() 