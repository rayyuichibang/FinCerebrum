from cerebrum.config.Config import Config
from openai import OpenAI
import threading
from cerebrum.toolkit.MessageBroker import MessageBroker
from cerebrum.toolkit.Topics import Topics
from typing import Dict, Any, Callable
import time
from cerebrum.staff.UserProxy import UserProxy
from cerebrum.staff.MarketAnalyst import MarketAnalyst
from cerebrum.staff.ChiefAnalyst import ChiefAnalyst


class AIWorkGroup:
    """A group of AI agents working together to handle financial analysis tasks."""
    
    def __init__(self, interactive_mode=False):
        """
        Initialize the AI work group.
        
        Args:
            interactive_mode: Whether to run in interactive user mode
        """
        self.broker = MessageBroker()  # Message broker for inter-agent communication
        self.clients = []  # List to store all AI client threads
        
        # Initialize core components
        self._init_clients()
        self.broker.subscribe(Topics.SYSTEM_SHUTDOWN, self.handle_shutdown)
        self.running = True  # System running status flag
    
    def _init_clients(self):
        """Initialize all AI role clients."""
        roles = [
            UserProxy(self.broker, interactive_mode=True),  # User interface agent
            ChiefAnalyst(self.broker),  # Chief analysis agent
            MarketAnalyst(self.broker, interactive_mode=True),  # Market analysis agent
            # Can add BacktestAnalyst and SentimentAnalyst here
        ]
        
        # Start all client threads
        for client in roles:
            client.start()
            self.clients.append(client)
    
    def shutdown(self):
        """Shut down the entire system gracefully."""
        # Publish shutdown message to all subscribed clients
        self.broker.publish(Topics.SYSTEM_SHUTDOWN, {})

    def handle_shutdown(self, message: Dict[str, Any]):
        """
        Handle system shutdown by stopping all client threads.
        
        Args:
            message: Shutdown message (contents ignored)
        """
        for client in self.clients:
            client.active = False  # Signal thread to stop
            client.join(timeout=3)  # Wait for thread to finish
            
            if client.is_alive():
                print(f"Warning: {client.role} thread did not exit properly")
        
        self.running = False  # Update system status
        
        # Debug: Print all remaining threads
        for thread in threading.enumerate():
            print(f"Thread: {thread.name}, daemon: {thread.daemon}")


# Example usage
user_input = input('Please input ticker:')

# Create and run system
system = AIWorkGroup(interactive_mode=False)

# Publish sample analysis request
system.broker.publish(Topics.USER_INPUT, {
    "data": {
        'ticker': user_input,
        'filter': {
            'option': 1,
            'period': '3mo'
        }
    }
})

# Main loop
while system.running:
    time.sleep(0.1)
