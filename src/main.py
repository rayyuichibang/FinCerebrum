from cerebrum.toolkit.AIWorkGroup import AIWorkGroup
from cerebrum.toolkit.Topics import Topics
import time
if __name__ == '__main__':
    
    user_input = input('Please input ticker:')

    # Create and run system
    system = AIWorkGroup(interactive_mode=True)

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
