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

def get_schools_by_score(score, range_min=5):
    conn = sqlite3.connect('schools.db')
    cursor = conn.cursor()
    
    # 设置分数范围
    score_min = score - range_min
    score_max = score + range_min
    
    # 查询在分数范围内的学校，添加 DISTINCT 关键字去重
    cursor.execute('''
    SELECT DISTINCT 院校名称, 省份, 专业组名称, 投档线, 最低投档排名
    FROM schools
    WHERE 投档线 BETWEEN ? AND ?
    ORDER BY 投档线 DESC
    LIMIT 5
    ''', (score_min, score_max))
    
    schools = cursor.fetchall()
    
    # 如果没有找到学校，尝试扩大范围
    if not schools:
        # 扩大范围
        score_min = score - (range_min * 2)
        score_max = score + (range_min * 2)
        
        cursor.execute('''
        SELECT DISTINCT 院校名称, 省份, 专业组名称, 投档线, 最低投档排名
        FROM schools
        WHERE 投档线 BETWEEN ? AND ?
        ORDER BY 投档线 DESC
        LIMIT 5
        ''', (score_min, score_max))
        
        schools = cursor.fetchall()
    
    # 将结果转换为字典列表
    result = []
    seen_schools = set()  # 用于跟踪已经添加的学校和专业组组合
    
    for school in schools:
        school_dict = {
            '院校名称': school[0],
            '省份': school[1],
            '专业组名称': school[2],
            '投档线': school[3],
            '最低投档排名': school[4]
        }
        
        # 创建唯一标识符，用于检测重复
        unique_id = f"{school[0]}_{school[2]}"
        
        # 只有当这个组合不在已见列表中时才添加
        if unique_id not in seen_schools:
            seen_schools.add(unique_id)
            result.append(school_dict)
    
    conn.close()
    return result