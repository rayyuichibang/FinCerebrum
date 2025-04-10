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
