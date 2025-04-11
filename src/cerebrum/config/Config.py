class Config:
    _default_config = {
        'utils':{
            'FinanceTools':[
                {
                    'name':'YahooFinance',
                    'apiKey':'',
                    'priority':1              
                },
                {
                    'name':'Finhub',
                    'apiKey':'',
                    'priority':2              
                }
            ],
            'AI':{
                'baseURL':'https://openrouter.ai/api/v1',
                'apiKey':'',
                'model':{
                    'user_proxy':'meta-llama/llama-4-maverick:free',
                    'market_analyst':'meta-llama/llama-4-maverick:free',
                    'news_analyst':'meta-llama/llama-4-maverick:free',
                    'chief_analyst':'meta-llama/llama-4-maverick:free'
                }
                
            }
        }
    }

    def __init__(self):
        self.config = self._default_config
