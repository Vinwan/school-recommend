// 获取API地址
function getApiUrl() {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const localApiUrl = `http://${window.location.hostname}:8066/api/recommend`;
    const remoteApiUrl = 'http://124.223.109.134:8066/api/recommend';
    return isLocalhost ? localApiUrl : remoteApiUrl;
}

// API 调用相关函数
async function getRecommendations() {
    const scoreInput = document.getElementById('score');
    const score = scoreInput.value;
    const resultsDiv = document.getElementById('results');

    if (!score || score < 0 || score > 750) {
        alert('请输入有效的分数（0-750）');
        return;
    }

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
            body: JSON.stringify({ score: parseFloat(score) })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.success && data.data && data.data.length > 0) {
            let majorRecommendations = [];
            if (data.major_recommendations && data.major_recommendations.success) {
                majorRecommendations = data.major_recommendations.data
                    .split(/[,，]/)
                    .map(major => major.trim())
                    .filter(major => major);
            }

            const schoolsWithMajors = data.data.map(school => ({
                ...school,
                推荐专业: majorRecommendations
            }));
            
            displayResults(schoolsWithMajors);
        } else {
            resultsDiv.innerHTML = '<div style="text-align: center; color: #86868b; padding: 20px;">未找到符合条件的院校</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = `<div style="text-align: center; color: #86868b; padding: 20px;">请求失败：${error.message || '未知错误'}</div>`;
    }
}

// 展示结果相关函数
function displayResults(schools) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    schools.forEach(school => {
        let majors = [];
        if (typeof school.推荐专业 === 'string') {
            majors = school.推荐专业.split(',').map(m => m.trim());
        } else if (Array.isArray(school.推荐专业)) {
            majors = school.推荐专业;
        }

        const majorsHtml = majors.map(major => 
            `<span class="major-tag">${major}</span>`
        ).join('');

        resultsDiv.innerHTML += `
            <div class="school-card">
                <h3>${school.院校名称}</h3>
                <p>省份：${school.省份}</p>
                <p>专业组：${school.专业组名称}</p>
                <p>投档线：${school.投档线}</p>
                <p>最低投档排名：${school.最低投档排名}</p>
                <div class="majors">
                    <p>推荐专业：</p>
                    ${majorsHtml}
                </div>
            </div>
        `;
    });
}