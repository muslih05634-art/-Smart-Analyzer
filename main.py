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
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Telegram يسمح بحد أقصى يقارب 4096 حرفاً للرسالة
    chunks = [
        message[i:i + 4000]
        for i in range(0, len(message), 4000)
    ]

    for chunk in chunks:
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": chunk
        }).encode()

        request = urllib.request.Request(
            url,
            data=data,
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = response.read().decode()
                print("Telegram:", result)

        except Exception as e:
            print(f"Telegram error: {e}")
            return False

    return True


def main():
    print("================================")
    print("   محلل ذكي | Smart Analyzer")
    print("================================")
    print(f"الفريم: {TIMEFRAME}")
    print()

    results = []

    for symbol in SYMBOLS:
        try:
            print(f"تحليل {symbol}...")

            df = get_data(symbol, interval=TIMEFRAME)
            result = analyze(df)

            formatted = format_result(symbol, result)

            print(formatted)
            print()

            results.append(formatted)

        except Exception as e:
            error_message = f"{symbol}: خطأ - {e}"
            print(error_message)
            results.append(error_message)

    if not results:
        print("لا توجد نتائج لإرسالها إلى Telegram")
        return

    telegram_message = (
        "📊 محلل ذكي | Smart Analyzer\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        + "\n\n".join(results)
    )

    print("إرسال النتائج إلى Telegram...")
    send_telegram(telegram_message)


if __name__ == "__main__":
    main()
