import os
import urllib.parse
import urllib.request

from config import SYMBOLS, TIMEFRAME
from market_data import get_data
from analyzer import analyze, format_result


def send_telegram(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram secrets are missing")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Telegram يسمح برسالة حتى 4096 حرفًا
    chunks = [message[i:i + 4000] for i in range(0, len(message), 4000)]

    for chunk in chunks:
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": chunk
        }).encode()

        request = urllib.request.Request(url, data=data, method="POST")

        with urllib.request.urlopen(request, timeout=30) as response:
            print("Telegram:", response.read().decode())


def main():
    results = []

    header = (
        "==============================\n"
        "محلل ذكي | Smart Analyzer\n"
        "==============================\n"
        f"الفريم: {TIMEFRAME}\n"
    )

    results.append(header)

    for symbol in SYMBOLS:
        try:
            df = get_data(symbol, interval=TIMEFRAME)
            result = analyze(df)

            formatted = format_result(symbol, result)
            results.append(formatted)

        except Exception as e:
            results.append(f"{symbol}: خطأ - {e}")

    final_message = "\n\n".join(results)

    print(final_message)
    send_telegram(final_message)


if __name__ == "__main__":
    main()
