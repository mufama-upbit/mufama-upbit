import pyupbit
import time
from datetime import datetime

# API 키 설정
access_key = "your_access_key"
secret_key = "your_secret_key"
upbit = pyupbit.Upbit(access_key, secret_key)

# 이동평균선 계산 함수
def get_ma(ticker, days):
    try:
        df = pyupbit.get_ohlcv(ticker, interval="day", count=days, to=datetime.now().strftime('%Y-%m-%d') + ' 09:00:00')
        if len(df) < days:
            return None  # 데이터가 충분하지 않으면 None 반환
        ma = df['close'].rolling(window=days).mean().iloc[-1]
        return ma
    except Exception as e:
        print(f"Error in get_ma: {e}")
        return None

# 매수 함수
def buy_crypto(ticker, krw):
    try:
        upbit.buy_market_order(ticker, krw)
    except Exception as e:
        print(f"Error in buy_crypto: {e}")

# 매도 함수
def sell_crypto(ticker, amount):
    try:
        upbit.sell_market_order(ticker, amount)
    except Exception as e:
        print(f"Error in sell_crypto: {e}")

# 전체 평가 금액 조회 함수
def get_total_balance():
    try:
        balances = upbit.get_balances()
        total_balance = 0
        for balance in balances:
            if balance['currency'] == 'KRW':
                total_balance += float(balance['balance'])
            else:
                ticker = "KRW-" + balance['currency']
                price = pyupbit.get_current_price(ticker)
                total_balance += float(balance['balance']) * price
        return total_balance
    except Exception as e:
        print(f"Error in get_total_balance: {e}")
        return 0

# 매수된 코인 종류 수 조회 함수
def get_bought_tickers():
    try:
        balances = upbit.get_balances()
        bought_tickers = []
        for balance in balances:
            if balance['currency'] != 'KRW' and float(balance['balance']) > 0:
                bought_tickers.append("KRW-" + balance['currency'])
        return bought_tickers
    except Exception as e:
        print(f"Error in get_bought_tickers: {e}")
        return []

# 자동매매 실행
tickers = pyupbit.get_tickers(fiat="KRW")  # 모든 원화 거래 가능 코인 목록
while True:  # 무한 루프
    try:
        bought_tickers = get_bought_tickers()
        if len(bought_tickers) < 4:  # 매수된 코인 종류가 4개 미만일 때만 매수
            for ticker in tickers:
                price = pyupbit.get_current_price(ticker)
                ma30 = get_ma(ticker, 30)
                ma365 = get_ma(ticker, 365)
                
                if ma365 is not None and price > ma30 and price > ma365 and ma30 > ma365:
                    total_balance = get_total_balance()
                    buy_amount = total_balance * 0.2  # 전체 평가 금액의 20%
                    buy_crypto(ticker, buy_amount)
                elif price < ma30:
                    balance = upbit.get_balance(ticker)
                    if balance > 0.0001:  # 최소 매도 단위 확인
                        sell_crypto(ticker, balance)
        
        time.sleep(60)  # 1분마다 실행
    except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(60)  # 오류 발생 시 1분 대기 후 재시도