from cerebrum.toolkit.AIClient import AIClient
from cerebrum.toolkit.MessageBroker import MessageBroker
from typing import Dict, Any, Callable
from cerebrum.toolkit.Topics import Topics
import uuid


class UserProxy(AIClient):
    """
    User proxy agent that acts as interface between human users and AI analysts.
    Handles task delegation and feedback collection.
    """
    
    def __init__(self, broker: MessageBroker, interactive_mode: bool = False):
        """
        Initialize the UserProxy agent.
        
        Args:
            broker: Message broker for communication
            interactive_mode: Whether to enable interactive user feedback
        """
        super().__init__(broker, "user_proxy")
        greeting = [
            {
                'role':'user',
                'content':'您的角色**：**高級用戶助理**，負責處理用戶的反饋需求和協調各分析師的工作。現在你正式開始工作，請向你的用戶進行簡短問候。'
            }
        ]
        greeting = self.call_ai(greeting)
        
        print(f"\033[92m「問候」:{greeting}\033[0m")  # greeting

        self.interactive_mode = interactive_mode  # Controls user interruption for feedback
        self.current_tasks: Dict[str, Dict] = {}  # Track active tasks
        self.market_analyzer_history = []  # Chat history with market analyst
        self.market_analyzer_retries = 3  # Max retries for market analysis
        self.news_analyzer_history = []  # Chat history with news analyst
        self.news_analyzer_retries = 3  # Max retries for news analysis

        # Register message handlers
        self.broker.subscribe(Topics.USER_INPUT, self.handle_task)
        self.broker.subscribe(Topics.PRESENT_REPORT, self.handle_final_report)

        # Additional handlers for interactive mode
        if interactive_mode:
            self.broker.subscribe(Topics.USER_FEEDBACK, self.handle_user_feedback)
    
    def handle_task(self, message: Dict[str, Any]):
        """
        Handle incoming tasks and delegate to appropriate analysts.
        
        Args:
            message: Task message containing ticker and filter data
        """
        task_id = f'task_{str(uuid.uuid4())}'  # Generate unique task ID
        ticker = message['data']['ticker']
        filter = message['data']['filter']
        
        # Delegate to Market Analyst
        topic_market_analysis = Topics.MARKET_ANALYSIS
        self.broker.publish(topic_market_analysis, {
            "task_id": task_id,
            "data": {
                'ticker': ticker,
                'filter': filter
            },
            'isInteractiveMode': self.interactive_mode
        })

        # Placeholder for News Analyst delegation
        '''
        topic_news_analysis = Topics.MARKET_ANALYSIS
        self.broker.publish(topic_news_analysis, {
            "task_id": task_id,
            "data": {
                'ticker': ticker,
            }
        })
        '''
    
    def handle_final_report(self, message: Dict[str, Any]):
        """
        Handle the final analysis report presentation.
        
        Args:
            message: Contains the final report data
        """
        task_id = message["task_id"]
        print(f"\033[92m用戶助理:最終的分析報告結果\033[0m") 
        print(f"\033[92m{message['report']}\033[0m") 
        #print(message['report'])
        
        # Shutdown system after final report
        self.active = False  # Mark task as complete
        self.broker.publish(Topics.SYSTEM_SHUTDOWN, {
            "task_id": task_id,
            "data": {
                'report': message['report']
            }
        })
    

    def handle_user_feedback(self, message: Dict[str, Any]):
        """
        Collect user feedback for analysis reports.
        
        Args:
            message: Contains report content needing feedback
        """
        #print(f"\033[92m用戶助理:用戶你好，請審閱{message['role']}的分析結果。如果你有什麼反饋，請告知。如果沒有，請輸入回車或'no'\033[0m") 
        #print('Following is the report from:', message['role'], 
        #      '.Please review and input your comments, if you do not have further comment, enter space or no')
        print(f"分析結果：{message['content']}") 
        #print('Analysis:', message['content'])
        
        feedback = input(f"\033[92m用戶助理:用戶你好，請審閱{message['role']}的分析結果。如果你有什麼反饋，請告知。如果沒有，請輸入回車或'no'\033[0m")
        currentAnalysis = message['content']
        
        #return the feedback to market analyzer
        self.broker.publish(Topics.MARKET_ANALYSIS_FEEDBACK, {
            "task_id": message['task_id'],
            "data": {
                'ticker': message['ticker'],
                'feedback': feedback,
                'chatHistory': message['chatHistory'],
                'retryAttempts': message['retries'],
                'currentAnalysis': currentAnalysis
            }
        })
        
        return 'This is the modified report'
 