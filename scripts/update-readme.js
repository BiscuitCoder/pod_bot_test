const fs = require('fs');
const path = require('path');
const { collectPodsData, loadData } = require('./utils');

const README_PATH = path.join(__dirname, '../README.md');

function updateReadme() {
    try {
        console.log('开始更新 README.md...');

        // 尝试从 data.json 加载数据
        let data = loadData();

        // 如果没有数据或数据过期，重新收集数据
        if (!data) {
            console.log('未找到数据文件，开始收集数据...');
            data = collectPodsData();
        }

        // 生成 README 内容
        let content = '# Pods 目录\n\n';
        content += '## 文件列表\n\n';

        // 按分类组织内容
        const podsByCategory = new Map();
        data.pods.forEach(pod => {
            if (!podsByCategory.has(pod.category)) {
                podsByCategory.set(pod.category, []);
            }
            podsByCategory.get(pod.category).push(pod);
        });

        // 生成分类内容
        for (const [category, pods] of podsByCategory) {
            content += `### ${category}\n\n`;

            pods.forEach(pod => {
                content += `#### ${pod.title}\n\n`;
                content += `- 文件名: ${pod.filename}\n`;
                content += `- 最后修改: ${new Date(pod.modified_time).toLocaleString()}\n`;
                if (pod.git_info.message) {
                    content += `- 最近提交: ${pod.git_info.message}\n`;
                    content += `- 提交时间: ${pod.git_info.date}\n`;
                }
                if (pod.description) {
                    content += `- 描述: ${pod.description}\n`;
                }
                content += '\n';
            });
        }

        // 添加统计信息
        content += '## 统计信息\n\n';
        content += `- 总 Pods 数量: ${data.stats.total}\n`;
        content += `- 本月新增: ${data.stats.newThisMonth}\n`;
        content += `- 最近更新: ${new Date(data.stats.lastUpdate).toLocaleString()}\n`;
        content += `- 平均更新频率: ${data.stats.updateFrequency}\n\n`;

        // 添加最后更新时间
        content += `最后更新时间: ${new Date(data.last_updated).toLocaleString()}\n`;

        // 写入文件
        fs.writeFileSync(README_PATH, content);
        console.log('README.md 更新完成！');

    } catch (error) {
        console.error('更新 README.md 失败:', error);
        process.exit(1);
    }
}

updateReadme();