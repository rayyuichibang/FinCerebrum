from cerebrum.toolkit.AIClient import AIClient
from cerebrum.toolkit.MessageBroker import MessageBroker
from typing import Dict, Any, Callable
from cerebrum.toolkit.Topics import Topics
import random
from cerebrum.toolkit.FinanceDataUtils import FinanceDataUtils
from cerebrum.config.Prompt import Prompt


class MarketAnalyst(AIClient):
    """AI agent specialized in market technical analysis."""
    
    def __init__(self, broker: MessageBroker, interactive_mode):
        """
        Initialize the Market Analyst.
        
        Args:
            broker: Message broker for communication
            interactive_mode: Whether to enable interactive user feedback
        """
        super().__init__(broker, "market_analyst")
        greeting = [
            {
                'role':'user',
                'content':'您的角色**：**高級量化股票市場分析師**，負責提供全面、可行的市場洞察。現在你正式開始工作，請向你的用戶進行簡短問候。'
            }
        ]
        greeting = self.call_ai(greeting)
        print(f"\033[38;5;208m「問候」:{greeting}\033[0m")
        #print(f"\033[92minit: \033[0m")
        self.tickerData = None  # Cache for ticker data

        # Register message handlers
        self.broker.subscribe(Topics.MARKET_ANALYSIS, self.handle_task)
        self.broker.subscribe(Topics.MARKET_ANALYSIS_REVISE, self.handle_revise)

        # Additional handler for interactive feedback mode
        if interactive_mode:
            self.broker.subscribe(Topics.MARKET_ANALYSIS_FEEDBACK, 
                                self.handle_analysis_with_feedback)
    
    def handle_task(self, message: Dict[str, Any]):
        """Handle market analysis tasks."""
        print(f"\033[38;5;208m 高級市場分析師：開始分析工作\033[0m")
        
        
        task_id = message["task_id"]
        ticker = message["data"]['ticker']
        filter = message['data']['filter']
        isInteractiveMode = message['isInteractiveMode']

        # 1. Retrieve market data
        financeUtils = FinanceDataUtils()
        tickerData = financeUtils.retrieveData(
            ticker=ticker,
            filter=filter
        )

        # 2. Calculate technical indicators
        indicators = financeUtils.getTechnicalIndicators(tickerData)
        
        # 3. Prepare analysis prompt
        prompt_config = Prompt()
        system_role = prompt_config.market_analysis_role()
        user_prompt = prompt_config.market_analysis(indicators)
        
        prompt = [
            {
                'role': 'system',
                'content': system_role
            },
            {
                'role': 'user',
                'content': user_prompt
            }
        ]
        
        analysis = self.call_ai(prompt)
        chat_history = prompt
        chat_history.append(
            {
                'role': 'assistant',
                'content': analysis
            }
        )

        try:
            if isInteractiveMode:
                # Interactive mode: collect user feedback       
                self.broker.publish(Topics.USER_FEEDBACK, {
                    "task_id": task_id,
                    "ticker": ticker,
                    "role": "market_analyzer",
                    "content": analysis,
                    "chatHistory": chat_history,
                    "retries": self.max_retries
                })
            else:
                # Non-interactive mode: send directly to chief analyst
                print(f"\033[38;5;208m高級市場分析師：\033[0m")
                print(f"{analysis}")
                #print(analysis)
                print(f"\033[38;5;208m高級市場分析師：完成工作了，現在向首席分析師提交分析報告進行審核。\033[0m")
                #print('completed analyze, now passing to chief analyzer to review')
                self.broker.publish(Topics.CHIEF_REVIEW, {
                    "task_id": task_id,
                    "ticker": ticker,
                    "role": "market_analyzer",
                    "content": analysis,
                    "chatHistory": chat_history,
                    "retries": self.max_retries
                })
        except Exception as e:
            print(f"\033[38;5;208m高級市場分析師：系統故障，分析處理失敗\033[0m")
            #print(f"Market analyzer action failed:{str(e)}")

    def handle_analysis_with_feedback(self, message: Dict[str, Any]):
        """Handle analysis tasks incorporating user feedback."""
        print(f"\033[38;5;208m高級市場分析師：正在理解用戶的反饋。\033[0m")
        #print('Handling analysis task with user feedback')
        
        task_id = message["task_id"]
        ticker = message['data']['ticker']
        chatHistory = message['data']['chatHistory']
        feedback = message['data']['feedback']
        currentAnalysis = message['data']['currentAnalysis']

        if feedback == '' or feedback == 'no':
            # No feedback - submit to chief analyst
            print(f"\033[38;5;208m高級市場分析師：用戶沒有進一步的反饋，現在我將報告提交給首席分析師進行審核。\033[0m")
            self.broker.publish(Topics.CHIEF_REVIEW, {
                "task_id": task_id,
                "ticker": ticker,
                "role": "market_analyzer",
                "content": currentAnalysis,
                "chatHistory": chatHistory,
                "retries": self.max_retries
            })
        else:
            # Process feedback and re-analyze
            prompt_config = Prompt()
            prompt = {
                'role': 'user',
                'content': prompt_config.user_feedback(feedback)
            }
            
            chatHistory.append(prompt)
            #print(chatHistory)
            
            analysis = self.call_ai(chatHistory)
            print(f"高級市場分析師：用戶提交了反饋「{feedback}」，我將根據要求進行修正分析。")
            
            self.max_retries = self.max_retries - 1
            
            if self.max_retries > 0:
                # Still have retries remaining
                chatHistory.append(
                    {
                        'role': 'assistant',
                        'content': analysis
                    }
                )
                
                self.broker.publish(Topics.USER_FEEDBACK, {
                    "task_id": task_id,
                    "ticker": message['data']['ticker'],
                    "role": "market_analyzer",
                    "content": analysis,
                    "chatHistory": chatHistory,
                    "retries": self.max_retries
                })
            else:
                # Max retries reached - submit to chief analyst
                print(f"\033[38;5;208m高級市場分析師：已經多次修正，現在將分析報告提交給首席分析師進行審核。\033[0m")
                self.broker.publish(Topics.CHIEF_REVIEW, {
                    "task_id": task_id,
                    "ticker": ticker,
                    "role": "market_analyzer",
                    "content": analysis,
                    "chatHistory": chatHistory,
                    "retries": self.max_retries
                })
    def handle_revise(self,message: Dict[str, Any]):
        print(f"\033[38;5;208m高級市場分析師：正在根據首席分析師的審核結果進行修正。\033[0m")
        #print('handling revise')
        market_analysis = message['market_analysis']
        review_feedback = message['review_feedback']
        prompt_config = Prompt()
        revise_prompt = [{
                'role': 'user',
                'content': prompt_config.revise_market_analysis(market_analysis,review_feedback)
            }]
        revised_result = self.call_ai(revise_prompt)
        print(f"\033[38;5;208m高級市場分析師：修正完成，正在將報告提交給用戶助理並完成分析任務。\033[0m") 
        self.broker.publish(Topics.PRESENT_REPORT, {
                "task_id": message["task_id"],
                "type": "final_report",
                "report": revised_result
        })