import pandas as pd
import requests

class TradingEngine:
    def __init__(self):
        self.api_base = "https://api.binance.com/api/v3/klines"

    def fetch_data(self, symbol, interval, limit=100):
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        try:
            r = requests.get(self.api_base, params=params, timeout=5)
            df = pd.DataFrame(r.json(), columns=['time', 'open', 'high', 'low', 'close', 'volume', 'ct', 'qa', 'nt', 'tb', 'tq', 'i'])
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].apply(pd.to_numeric)
            return df
        except: return pd.DataFrame()

    def calculate_indicators(self, df):
        if df.empty: return df
        df['ema'] = df['close'].ewm(span=30, adjust=False).mean()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['rsi'] = 100 - (100 / (1 + (gain / loss)))
        
        df['atr'] = (df['high'] - df['low']).rolling(window=14).mean()
        df['volatility_ok'] = df['atr'] > df['atr'].rolling(50).mean() * 0.8 
        return df

    def check_confirmation(self, df, signal):
        if len(df) < 3: return False
        last = df.iloc[-1]
        prev = df.iloc[-2]
        if signal == "ACHAT":
            return last['close'] > last['ema'] and prev['close'] > prev['ema']
        elif signal == "VENTE":
            return last['close'] < last['ema'] and prev['close'] < prev['ema']
        return False

    def get_trade_plan(self, df, signal):
        price = df.iloc[-1]['close']
        atr = df.iloc[-1]['atr']
        dist = atr * 2.5
        sl = (price - dist) if signal == "ACHAT" else (price + dist)
        tp = (price + dist * 2) if signal == "ACHAT" else (price - dist * 2)
        target_be = price + (tp - price) * 0.5 if signal == "ACHAT" else price - (price - tp) * 0.5
        return {
            "type": signal, "entry": price, "sl": sl, "tp": tp, 
            "be_activated": False, "target_be": target_be
        }
