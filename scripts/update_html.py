#!/usr/bin/env python3
import os
import json
from datetime import datetime

def update_html():
    """更新 index.html 文件"""
    try:
        # 加载数据
        with open('dist/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 生成 HTML 内容
        html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pods 目录</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .pod {{ margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .pod h2 {{ margin-top: 0; }}
        .pod-meta {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
        .pod-content {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <h1>Pods 目录</h1>
    <p>最后更新: {data['last_updated']}</p>
    <p>Git 信息: {data['git']['branch']} - {data['git']['commit'][:7]} ({data['git']['date']})</p>
    
    <div class="pods">
"""

        # 添加每个 Pod 的内容
        for pod in data['pods']:
            html_content += f"""
        <div class="pod">
            <h2>{pod['title']}</h2>
            <div class="pod-meta">
                <p>文件: {pod['file']}</p>
            </div>
            <div class="pod-content">
                {pod['content']}
            </div>
        </div>
"""

        html_content += """
    </div>
</body>
</html>
"""
        
        # 确保 dist 目录存在
        os.makedirs('dist', exist_ok=True)
        
        # 写入 HTML 文件
        with open('dist/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return True
    except Exception as e:
        print(f"Error updating HTML: {e}")
        return False

if __name__ == '__main__':
    update_html() 