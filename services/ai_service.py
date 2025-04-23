import requests
import json
from typing import Dict, Any, Optional
from config import Config

class AIRecommendationService:
    def __init__(self):
        self.api_key = Config.LINK_AI_API_KEY
        self.api_url = Config.LINK_AI_API_URL
        
    def get_major_recommendations(self, score: float) -> Dict[str, Any]:
        """
        通过 LinkAI 获取专业推荐
        Args:
            score: 高考分数
        Returns:
            Dict 包含推荐结果
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",  # LinkAI 支持的模型
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的高考志愿填报顾问，请根据考生分数推荐合适的专业。"
                    },
                    {
                        "role": "user",
                        "content": f"我的高考分数是{score}分，请推荐5个适合的大学专业。对每个专业请详细说明：1.专业名称 2.推荐理由 3.就业方向 4.未来发展前景"
                    }
                ],
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 处理 LinkAI 的响应格式
            if 'choices' in result and len(result['choices']) > 0:
                recommendations = result['choices'][0]['message']['content']
                return {
                    "success": True,
                    "data": recommendations
                }
            else:
                return {
                    "success": False,
                    "error": "无法获取推荐结果"
                }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"AI服务调用失败: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"处理失败: {str(e)}"
            }

    def _format_recommendations(self, raw_response: str) -> Dict[str, Any]:
        """
        格式化 AI 返回的推荐结果
        """
        try:
            # 这里可以添加更多的格式化逻辑
            return {
                "recommendations": raw_response,
                "formatted": True
            }
        except Exception as e:
            return {
                "error": f"格式化失败: {str(e)}",
                "raw_content": raw_response
            }