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
            print(f"\033[31m首席分析師審核結果:{review_result}\033[0m")
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
        #print('Chief analyst has completed report review, now passing back to user.')
    def handle_analysis_result(self, message: Dict[str, Any]):
        """处理单个分析结果"""
        task_id = message["task_id"]
        analysis_type = message["type"]
        print('message that cheif received,',message)

        # check quality
        
        #generate final report
        report = 'This is the final report: '+message['content']
        self.broker.publish(Topics.PRESENT_REPORT, {
                "task_id": task_id,
                "type": "final_report",
                "report": report
            })
        '''
        if task_id not in self.pending_tasks:
            self.pending_tasks[task_id] = {
                "market": None,
                "backtest": None,
                "sentiment": None,
                "retries": 0
            }
        
        # 存储结果
        self.pending_tasks[task_id][analysis_type] = message["content"]
        
        # 检查完整性
        if all(self.pending_tasks[task_id].values()):
            self._process_complete_task(task_id)
        '''
    
    def _process_complete_task(self, task_id: str):
        """处理完整任务"""
        task = self.pending_tasks[task_id]
        
        # 生成最终报告
        # 應該先處理質量檢查，再生成最終報告
        report = self._generate_report(task)
        print('Generated report,',report)
        
        # 质量检查
        if self._quality_check(report):
            print('Quality checked')
            self.broker.publish(Topics.CHIEF_REVIEW, {
                "task_id": task_id,
                "type": "final_report",
                "report": report
            })
            del self.pending_tasks[task_id]
        else:
            print('Quality not checked')
            self._handle_failed_task(task_id, task)
    
    def _generate_report(self, task: Dict) -> str:
        """生成最终报告"""
        return (
            "=== 综合分析报告 ===\n"
            f"市场分析：{task['market']}\n"
            f"回测分析：{task['backtest']}\n"
            f"情绪分析：{task['sentiment']}\n"
        )
    
    def _quality_check(self, report: str) -> bool:
        """AI质量检查"""
        return "不合格" not in self.call_ai(f"检查报告质量：{report}")
    
    def _handle_failed_task(self, task_id: str, task: Dict):
        """处理失败任务"""
        task["retries"] += 1
        if task["retries"] < self.max_retries:
            print(f"任务 {task_id} 需要重试")
            # 重新分发任务
            for analysis_type in ["market", "backtest", "sentiment"]:
                self.broker.publish(f"task/{analysis_type}_analysis", {
                    "task_id": task_id,
                    "data": task["original_query"],
                    "retries": task["retries"]
                })
        else:
            print(f"任务 {task_id} 已达到最大重试次数")
            del self.pending_tasks[task_id]
