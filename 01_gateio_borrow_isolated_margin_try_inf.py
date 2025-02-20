import ccxt
import time
import requests
import hashlib
import hmac

# =====================================
# 입력
GATEIO_API = ""
GATEIO_SECRET = ""
BORROW_TICKER = "BTC"  # 빌리고자 하는 코인
USDT_AMOUNT = 10  # 사용할 USDT 금액
# =====================================


exchange = ccxt.gate(
    {
        "apiKey": GATEIO_API,
        "secret": GATEIO_SECRET,
    }
)


def transfer_and_borrow(ticker):
    # Spot에서 Margin으로 USDT 전송
    try:
        exchange.transfer(
            code="USDT",
            amount=USDT_AMOUNT,
            fromAccount="spot",
            toAccount="margin",
            params={"currency_pair": f"{ticker}_USDT"},
        )
        print(f"성공적으로 {USDT_AMOUNT} USDT를 Margin으로 전송했습니다.")
    except Exception as e:
        print(f"전송 중 오류 발생: {e}")
        return

    # max borrowable 구하기
    try:
        borrowable = get_maximum_borrowable(ticker)
        amount = float(borrowable["borrowable"])
        print(f"최대 대출 가능 금액: {amount}")
    except Exception as e:
        print(f"최대 대출 가능 금액 조회 중 오류 발생: {e}")
        return

    # 대출 시도
    while True:
        try:
            exchange.borrowIsolatedMargin(f"{ticker}/USDT", ticker, amount)
            print(f"성공적으로 {amount} {ticker}를 대출했습니다.")
            break
        except Exception as e:
            print(f"대출 중 오류 발생: {e}")
            time.sleep(1)


def get_maximum_borrowable(ticker):
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    url = "/margin/uni/borrowable"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    query_param = f"currency={ticker}&currency_pair={ticker}_USDT"
    sign_headers = gen_sign("GET", prefix + url, query_param)
    headers.update(sign_headers)

    response = requests.request(
        "GET", host + prefix + url + "?" + query_param, headers=headers
    )
    return response.json()


def gen_sign(method, url, query_string=None, payload_string=None):
    key = GATEIO_API
    secret = GATEIO_SECRET

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode("utf-8"))
    hashed_payload = m.hexdigest()
    s = "%s\n%s\n%s\n%s\n%s" % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(
        secret.encode("utf-8"), s.encode("utf-8"), hashlib.sha512
    ).hexdigest()
    return {"KEY": key, "Timestamp": str(t), "SIGN": sign}


# 사용 예시
transfer_and_borrow(BORROW_TICKER)
