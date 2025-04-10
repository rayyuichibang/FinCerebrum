from enum import Enum


class Topics(str, Enum):
    """
    Enumeration of message topics used in the system.
    Each topic represents a specific communication channel or event type.
    Inherits from str to enable string comparison and serialization.
    """
    
    # User interaction topics
    USER_INPUT = 'task/handle_user_input'  # Topic for handling raw user input
    PRESENT_REPORT = "/task/present_report"  # Topic for presenting reports to users
    
    # User feedback topics
    USER_FEEDBACK = "task/user_feedback_out"  # Sends content for user feedback
    
    # Analysis topics
    MARKET_ANALYSIS = "task/market_analysis"  # Market data analysis requests
    MARKET_ANALYSIS_REVISE = "task/market_analysis_revise"
    NEWS_ANALYSIS = "task/news_analysis"  # News content analysis requests
    
    # Feedback handling topics
    MARKET_ANALYSIS_FEEDBACK = 'task/market_analysis_feedback'  # Market analysis feedback reprocessing
    NEWS_ANALYSIS_FEEDBACK = 'task/news_analysis_feedback'  # News analysis feedback reprocessing
    
    # Review and oversight topics
    CHIEF_REVIEW = "task/chief_review"  # Handles review by chief analyst
    
    # Specialized analysis topics
    BACKTEST_ANALYSIS = "task/backtest_analysis"  # Backtesting results analysis
    CHIEF_ANALYSIS = "task/chief_analyst"  # Chief analyst's comprehensive analysis
    SENTIMENT_ANALYSIS = "task/sentiment_analysis"  # Market sentiment analysis
    
    # System control topic
    SYSTEM_SHUTDOWN = "system/shutdown"  # System shutdown command