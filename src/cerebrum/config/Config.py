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
                'apiKey':'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',
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
