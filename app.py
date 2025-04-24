from flask import Flask, request, jsonify, render_template, make_response
app = Flask(__name__, static_folder='static')
import pandas as pd
import os
import logging
import sys
from datetime import datetime

app = Flask(__name__)

# 配置日志输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 移除 AI 服务初始化
# 检查并创建示例数据
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, 'schools.csv')

if not os.path.exists(csv_path):
    sample_data = {
        '院校名称': ['示例大学A', '示例大学B', '示例大学C', '示例大学D', '示例大学E'],
        '省份': ['北京', '上海', '广东', '江苏', '浙江'],
        '专业组名称': ['理工类', '理工类', '理工类', '理工类', '理工类'],
        '投档线': [500, 502, 503, 505, 508],
        '最低投档排名': [1000, 1200, 1300, 1400, 1500]
    }
    df = pd.DataFrame(sample_data)
    df.to_csv(csv_path, index=False, encoding='utf-8')
else:
    df = pd.read_csv(csv_path, encoding='utf-8')

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
        
        # 使用logger替换print
        logger.info("="*50)
        logger.info("请求开始处理")
        logger.info(f"请求数据: {data}")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"CSV文件路径: {csv_path}")
        logger.info(f"CSV文件是否存在: {os.path.exists(csv_path)}")
        if os.path.exists(csv_path):
            logger.info(f"CSV文件大小: {os.path.getsize(csv_path)} bytes")
            logger.info("CSV文件内容预览:")
            with open(csv_path, 'r', encoding='utf-8') as f:
                logger.info(f.read(200))  # 打印前200个字符
        logger.info(f"数据框大小: {df.shape}")
        if not df.empty:
            logger.info(f"数据框列名: {df.columns.tolist()}")
            logger.info(f"投档线范围: {df['投档线'].min()} - {df['投档线'].max()}")
            # 添加数据类型检查
            logger.info(f"投档线列的数据类型: {df['投档线'].dtype}")
            logger.info(f"投档线列的前5个值: {df['投档线'].head()}")
        logger.info("="*50)
        
        # 设置分数范围（±5分）
        score_min = score - 5
        score_max = score + 5
        
        logger.info(f"初始筛选范围: {score_min} - {score_max}")
        
        # 筛选符合分数范围的学校
        filtered_schools = df[
            (df['投档线'] >= score_min) & 
            (df['投档线'] <= score_max)
        ]
        
        logger.info(f"筛选后学校数量: {len(filtered_schools)}")
        
        # 如果找到的学校少于5所，扩大范围到±10分
        if len(filtered_schools) < 5:
            score_min = score - 10
            score_max = score + 10
            logger.info(f"扩大筛选范围: {score_min} - {score_max}")
            filtered_schools = df[
                (df['投档线'] >= score_min) & 
                (df['投档线'] <= score_max)
            ]
            logger.info(f"扩大范围后学校数量: {len(filtered_schools)}")
        
        # 对于同一院校只保留分数最低的专业组
        filtered_schools = filtered_schools.sort_values('投档线').groupby('院校名称').first().reset_index()
        
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
        logger.error(f"输入分数: {score}")
        logger.error(f"分数范围: {score_min} - {score_max}")
        logger.error(f"筛选前学校数量: {len(df)}")
        logger.error(f"筛选后学校数量: {len(filtered_schools)}")
        logger.error(f"Error: {str(e)}")
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
    app.run(host='0.0.0.0', port=8066)