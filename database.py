import sqlite3
import pandas as pd
from pathlib import Path

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('schools.db')
    cursor = conn.cursor()
    
    # 创建物理组学校表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        院校名称 TEXT NOT NULL,
        省份 TEXT NOT NULL,
        专业组名称 TEXT NOT NULL,
        投档线 REAL NOT NULL,
        最低投档排名 INTEGER NOT NULL
    )
    ''')
    
    # 创建历史组学校表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schools_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        院校名称 TEXT NOT NULL,
        省份 TEXT NOT NULL,
        专业组名称 TEXT NOT NULL,
        投档线 REAL NOT NULL,
        最低投档排名 INTEGER NOT NULL
    )
    ''')
    
    # 创建学校信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS school_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        院校名称 TEXT NOT NULL,
        性质 TEXT,
        考研 TEXT,
        行业隶属 TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def import_csv_to_db(csv_path, table_name='schools'):
    """导入CSV数据到指定表"""
    try:
        conn = sqlite3.connect('schools.db')
        cursor = conn.cursor()
        
        # 清空表
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        
        # 读取CSV文件
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # 导入数据
        for _, row in df.iterrows():
            cursor.execute(f'''
                INSERT INTO {table_name} (院校名称, 省份, 专业组名称, 投档线, 最低投档排名)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['院校名称'],
                row['省份'],
                row['专业组名称'],
                row['投档线'],
                row['最低投档排名']
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"导入数据失败: {str(e)}")
        return False

def import_school_info(csv_path):
    """导入学校信息数据"""
    try:
        conn = sqlite3.connect('schools.db')
        cursor = conn.cursor()
        
        # 清空表
        cursor.execute("DELETE FROM school_info")
        conn.commit()
        
        # 读取CSV文件
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # 导入数据，处理985/211标签
        for _, row in df.iterrows():
            性质 = row['性质']
            if 性质 == '985/211':
                性质 = '985,211'
            elif 性质 != '211':
                性质 = None
                
            cursor.execute('''
                INSERT INTO school_info (院校名称, 性质, 考研, 行业隶属)
                VALUES (?, ?, ?, ?)
            ''', (
                row['院校名称'],
                性质,
                row['考研'],
                row['行业隶属']
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"导入学校信息失败: {str(e)}")
        return False

def get_schools_by_score(score, group_type='physics'):
    """根据分数和组别获取推荐学校"""
    conn = sqlite3.connect('schools.db')
    cursor = conn.cursor()
    
    # 根据组别选择表
    table_name = 'schools' if group_type == 'physics' else 'schools_history'
    
    # 定义三个类别的分数范围
    chong_min = score + 5  # "冲"的院校
    wen_min = score - 3    # "稳"的院校下限
    wen_max = score        # "稳"的院校上限
    bao_min = score - 10   # "保"的院校
    
    # 查询"冲"的院校
    cursor.execute(f'''
    SELECT DISTINCT s.院校名称, s.省份, s.专业组名称, s.投档线, s.最低投档排名,
           i.性质, i.考研, i.行业隶属
    FROM {table_name} s
    LEFT JOIN school_info i ON s.院校名称 = i.院校名称
    WHERE s.投档线 >= ?
    ORDER BY s.投档线 ASC
    LIMIT 3
    ''', (chong_min,))
    
    chong_schools = cursor.fetchall()
    
    # 查询"稳"的院校
    cursor.execute(f'''
    SELECT DISTINCT s.院校名称, s.省份, s.专业组名称, s.投档线, s.最低投档排名,
           i.性质, i.考研, i.行业隶属
    FROM {table_name} s
    LEFT JOIN school_info i ON s.院校名称 = i.院校名称
    WHERE s.投档线 BETWEEN ? AND ?
    ORDER BY s.投档线 DESC
    LIMIT 3
    ''', (wen_min, wen_max))
    
    wen_schools = cursor.fetchall()
    
    # 查询"保"的院校
    cursor.execute(f'''
    SELECT DISTINCT s.院校名称, s.省份, s.专业组名称, s.投档线, s.最低投档排名,
           i.性质, i.考研, i.行业隶属
    FROM {table_name} s
    LEFT JOIN school_info i ON s.院校名称 = i.院校名称
    WHERE s.投档线 <= ? AND s.投档线 >= ?
    ORDER BY s.投档线 DESC
    LIMIT 3
    ''', (bao_min, bao_min - 5))
    
    bao_schools = cursor.fetchall()
    
    # 将结果转换为字典
    result = {
        'chong': [],
        'wen': [],
        'bao': []
    }
    
    # 处理"冲"的院校
    for school in chong_schools:
        tags = []
        if school[5]:  # 性质
            tags.extend(school[5].split(','))
        if school[6]:  # 考研
            tags.append(school[6])
        if school[7]:  # 行业隶属
            tags.append(school[7])
            
        school_dict = {
            '院校名称': school[0],
            '省份': school[1],
            '专业组名称': school[2],
            '投档线': school[3],
            '最低投档排名': school[4],
            '标签': tags,
            '类别': '冲'
        }
        result['chong'].append(school_dict)
    
    # 处理"稳"的院校
    for school in wen_schools:
        tags = []
        if school[5]:  # 性质
            tags.extend(school[5].split(','))
        if school[6]:  # 考研
            tags.append(school[6])
        if school[7]:  # 行业隶属
            tags.append(school[7])
            
        school_dict = {
            '院校名称': school[0],
            '省份': school[1],
            '专业组名称': school[2],
            '投档线': school[3],
            '最低投档排名': school[4],
            '标签': tags,
            '类别': '稳'
        }
        result['wen'].append(school_dict)
    
    # 处理"保"的院校
    for school in bao_schools:
        tags = []
        if school[5]:  # 性质
            tags.extend(school[5].split(','))
        if school[6]:  # 考研
            tags.append(school[6])
        if school[7]:  # 行业隶属
            tags.append(school[7])
            
        school_dict = {
            '院校名称': school[0],
            '省份': school[1],
            '专业组名称': school[2],
            '投档线': school[3],
            '最低投档排名': school[4],
            '标签': tags,
            '类别': '保'
        }
        result['bao'].append(school_dict)
    
    conn.close()
    return result