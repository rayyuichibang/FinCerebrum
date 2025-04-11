from cerebrum.toolkit.AIClient import AIClient
from cerebrum.toolkit.MessageBroker import MessageBroker
from typing import Dict, Any, Callable
from cerebrum.toolkit.Topics import Topics
import random
from cerebrum.config.Prompt import Prompt
import json

class ChiefAnalyst(AIClient):
    def __init__(self, broker: MessageBroker):
        super().__init__(broker, "chief_analyst")
        self.pending_tasks: Dict[str, Dict] = {}
        self.reviewed_times = 0
        greeting = [
            {
                'role':'user',
                'content':'您的角色**：首席分析師（Chief Analysis Officer）**，審核 **市場分析師** 提交的 **股票技術指標分析報告**，確保其質量、準確性和戰略意義。現在你正式開始工作，請向你的用戶進行簡短問候。'
            }
        ]
        greeting = self.call_ai(greeting)
        print(f"\033[31m「問候」:{greeting}\033[0m")
        self.broker.subscribe(Topics.CHIEF_REVIEW, self.handle_task)
    
    def handle_task(self, message: Dict[str, Any]):
        chatHistory = message['chatHistory']
        analysis = message['content']
        if self.reviewed_times <1:
            #review the report
            
            prompt_config = Prompt()
            review_prompt = [
                {
                    'role':'user',
                    'content':prompt_config.chief_analyzer_review(analysis)
                }
            ]
            self.reviewed_times +=1
            review_result = self.call_ai(review_prompt)
            print(f"首席分析師審核結果:{review_result}")
            #print('Chief analyst review:',review_result)
            self.broker.publish(Topics.MARKET_ANALYSIS_REVISE, {
                        "task_id": message["task_id"],
                        "type": "final_report",
                        "review_feedback": review_result,
                        'market_analysis':analysis
                    })

        else:
            self.broker.publish(Topics.PRESENT_REPORT, {
                "task_id": message["task_id"],
                "type": "final_report",
                "report": analysis
            })
        print(f"\033[31m首席分析師已經完成了報告分析，現在將報告提交給用戶助理並完成審核任務。\033[0m")
    
