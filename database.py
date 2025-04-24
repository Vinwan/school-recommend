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
    
    # 查询在分数范围内的学校
    cursor.execute('''
    SELECT school_name, province, major_group, score_line, lowest_rank
    FROM schools
    WHERE score_line BETWEEN ? AND ?
    ORDER BY score_line DESC
    LIMIT 5
    ''', (score_min, score_max))
    
    schools = cursor.fetchall()
    
    # 如果结果少于5所学校，扩大范围继续查询
    if len(schools) < 5:
        score_min = score - (range_min * 2)
        score_max = score + (range_min * 2)
        cursor.execute('''
        SELECT school_name, province, major_group, score_line, lowest_rank
        FROM schools
        WHERE score_line BETWEEN ? AND ?
        ORDER BY score_line DESC
        LIMIT 5
        ''', (score_min, score_max))
        schools = cursor.fetchall()
    
    conn.close()
    
    return [
        {
            '院校名称': school[0],
            '省份': school[1],
            '专业组名称': school[2],
            '投档线': float(school[3]),
            '最低投档排名': int(school[4])
        }
        for school in schools
    ]