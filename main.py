import os
import urllib.parse
import urllib.request

from config import SYMBOLS, TIMEFRAME
from market_data import get_data
from analyzer import analyze, format_result


TELEGRAM_API = "https://api.telegram.org/bot"


def telegram_request(method, params=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        print("TELEGRAM_BOT_TOKEN is missing")
        return None

    url = f"{TELEGRAM_API}{token}/{method}"

    data = None

    if params is not None:
        data = urllib.parse.urlencode(params).encode()

    request = urllib.request.Request(
        url,
        data=data,
        method="POST" if data else "GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode()
    except Exception as e:
        print(f"Telegram error: {e}")
        return None


def send_telegram(message, chat_id=None):
    configured_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    chat_id = chat_id or configured_chat_id

    if not chat_id:
        print("TELEGRAM_CHAT_ID is missing")
        return False

    # Telegram يسمح برسالة تصل إلى 4096 حرفًا.
    chunks = [
        message[i:i + 4000]
        for i in range(0, len(message), 4000)
    ]

    for chunk in chunks:
        result = telegram_request(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": chunk,
            },
        )

        if result is None:
            return False

    return True


def run_analysis():
    results = []

    header = (
        "📊 Smart Analyzer\n"
        f"⏱ الإطار الزمني: {TIMEFRAME}\n"
        "━━━━━━━━━━━━━━━━━━\n"
    )

    results.append(header)

    for symbol in SYMBOLS:
        try:
            df = get_data(symbol, interval=TIMEFRAME)
            result = analyze(df)

            results.append(
                format_result(symbol, result)
            )

        except Exception as e:
            results.append(
                f"❌ {symbol}: خطأ - {e}"
            )

    return "\n\n".join(results)


def get_updates():
    result = telegram_request(
        "getUpdates",
        {
            "timeout": 1,
            "allowed_updates": "message",
        },
    )

    if not result:
        return []

    try:
        import json

        data = json.loads(result)

        if not data.get("ok"):
            return []

        return data.get("result", [])

    except Exception as e:
        print(f"Update parsing error: {e}")
        return []


def confirm_updates(updates):
    if not updates:
        return

    last_update_id = max(
        update["update_id"]
        for update in updates
    )

    telegram_request(
        "getUpdates",
        {
            "offset": last_update_id + 1,
            "timeout": 1,
        },
    )


def handle_command(command, chat_id):
    command = command.split()[0].lower()

    if command == "/start":
        send_telegram(
            "🤖 مرحبًا بك في Smart Analyzer\n\n"
            "الأوامر المتاحة:\n"
            "/analyze - تشغيل التحليل\n"
            "/options - عرض الخيارات\n"
            "/alerts - حالة التنبيهات\n"
            "/help - المساعدة",
            chat_id,
        )

    elif command == "/help":
        send_telegram(
            "📚 Smart Analyzer\n\n"
            "/analyze\n"
            "تشغيل التحليل وإرسال النتائج.\n\n"
            "/options\n"
            "عرض إعدادات المحلل.\n\n"
            "/alerts\n"
            "عرض حالة التنبيهات.",
            chat_id,
        )

    elif command == "/options":
        symbols = ", ".join(SYMBOLS)

        send_telegram(
            "⚙️ إعدادات Smart Analyzer\n\n"
            f"⏱ الإطار الزمني: {TIMEFRAME}\n"
            f"📌 الأصول: {symbols}\n\n"
            "استخدم /analyze لتشغيل التحليل.",
            chat_id,
        )

    elif command == "/alerts":
        send_telegram(
            "🔔 التنبيهات\n\n"
            "الحالة: مفعلة\n"
            "📡 مصدر الإرسال: Telegram\n"
            "📊 المحلل: Smart Analyzer",
            chat_id,
        )

    elif command == "/analyze":
        send_telegram(
            "⏳ جاري تشغيل Smart Analyzer...",
            chat_id,
        )

        result = run_analysis()

        send_telegram(
            result,
            chat_id,
        )

    else:
        send_telegram(
            "❓ أمر غير معروف.\n\n"
            "استخدم /help لرؤية الأوامر المتاحة.",
            chat_id,
        )


def process_telegram_commands():
    configured_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    updates = get_updates()

    if not updates:
        return False

    for update in updates:
        message = update.get("message", {})
        text = message.get("text", "")
        chat = message.get("chat", {})
        chat_id = str(chat.get("id", ""))

        if not text.startswith("/"):
            continue

        # السماح فقط للمحادثة الموجودة في Secret
        if configured_chat_id and chat_id != str(configured_chat_id):
            print(f"Ignored message from chat {chat_id}")
            continue

        print(f"Telegram command: {text}")

        handle_command(text, chat_id)

    # تأكيد استلام التحديثات حتى لا تتكرر في التشغيل القادم.
    confirm_updates(updates)

    return True


def main():
    print("================================")
    print("       Smart Analyzer")
    print("================================")
    print(f"Timeframe: {TIMEFRAME}")
    print()

    # أولًا: معالجة أوامر Telegram.
    process_telegram_commands()


if __name__ == "__main__":
    main()
