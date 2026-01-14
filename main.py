from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.core.window import Window
from kivy.lang import Builder

from datetime import datetime
from engine import TradingEngine
from config import CONFIG

# Charger le fichier .kv pour le design
Builder.load_file('amiraltitan.kv')

class AmiralTitanUI(BoxLayout):
    capital_text = StringProperty(f"{CONFIG['risk_management']['initial_capital']:.2f} USDT")
    
    # Propriétés pour chaque symbole
    btc_price = StringProperty("---")
    btc_signal = StringProperty("RANGE")
    btc_plan = StringProperty("")
    
    eth_price = StringProperty("---")
    eth_signal = StringProperty("RANGE")
    eth_plan = StringProperty("")
    
    bnb_price = StringProperty("---")
    bnb_signal = StringProperty("RANGE")
    bnb_plan = StringProperty("")
    
    paxg_price = StringProperty("---")
    paxg_signal = StringProperty("RANGE")
    paxg_plan = StringProperty("")

    log_history = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = (0.04, 0.04, 0.04, 1) # Couleur de fond gris très foncé

        self.engine = TradingEngine()
        self.capital = CONFIG["risk_management"]["initial_capital"]
        self.active_trades = {}
        
        # Mettre à jour l'interface toutes les 15 secondes
        Clock.schedule_interval(self.update_loop, 15)

    def update_loop(self, dt):
        self.capital_text = f"{self.capital:.2f} USDT" # Mise à jour du capital

        for symbol_idx, symbol in enumerate(CONFIG["symbols"]):
            df1 = self.engine.calculate_indicators(self.engine.fetch_data(symbol, "1m"))
            if df1.empty: continue
            last_price = df1.iloc[-1]['close']
            
            # 1. Gestion des Sorties & Break-Even
            if symbol in self.active_trades:
                t = self.active_trades[symbol]
                
                if not t['be_activated']:
                    if (t['type'] == "ACHAT" and last_price >= t['target_be']) or \
                       (t['type'] == "VENTE" and last_price <= t['target_be']):
                        t['sl'] = t['entry']
                        t['be_activated'] = True
                        self.log_trade(f"SAFE: BE ACTIVE sur {symbol}", "#00CCFF")

                win = (t['type'] == "ACHAT" and last_price >= t['tp']) or (t['type'] == "VENTE" and last_price <= t['tp'])
                loss = (t['type'] == "ACHAT" and last_price <= t['sl']) or (t['type'] == "VENTE" and last_price >= t['sl'])
                
                if win or loss:
                    risk_amt = self.capital * (CONFIG["risk_management"]["risk_per_trade_pct"] / 100)
                    pnl = (risk_amt * 2.0) if win else (0 if t['be_activated'] else -risk_amt)
                    self.capital += pnl
                    res_txt = "PROFIT" if win else ("SORTIE BE" if t['be_activated'] else "STOP LOSS")
                    res_col = "#00FF66" if win else "#FF3333"
                    self.log_trade(f"{res_txt} {symbol}: {pnl:+.2f} USDT", res_col)
                    self.active_trades.pop(symbol) # Utiliser .pop() pour supprimer la clé
                    
                    # Réinitialiser le plan sur l'UI
                    self.set_symbol_plan(symbol, "")


            # 2. Analyse Multi-Timeframe avec Confirmation et Volatilité
            df5 = self.engine.calculate_indicators(self.engine.fetch_data(symbol, "5m"))
            signal = "RANGE"
            
            if not df5.empty and df1.iloc[-1]['volatility_ok']:
                temp_sig = "RANGE"
                if last_price > df1.iloc[-1]['ema'] and last_price > df5.iloc[-1]['ema'] and df1.iloc[-1]['rsi'] < 70:
                    temp_sig = "ACHAT"
                elif last_price < df1.iloc[-1]['ema'] and last_price < df5.iloc[-1]['ema'] and df1.iloc[-1]['rsi'] > 30:
                    temp_sig = "VENTE"
                
                if temp_sig != "RANGE" and self.engine.check_confirmation(df1, temp_sig):
                    signal = temp_sig

            # Mise à jour UI des cartes
            fmt_price = f"{last_price:,.2f}" if last_price > 100 else f"{last_price:,.4f}"
            self.set_symbol_price(symbol, fmt_price)
            self.set_symbol_signal(symbol, signal)

            # 3. Ouverture de Position
            if signal in ["ACHAT", "VENTE"] and symbol not in self.active_trades:
                plan = self.engine.get_trade_plan(df1, signal)
                self.active_trades[symbol] = plan
                self.set_symbol_plan(symbol, f"TP:{plan['tp']:.1f}\nSL:{plan['sl']:.1f}")
                self.log_trade(f"IN {signal} {symbol} @ {last_price:,.2f}", "#FFFF00")

    def log_trade(self, msg, color="#00FF66"):
        t = datetime.now().strftime("%H:%M:%S")
        self.log_history = f"[{t}] {msg}\n" + self.log_history # Ajoute en haut
        
        # Pour éviter que le log soit trop long et ralentisse l'app
        lines = self.log_history.split('\n')
        if len(lines) > 50:
            self.log_history = '\n'.join(lines[:50])

    # Fonctions pour mettre à jour les propriétés des symboles via Kivy
    def set_symbol_price(self, symbol, price):
        if symbol == "BTCUSDT": self.btc_price = price
        elif symbol == "ETHUSDT": self.eth_price = price
        elif symbol == "BNBUSDT": self.bnb_price = price
        elif symbol == "PAXGUSDT": self.paxg_price = price

    def set_symbol_signal(self, symbol, signal):
        if symbol == "BTCUSDT": self.btc_signal = signal
        elif symbol == "ETHUSDT": self.eth_signal = signal
        elif symbol == "BNBUSDT": self.bnb_signal = signal
        elif symbol == "PAXGUSDT": self.paxg_signal = signal

    def set_symbol_plan(self, symbol, plan):
        if symbol == "BTCUSDT": self.btc_plan = plan
        elif symbol == "ETHUSDT": self.eth_plan = plan
        elif symbol == "BNBUSDT": self.bnb_plan = plan
        elif symbol == "PAXGUSDT": self.paxg_plan = plan


class AmiralTitanApp(App):
    def build(self):
        self.title = "Amiral Titan 2.0 PRO"
        return AmiralTitanUI()

if __name__ == "__main__":
    AmiralTitanApp().run()
