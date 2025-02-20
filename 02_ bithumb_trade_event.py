import ccxt
import time

# =====================================
# 입력
TICKER = "BTC/KRW"
ACCOUNTS = [
    {"apiKey": "", "secret": ""},
    {"apiKey": "", "secret": ""},
    {"apiKey": "", "secret": ""},
    {"apiKey": "", "secret": ""},
]  # 다계정할거면 여러개 추가
# =====================================

for i, account in enumerate(ACCOUNTS):
    exchange = ccxt.bithumb(account)
    current_price = exchange.fetch_order_book(TICKER, limit=1)[0][0]
    amount = 5500 // current_price + 1
    exchange.create_order(TICKER, type="market", side="buy", amount=amount)
    print(f"[{i+1}번째 계정] 매수 완료: {TICKER} {amount}개")
    exchange.create_order(TICKER, type="market", side="sell", amount=amount)
    print(f"[{i+1}번째 계정] 매도 완료: {TICKER} {amount}개")
