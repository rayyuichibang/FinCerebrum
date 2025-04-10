from cerebrum.config.Config import Config
from openai import OpenAI
import threading
from cerebrum.toolkit.MessageBroker import MessageBroker
from cerebrum.toolkit.Topics import Topics
from typing import Dict, Any, Callable
import time


class AIClient(threading.Thread):
    """
    Base class for AI client threads that handle specific AI tasks.
    Implements common functionality for interacting with AI services.
    """
    
    def __init__(self, 
                 broker: MessageBroker, 
                 role: str, 
                 max_retries: int = 3,
                 model: str = ''):
        """
        Initialize the AI client thread.
        
        Args:
            broker: The message broker for pub/sub communication
            role: The specialized role of this AI client
            max_retries: Maximum number of retry attempts for API calls
            model: Optional specific model to override default
        """
        super().__init__(daemon=True)  # Set as daemon thread to exit with main program
        config = Config()
        self.config = config.config  # Load system configuration
        self.broker = broker
        self.role = role
        self.max_retries = max_retries
        self.model = model  # The LLM model this client will use
        self.active = True  # Thread running status flag
        self._register_handlers()  # Setup default message handlers
        self.client = self.initClient()  # Initialize AI service client
    
    def initClient(self):
        """Initialize and configure the AI service client."""
        aiConfig = self.config['utils']['AI']
        client = OpenAI(
            base_url=aiConfig['baseURL'],
            api_key=aiConfig['apiKey']
        )
        return client
    
    def _register_handlers(self):
        """Register default message handlers for this client."""
        # Default handler for system shutdown
        self.broker.subscribe(Topics.SYSTEM_SHUTDOWN, self._handle_shutdown)
    
    def call_ai(self, prompt):
        """
        Make a request to the AI service.
        
        Args:
            prompt: The input messages/prompt for the AI
            
        Returns:
            The content of the AI's response
        """
        aiConfig = self.config['utils']['AI']
        role = self.role
        model = aiConfig['model'][role]
        
        result = self.client.chat.completions.create(
            model=model,
            messages=prompt,
            temperature=0.7,  # Controls randomness of output
            max_tokens=3000  # Limit response length
        )

        return result.choices[0].message.content
    
    def _handle_shutdown(self, _):
        """Handle system shutdown command."""
        print(f'\033[92m{self.role} client is shutting down\033[0m')  # Green text
        self.active = False  # Set flag to terminate thread
    
    def handle_task(self, message: Dict[str, Any]):
        """
        Process a task message (to be implemented by child classes).
        
        Args:
            message: The task message dictionary
            
        Raises:
            NotImplementedError: If child class doesn't implement this
        """
        raise NotImplementedError("Child classes must implement handle_task")
    
    def run(self):
        """Main thread execution loop."""
        while self.active:
            time.sleep(0.1)  # Small delay to prevent CPU overuse