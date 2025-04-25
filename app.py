from flask import Flask, request, jsonify, render_template, make_response
import pandas as pd
import os
import logging
import sys
from datetime import datetime
from database import init_db, import_csv_to_db, get_schools_by_score, import_school_info  # Added import_school_info

app = Flask(__name__, static_folder='static')

# 配置日志输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize database first
init_db()

# 检查并创建示例数据
current_dir = os.path.dirname(os.path.abspath(__file__))
physics_csv_path = os.path.join(current_dir, 'schools.csv')
history_csv_path = os.path.join(current_dir, 'school-history.csv')
school_info_path = os.path.join(current_dir, 'school-info.csv')

if not os.path.exists(physics_csv_path):
    sample_data = {
        '院校名称': ['示例大学A', '示例大学B', '示例大学C', '示例大学D', '示例大学E'],
        '省份': ['北京', '上海', '广东', '江苏', '浙江'],
        '专业组名称': ['理工类', '理工类', '理工类', '理工类', '理工类'],
        '投档线': [500, 502, 503, 505, 508],
        '最低投档排名': [1000, 1200, 1300, 1400, 1500]
    }
    df = pd.DataFrame(sample_data)
    df.to_csv(physics_csv_path, index=False, encoding='utf-8')

# Import physics data
import_csv_to_db(physics_csv_path, 'schools')
logger.info("物理组数据导入完成")

# Import history data if exists
if os.path.exists(history_csv_path):
    import_csv_to_db(history_csv_path, 'schools_history')
    logger.info("历史组数据导入完成")
else:
    logger.warning("历史组数据文件不存在")

# 导入学校信息数据
if os.path.exists(school_info_path):
    import_school_info(school_info_path)
    logger.info("学校信息数据导入完成")
else:
    logger.warning("学校信息数据文件不存在")

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
        group_type = data.get('group', 'physics')  # 默认为物理组
        
        # 记录请求信息
        logger.info("="*50)
        logger.info("请求开始处理")
        logger.info(f"请求数据: {data}")
        
        # 从数据库获取推荐学校
        result = get_schools_by_score(score, group_type)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

if __name__ == '__main__':
    # 修改host为'0.0.0.0'以允许外部访问
    app.run(host='0.0.0.0', port=8066)