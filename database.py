import sqlite3
import pandas as pd
from pathlib import Path

def init_db():
    # 创建数据库连接
    conn = sqlite3.connect('schools.db')
    cursor = conn.cursor()
    
    # 创建学校表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_name TEXT NOT NULL,
        province TEXT NOT NULL,
        major_group TEXT NOT NULL,
        score_line FLOAT NOT NULL,
        lowest_rank INTEGER NOT NULL
    )
    ''')
    
    conn.commit()
    return conn

def import_csv_to_db(csv_path):
    # 读取CSV文件
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    # 创建数据库连接
    conn = init_db()
    
    # 将DataFrame数据导入到数据库
    df.to_sql('schools', conn, if_exists='replace', index=False, 
              dtype={
                  '院校名称': 'TEXT',
                  '省份': 'TEXT',
                  '专业组名称': 'TEXT',
                  '投档线': 'FLOAT',
                  '最低投档排名': 'INTEGER'
              })
    
    conn.commit()
    conn.close()

def get_schools_by_score(score, range_min=10):
    conn = sqlite3.connect('schools.db')
    cursor = conn.cursor()
    
    # 定义三个类别的分数范围
    chong_min = score + 5  # "冲"的院校
    wen_min = score - 3    # "稳"的院校下限
    wen_max = score        # "稳"的院校上限
    bao_min = score - 10   # "保"的院校
    
    # 查询"冲"的院校
    cursor.execute('''
    SELECT DISTINCT 院校名称, 省份, 专业组名称, 投档线, 最低投档排名
    FROM schools
    WHERE 投档线 >= ?
    ORDER BY 投档线 ASC
    LIMIT 3
    ''', (chong_min,))
    
    chong_schools = cursor.fetchall()
    
    # 查询"稳"的院校
    cursor.execute('''
    SELECT DISTINCT 院校名称, 省份, 专业组名称, 投档线, 最低投档排名
    FROM schools
    WHERE 投档线 BETWEEN ? AND ?
    ORDER BY 投档线 DESC
    LIMIT 3
    ''', (wen_min, wen_max))
    
    wen_schools = cursor.fetchall()
    
    # 查询"保"的院校
    cursor.execute('''
    SELECT DISTINCT 院校名称, 省份, 专业组名称, 投档线, 最低投档排名
    FROM schools
    WHERE 投档线 <= ? AND 投档线 >= ?
    ORDER BY 投档线 DESC
    LIMIT 3
    ''', (bao_min, bao_min - 5))
    
    bao_schools = cursor.fetchall()
    
    # 将结果转换为字典列表
    result = {
        'chong': [],
        'wen': [],
        'bao': []
    }
    
    # 处理"冲"的院校
    for school in chong_schools:
        school_dict = {
            '院校名称': school[0],
            '省份': school[1],
            '专业组名称': school[2],
            '投档线': school[3],
            '最低投档排名': school[4],
            '类别': '冲'
        }
        result['chong'].append(school_dict)
    
    # 处理"稳"的院校
    for school in wen_schools:
        school_dict = {
            '院校名称': school[0],
            '省份': school[1],
            '专业组名称': school[2],
            '投档线': school[3],
            '最低投档排名': school[4],
            '类别': '稳'
        }
        result['wen'].append(school_dict)
    
    # 处理"保"的院校
    for school in bao_schools:
        school_dict = {
            '院校名称': school[0],
            '省份': school[1],
            '专业组名称': school[2],
            '投档线': school[3],
            '最低投档排名': school[4],
            '类别': '保'
        }
        result['bao'].append(school_dict)
    
    conn.close()
    return result