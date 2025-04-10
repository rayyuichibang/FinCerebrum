import json
from types import SimpleNamespace
from typing import Any

class Config:
    _default_config = {
        'utils':{
            'FinanceTools':[
                {
                    'name':'YahooFinance',
                    'apiKey':'',
                    'priority':1              
                }
            ],
            'AI':[
                {
                    'role':'General',
                    'name':'LLM',
                    'apiKey':'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',
                    'baseURL':'https://openrouter.ai/api/v1',
                    'model':'qwen/qwen2.5-vl-32b-instruct:free'
                }
            ]
        },
        'a':'b'
    }

    def __init__(self):
        self.config = self._default_config
    





