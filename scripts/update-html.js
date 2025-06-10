const fs = require('fs');
const path = require('path');
const { collectPodsData, loadData } = require('./utils');

const INDEX_HTML = path.join(__dirname, '../dist/index.html');

function updateIndexHtml() {
    try {
        console.log('开始更新 index.html...');

        // 尝试从 data.json 加载数据
        let data = loadData();

        // 如果没有数据或数据过期，重新收集数据
        if (!data) {
            console.log('未找到数据文件，开始收集数据...');
            data = collectPodsData();
        }

        let html = fs.readFileSync(INDEX_HTML, 'utf-8');

        // 更新统计数据
        html = html.replace(
            /<div class="stat-value" id="totalPods">.*?<\/div>/,
            `<div class="stat-value" id="totalPods">${data.stats.total}</div>`
        );
        html = html.replace(
            /<div class="stat-value" id="newPods">.*?<\/div>/,
            `<div class="stat-value" id="newPods">${data.stats.newThisMonth}</div>`
        );
        html = html.replace(
            /<div class="stat-value" id="lastUpdate">.*?<\/div>/,
            `<div class="stat-value" id="lastUpdate">${new Date(data.stats.lastUpdate).toLocaleString()}</div>`
        );
        html = html.replace(
            /<div class="stat-value" id="updateFrequency">.*?<\/div>/,
            `<div class="stat-value" id="updateFrequency">${data.stats.updateFrequency}</div>`
        );

        // 更新图表数据
        const chartsData = `
            <script>
                window.podData = ${JSON.stringify(data, null, 2)};
            </script>
        `;
        html = html.replace(
            /<script>[\s\S]*?<\/script>/,
            chartsData
        );

        // 更新 Pods 列表
        const podsList = data.pods.map(pod => `
            <div class="pod-card">
                <div class="pod-header">
                    <h2 class="pod-title">${pod.title}</h2>
                    <div class="pod-meta">
                        <div>文件名: ${pod.filename}</div>
                        <div>分类: ${pod.category}</div>
                        <div>最后修改: ${new Date(pod.modified_time).toLocaleString()}</div>
                        ${pod.git_info.message ? `
                            <div class="commit-info">
                                提交信息: ${pod.git_info.message}
                                <br>
                                提交时间: ${pod.git_info.date}
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="pod-content">
                    ${pod.content}
                </div>
            </div>
        `).join('');
        
        html = html.replace(
            /<div class="pod-list" id="podList">[\s\S]*?<\/div>/,
            `<div class="pod-list" id="podList">${podsList}</div>`
        );
        
        fs.writeFileSync(INDEX_HTML, html);
        console.log('index.html 更新完成！');
        
    } catch (error) {
        console.error('更新 index.html 失败:', error);
        process.exit(1);
    }
}

updateIndexHtml();