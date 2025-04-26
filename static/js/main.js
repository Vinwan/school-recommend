// 获取API地址
function getApiUrl() {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const localApiUrl = `http://${window.location.hostname}:8066/api/recommend`;
    const remoteApiUrl = 'http://124.223.109.134:8066/api/recommend';
    return isLocalhost ? localApiUrl : remoteApiUrl;
}

// API 调用相关函数
async function getRecommendations() {
    const score = document.getElementById('score').value;
    const selectedGroup = document.querySelector('input[name="group"]:checked').value;
    
    if (!score || score < 0 || score > 750) {
        alert('请输入有效的分数（0-750）');
        return;
    }

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div style="text-align: center; color: #86868b; padding: 20px;">正在查询...</div>';

    try {
        const apiUrl = getApiUrl();
        console.log('使用的API地址:', apiUrl);

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': window.location.origin
            },
            credentials: 'omit',
            body: JSON.stringify({ 
                score: parseFloat(score),
                group: selectedGroup
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.success && data.data) {
            // 判断分数是否大于等于680
            if (parseFloat(score) >= 680) {
                // 只显示四所顶尖高校
                const topSchools = ['清华大学', '北京大学', '上海交通大学', '复旦大学'];
                const filteredData = {
                    chong: data.data.chong ? data.data.chong.filter(school => topSchools.includes(school.院校名称)) : [],
                    wen: data.data.wen ? data.data.wen.filter(school => topSchools.includes(school.院校名称)) : [],
                    bao: data.data.bao ? data.data.bao.filter(school => topSchools.includes(school.院校名称)) : []
                };
                displayResults(filteredData, score);
            } else {
                displayResults(data.data, score);
            }
        } else {
            resultsDiv.innerHTML = '<div style="text-align: center; color: #86868b; padding: 20px;">未找到符合条件的院校</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = `<div style="text-align: center; color: #86868b; padding: 20px;">请求失败：${error.message || '未知错误'}</div>`;
    }
}

// 展示结果相关函数
function displayResults(schools, score) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    
    // 添加分数说明
    resultsDiv.innerHTML += `
        <div class="score-explanation">
            <p>您的分数：<strong>${score}</strong></p>
            <p class="category-explanation">
                <span class="category-tag chong">冲</span>：分数线在 ${Number(score) + 5} 分以上的学校
                <span class="category-tag wen">稳</span>：分数线在 ${Number(score) - 3} 至 ${score} 分之间的学校
                <span class="category-tag bao">保</span>：分数线在 ${Number(score) - 10} 分左右的学校
            </p>
        </div>
    `;

    // 显示"冲"的院校
    if (schools.chong && schools.chong.length > 0) {
        resultsDiv.innerHTML += `<h2 class="category-title chong-title">冲刺院校</h2>`;
        schools.chong.forEach(school => {
            displaySchoolCard(school, resultsDiv);
        });
    }

    // 显示"稳"的院校
    if (schools.wen && schools.wen.length > 0) {
        resultsDiv.innerHTML += `<h2 class="category-title wen-title">稳妥院校</h2>`;
        schools.wen.forEach(school => {
            displaySchoolCard(school, resultsDiv);
        });
    }

    // 显示"保"的院校
    if (schools.bao && schools.bao.length > 0) {
        resultsDiv.innerHTML += `<h2 class="category-title bao-title">保底院校</h2>`;
        schools.bao.forEach(school => {
            displaySchoolCard(school, resultsDiv);
        });
    }
    
    // 如果所有类别都没有学校
    if ((!schools.chong || schools.chong.length === 0) && 
        (!schools.wen || schools.wen.length === 0) && 
        (!schools.bao || schools.bao.length === 0)) {
        resultsDiv.innerHTML += '<div style="text-align: center; color: #86868b; padding: 20px;">未找到符合条件的院校</div>';
    }
}

// 显示单个学校卡片
function displaySchoolCard(school, container) {
    let majors = [];
    if (typeof school.推荐专业 === 'string') {
        majors = school.推荐专业.split(',').map(m => m.trim());
    } else if (Array.isArray(school.推荐专业)) {
        majors = school.推荐专业;
    }

    // 处理标签，优先显示985标签
    const tags = school.标签 || [];
    const tagsHtml = tags.map(tag => {
        // 如果学校有985标签，就不显示211标签
        if (tags.includes('985') && tag === '211') {
            return '';
        }
        if (tag === '985') return '<span class="tag tag-985">985</span>';
        if (tag === '211') return '<span class="tag tag-211">211</span>';
        // 处理保研率标签
        if (tag && !isNaN(tag)) {
            return `<span class="tag tag-postgraduate">保研率${tag}%</span>`;
        }
        return `<span class="tag">${tag}</span>`;
    }).filter(tag => tag !== '').join('');

    // 只有当有推荐专业时才显示专业部分
    const majorsSection = majors.length > 0 ? `
        <div class="majors">
            <p><strong>推荐专业：</strong></p>
            <div class="major-tags">
                ${majors.map(major => `<span class="major-tag">${major}</span>`).join('')}
            </div>
        </div>
    ` : '';

    container.innerHTML += `
        <div class="school-card ${school.类别}-card">
            <h3>${school.院校名称}</h3>
            ${tagsHtml ? `<div class="tags">${tagsHtml}</div>` : ''}
            <div class="school-info">
                <p><strong>省份：</strong>${school.省份}</p>
                <p><strong>专业组：</strong>${school.专业组名称}</p>
                <p><strong>投档线：</strong>${school.投档线}</p>
                <p><strong>最低投档排名：</strong>${school.最低投档排名}</p>
            </div>
            ${majorsSection}
        </div>
    `;
}

// 添加组别切换事件监听
document.querySelectorAll('input[name="group"]').forEach(radio => {
    radio.addEventListener('change', function() {
        // 清空输入框
        document.getElementById('score').value = '';
        
        // 清空结果区域并只显示欢迎图片
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="welcome-container">
                <img src="/static/images/background.svg" alt="欢迎" class="welcome-image">
            </div>
        `;
    });
});

// 页面加载时显示欢迎图片
document.addEventListener('DOMContentLoaded', function() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="welcome-container">
            <img src="/static/images/background.svg" alt="欢迎" class="welcome-image">
        </div>
    `;
});