from cerebrum.config.Config import Config
import yfinance as yf
import pandas as pd
import talib
import numpy as np


class FinanceDataUtils:
    """A utility class for retrieving financial data and calculating technical indicators."""
    
    def __init__(self):
        """Initialize FinanceDataUtils with configuration and default tool."""
        config = Config()
        self.config = config.config
        self.tool = self.toolKit(1)  # Get the highest priority tool by default
    
    def toolKit(self, priority):
        """
        Get the finance tool with specified priority from config.
        
        Args:
            priority: The priority level of the tool to retrieve
            
        Returns:
            The finance tool configuration dictionary
        """
        return next(tool for tool in self.config['utils']['FinanceTools'] 
                   if tool['priority'] == priority)
    
    def retrieveData(self, ticker, filter):
        """
        Retrieve stock data based on ticker and filter parameters.
        
        Args:
            ticker: The stock ticker symbol
            filter: Dictionary containing retrieval parameters (period or date range)
            
        Returns:
            Pandas DataFrame containing the stock data
        """
        if self.tool['name'] == 'YahooFinance':
            stock_data = yf.Ticker(ticker)
            if filter['option'] == 1:  # Search by period
                '''
                Supported period options: 1d,5d,1mo,1y
                '''
                period = filter['period']
                stock_data = stock_data.history(period=period)
            else:  # Search by start and end date
                start_date = filter['start_date']
                end_date = filter['end_date']
                stock_data = stock_data.history(start=start_date, end=end_date)
            
            return stock_data

        elif self.tool['name'] == 'FinHub':
            pass  # To supplement other tools
    
    def getTechnicalIndicators(self, data):
        """
        Calculate various technical indicators for the given stock data.
        
        Args:
            data: Pandas DataFrame containing stock data
            
        Returns:
            Dictionary containing all calculated technical indicators
        """
        # Calculate Moving Averages
        MA20 = round(talib.SMA(data['Close'], timeperiod=20).iloc[-1], 2)
        MA50 = round(talib.SMA(data['Close'], timeperiod=50).iloc[-1], 2)

        # Calculate Exponential Moving Averages
        EMA20 = round(talib.EMA(data['Close'], timeperiod=20).iloc[-1], 2)
        EMA50 = round(talib.EMA(data['Close'], timeperiod=50).iloc[-1], 2)

        # Get recent volume data
        recent20Volume = data['Volume'].tail(20).tolist()
        recent50Volume = data['Volume'].tail(50).tolist()

        # Calculate MACD indicators
        data['MACD'], data['MACD_signal'], data['MACD_hist'] = talib.MACD(data['Close'])
        data['MACD_prev'] = data['MACD'].shift(1)
        data['MACD_signal_prev'] = data['MACD_signal'].shift(1)

        data['MACD_signal_flag'] = np.where(
            (data['MACD_prev'] < data['MACD_signal_prev']) & (data['MACD'] > data['MACD_signal']),
            '黃金交叉',
            np.where(
                (data['MACD_prev'] > data['MACD_signal_prev']) & (data['MACD'] < data['MACD_signal']),
                '死亡交叉',
                '無交叉'
            )
        )
        recent20MACD = data['MACD'].tail(20).tolist()
        latest_cross = data[data['MACD_signal_flag'].isin(['黃金交叉', '死亡交叉'])].iloc[-1]['MACD_signal_flag']
        
        # Calculate RSI
        data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
        conditions = [data['RSI'] > 70, data['RSI'] < 30]
        choices = ['超買', '超賣']
        data['RSI_signal'] = np.select(conditions, choices, default='中性')
        latest_RSI_signal = data['RSI_signal'].iloc[-1]
        latest_RSI = data['RSI'].iloc[-1]

        # Calculate Bollinger Bands
        data['UpperBB'], data['MiddleBB'], data['LowerBB'] = talib.BBANDS(data['Close'], timeperiod=20)
        data['BB_signal'] = np.where(
            data['Close'] > data['UpperBB'], 
            '突破上軌', 
            np.where(
                data['Close'] < data['LowerBB'], 
                '跌破下軌', 
                '中間'
            )
        )
        latest_BB_signal = data[data['BB_signal'].isin(['突破上軌', '跌破下軌','中間'])].iloc[-1]['BB_signal']

        # Calculate Stochastic Oscillator
        data['slowk'], data['slowd'] = talib.STOCH(data['High'], data['Low'], data['Close'])
        data['KD_signal'] = np.where(data['slowk'] > data['slowd'], 'K上穿D', 'K下穿D')
        latest_KD_signal = data[data['KD_signal'].isin(['K上穿D', 'K下穿D'])].iloc[-1]['KD_signal']

        # Calculate ADX
        data['ADX'] = talib.ADX(data['High'], data['Low'], data['Close'], timeperiod=14)
        data['ADX_signal'] = np.where(data['ADX'] > 25, '趨勢明確', '趨勢弱')
        latest_ADX_signal = data[data['ADX_signal'].isin(['趨勢明確', '趨勢弱'])].iloc[-1]['ADX_signal']
        latest_ADX = data['ADX'].iloc[-1]

        # Calculate Volume indicators
        data['Volume_MA20'] = data['Volume'].rolling(window=20).mean()
        data['Volume_signal'] = np.where(
            data['Volume'] > data['Volume_MA20'], 
            '放量', 
            '縮量'
        )
        latest_Volume_signal = data[data['Volume_signal'].isin(['放量', '縮量'])].iloc[-1]['Volume_signal']

        #price trend
        price_trend_20 = data['Close'].tail(20).tolist()
        price_trend_50 = data['Close'].tail(50).tolist()

        # Compile all indicators into a dictionary
        indicators = {
            'volume': {
                'Volume20': recent20Volume,
                'Volume50': recent50Volume,
            },
            'price':{
                'Price20_Trend':price_trend_20,
                'Price50_Trend':price_trend_50,
            },
            'MA': {
                'MA20': MA20,
                'MA50': MA50,
                'direction': '若MA20上穿MA50且成交量增加，視為多頭訊號；反之為空頭'
            },
            'EMA': {
                'EMA20': EMA20,
                'EMA50': EMA50,
                'direction': 'EMA20上穿EMA50且成交量同步增加，視為短期買入訊號' 
            },
            'MACD': {
                'recent20MACD': recent20MACD,
                'latest_MACD_signal': latest_cross,
                'direction': '若黃金交叉且成交量上升，則為強多信號；反之為短空信號'
            },
            'RSI': {
                'latest_RSI': latest_RSI,
                'direction': 'RSI > 70 為超買（需小心回檔）；RSI < 30 為超賣（可能反彈），搭配成交量放大更可信'
            },
            'BB': {
                'latest_BB_signal': latest_BB_signal,
                'direction': '價格突破布林上軌且成交量增加，可能延續漲勢；跌破下軌加上放量，可能持續下跌'
            },
            'SO': {
               'latest_KD_signal': latest_KD_signal,
                'direction': 'K上穿D為買入訊號，尤其在20以下位置；K下穿D在80以上為賣出訊號，需觀察成交量是否同步' 
            },
            'ADX': {
                'latest_ADX': latest_ADX,
                'direction': 'ADX > 25 表示有趨勢，可結合MACD方向進行交易'
            },
            'VOMA': {
                'latest_Volume_signal': latest_Volume_signal,
                'direction': '量增有助於確認價格趨勢是否有效'
            }
        }
        
        return indicators