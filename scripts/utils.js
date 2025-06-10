const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const marked = require('marked');

// 配置
const PODS_DIR = path.join(__dirname, '../pods');
const DATA_JSON = path.join(__dirname, '../dist/data.json');

// 获取 Git 信息
function getGitInfo(filePath) {
    try {
        const relativePath = path.relative(process.cwd(), filePath);
        const gitLog = execSync(`git log -1 --pretty=format:"%h|%s|%ad" --date=format:"%Y-%m-%d %H:%M:%S" -- "${relativePath}"`, { encoding: 'utf-8' });
        const [hash, message, date] = gitLog.split('|');
        return { hash, message, date };
    } catch (error) {
        return { hash: null, message: null, date: null };
    }
}

// 解析 Markdown 文件
function parseMarkdownFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');

    let title = null;
    let category = '未分类';
    let description = '';

    // 解析元数据
    for (const line of lines) {
        if (line.startsWith('# ')) {
            title = line.substring(2).trim();
        } else if (line.startsWith('## ')) {
            title = line.substring(3).trim();
        } else if (line.startsWith('category:')) {
            category = line.substring(9).trim();
        } else if (line.startsWith('description:')) {
            description = line.substring(12).trim();
        }
    }

    // 如果没有找到标题，使用文件名
    if (!title) {
        title = path.basename(filePath, '.md');
    }

    return {
        title,
        category,
        description,
        content: marked.parse(content)
    };
}

// 收集所有 Pods 数据
function collectPodsData() {
    const pods = [];
    const categories = new Map();
    const updateDates = new Map();

    // 读取 pods 目录
    const files = fs.readdirSync(PODS_DIR);

    for (const file of files) {
        if (file.endsWith('.md')) {
            const filePath = path.join(PODS_DIR, file);
            const stats = fs.statSync(filePath);
            const gitInfo = getGitInfo(filePath);
            const { title, category, description, content } = parseMarkdownFile(filePath);

            // 更新分类统计
            categories.set(category, (categories.get(category) || 0) + 1);

            // 更新日期统计
            const dateKey = stats.mtime.toISOString().slice(0, 7); // YYYY-MM
            updateDates.set(dateKey, (updateDates.get(dateKey) || 0) + 1);

            pods.push({
                filename: file,
                title,
                category,
                description,
                content,
                modified_time: stats.mtime.toISOString(),
                git_info: gitInfo
            });
        }
    }

    // 按修改时间排序
    pods.sort((a, b) => new Date(b.modified_time) - new Date(a.modified_time));

    // 计算统计数据
    const now = new Date();
    const thisMonth = now.toISOString().slice(0, 7);
    const stats = {
        total: pods.length,
        newThisMonth: updateDates.get(thisMonth) || 0,
        lastUpdate: pods[0] ? pods[0].modified_time : '-',
        updateFrequency: updateDates.size > 0 ?
            (pods.length / updateDates.size).toFixed(1) + ' 次/月' : '-'
    };

    // 准备图表数据
    const charts = {
        updates: {
            labels: Array.from(updateDates.keys()).sort(),
            data: Array.from(updateDates.keys()).sort().map(date => updateDates.get(date))
        },
        categories: {
            labels: Array.from(categories.keys()),
            data: Array.from(categories.values())
        }
    };

    const data = {
        pods,
        stats,
        charts,
        last_updated: new Date().toISOString()
    };

    // 保存数据到 data.json
    saveData(data);

    return data;
}

// 保存数据到 data.json
function saveData(data) {
    try {
        // 确保目录存在
        const dir = path.dirname(DATA_JSON);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        // 写入数据
        fs.writeFileSync(DATA_JSON, JSON.stringify(data, null, 2));
        console.log('数据已保存到 data.json');
    } catch (error) {
        console.error('保存数据失败:', error);
        throw error;
    }
}

// 从 data.json 读取数据
function loadData() {
    try {
        if (fs.existsSync(DATA_JSON)) {
            const data = JSON.parse(fs.readFileSync(DATA_JSON, 'utf-8'));
            return data;
        }
    } catch (error) {
        console.error('读取数据失败:', error);
    }
    return null;
}

module.exports = {
    collectPodsData,
    getGitInfo,
    parseMarkdownFile,
    saveData,
    loadData
};