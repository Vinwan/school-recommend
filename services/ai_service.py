import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
import logging

class AIRecommendationService:
    def __init__(self):
        self.api_key = Config.LINK_AI_API_KEY
        self.api_url = Config.LINK_AI_API_URL
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 最多重试3次
            backoff_factor=1,  # 重试间隔时间
            status_forcelist=[429, 500, 502, 503, 504]  # 需要重试的HTTP状态码
        )
        
        # 创建会话并应用重试策略
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        
    def get_major_recommendations(self, score: float):
        """获取专业推荐"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        body = {
            "app_code": "UUwryw2c",  # 请替换为您的实际 app_code
            "messages": [
                {
                    "role": "user",
                    "content": f"我的高考分数是{score}分，请推荐5个适合的大学专业。对每个专业请详细说明：1.专业名称 2.就业方向"
                }
            ]
        }
        
        try:
            print(f"正在发送请求到 LinkAI，分数：{score}")
            print(f"请求头：{headers}")
            print(f"请求体：{body}")
            
            # 使用会话发送请求
            response = self.session.post(self.api_url, json=body, headers=headers, timeout=30)
            print(f"API 响应状态码：{response.status_code}")
            print(f"API 响应内容：{response.text}")
            
            if response.status_code == 200:
                reply_text = response.json().get("choices")[0]['message']['content']
                return {
                    "success": True,
                    "data": reply_text
                }
            else:
                error = response.json().get("error", {})
                error_message = f"请求异常, 错误码={response.status_code}, 错误类型={error.get('type')}, 错误信息={error.get('message')}"
                print(f"错误信息：{error_message}")
                return {
                    "success": False,
                    "error": error_message
                }
                
        except Exception as e:
            error_message = f"服务调用失败: {str(e)}"
            print(f"异常信息：{error_message}")
            return {
                "success": False,
                "error": error_message
            }