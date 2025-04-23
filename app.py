from flask import Flask, request, jsonify, render_template, make_response
import pandas as pd
import random
import os

app = Flask(__name__)

# 检查并创建示例数据
if not os.path.exists('schools.csv'):
    sample_data = {
        '院校名称': ['示例大学A', '示例大学B', '示例大学C', '示例大学D', '示例大学E'],
        '省份': ['北京', '上海', '广东', '江苏', '浙江'],
        '专业组名称': ['理工类', '理工类', '理工类', '理工类', '理工类'],
        '投档线': [500, 502, 503, 505, 508],
        '最低投档排名': [1000, 1200, 1300, 1400, 1500]
    }
    df = pd.DataFrame(sample_data)
    df.to_csv('schools.csv', index=False, encoding='utf-8')
else:
    df = pd.read_csv('schools.csv', encoding='utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST', 'OPTIONS'])
def recommend_schools():
    if request.method == 'OPTIONS':
        return make_response()

    try:
        data = request.get_json()
        if not data or 'score' not in data:
            return jsonify({
                'success': False,
                'error': '未提供分数'
            }), 400

        score = float(data['score'])
        
        # 设置分数范围（±2.5分）
        score_min = score - 2.5
        score_max = score + 2.5
        
        # 筛选符合分数范围的学校
        filtered_schools = df[
            (df['投档线'] >= score_min) & 
            (df['投档线'] <= score_max)
        ]
        
        # 如果找到的学校少于5所，扩大范围
        if len(filtered_schools) < 5:
            score_min = score - 5
            score_max = score + 5
            filtered_schools = df[
                (df['投档线'] >= score_min) & 
                (df['投档线'] <= score_max)
            ]
        
        # 随机选择5所学校
        if len(filtered_schools) > 5:
            recommended = filtered_schools.sample(n=5)
        else:
            recommended = filtered_schools
        
        # 确保数值类型正确转换为 Python 原生类型
        result = []
        for _, row in recommended.iterrows():
            school_dict = {
                '院校名称': str(row['院校名称']),
                '省份': str(row['省份']),
                '专业组名称': str(row['专业组名称']),
                '投档线': float(row['投档线']),
                '最低投档排名': int(row['最低投档排名'])
            }
            result.append(school_dict)

        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")  # 添加服务器端日志
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

if __name__ == '__main__':
    # 修改host为'0.0.0.0'以允许外部访问
    app.run(host='0.0.0.0', port=5003)