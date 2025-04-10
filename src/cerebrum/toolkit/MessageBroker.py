import threading
from typing import Dict, Any


class MessageBroker:
    """A simple thread-safe message broker for publish-subscribe pattern."""
    
    def __init__(self):
        """Initialize the MessageBroker with empty subscriptions and a lock."""
        self.subscriptions: Dict[str, list] = {}  # Topic to list of callbacks mapping
        self.lock = threading.Lock()  # Lock for thread safety
    
    def subscribe(self, topic: str, callback):
        """
        Subscribe a callback function to a topic.
        
        Args:
            topic: The topic to subscribe to
            callback: The function to be called when a message is published to the topic
        """
        with self.lock:
            if topic not in self.subscriptions:
                self.subscriptions[topic] = []
            self.subscriptions[topic].append(callback)
    
    def publish(self, topic: str, message: Dict[str, Any]):
        """
        Publish a message to a topic, notifying all subscribers asynchronously.
        
        Args:
            topic: The topic to publish to
            message: The message data to be sent to subscribers (as a dictionary)
        """
        with self.lock:
            subscribers = self.subscriptions.get(topic, [])
            for callback in subscribers:
                # Start a new daemon thread for each callback
                threading.Thread(
                    target=callback,
                    args=(message,),
                    daemon=True
                ).start()