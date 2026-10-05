import numpy as np
import pandas as pd

def _atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def _levels(df, window=20):
    recent = df.tail(window)
    support = float(recent["Low"].min())
    resistance = float(recent["High"].max())
    return support, resistance

def analyze(df, min_volume_ratio=1.20, volume_period=20):
    if df is None or len(df) < 60:
        return {"status": "بيانات غير كافية"}

    df = df.copy()
    for n in (20, 50, 200):
        df[f"EMA{n}"] = df["Close"].ewm(span=n, adjust=False).mean()

    df["ATR"] = _atr(df)
    close = float(df["Close"].iloc[-1])

    # فلتر السيولة: مقارنة آخر حجم بمتوسط آخر 20 شمعة
    volume_ratio = 0.0
    if "Volume" in df.columns:
        avg_volume = df["Volume"].rolling(volume_period).mean().iloc[-2]
        current_volume = df["Volume"].iloc[-1]
        if avg_volume and avg_volume > 0:
            volume_ratio = float(current_volume / avg_volume)

    liquidity_ok = volume_ratio >= min_volume_ratio
    ema20 = float(df["EMA20"].iloc[-1])
    ema50 = float(df["EMA50"].iloc[-1])
    ema200 = float(df["EMA200"].iloc[-1])

    support, resistance = _levels(df)
    atr = float(df["ATR"].iloc[-1]) if not np.isnan(df["ATR"].iloc[-1]) else close * 0.01

    # اتجاه مبسط: EMA + موقع السعر
    if close > ema20 > ema50 and close > ema200:
        trend = "صاعد"
    elif close < ema20 < ema50 and close < ema200:
        trend = "هابط"
    else:
        trend = "عرضي"

    # مناطق الدخول
    call_low = resistance * 1.0000
    call_high = resistance + atr * 0.20
    put_high = support * 1.0000
    put_low = support - atr * 0.20

    # أهداف مبنية على ATR، وليست توقعًا مضمونًا
    call_t1 = resistance + atr * 0.8
    call_t2 = resistance + atr * 1.6
    put_t1 = support - atr * 0.8
    put_t2 = support - atr * 1.6

    # درجة الإشارة
    score = 50
    if trend == "صاعد":
        score += 25
    elif trend == "هابط":
        score += 25
    else:
        score -= 5

    if close > ema20:
        score += 8
    if close > ema50:
        score += 7
    if close > ema200:
        score += 5

    if liquidity_ok:
        score += 10
    else:
        score -= 15

    score = max(0, min(100, int(score)))

    return {
        "price": close,
        "trend": trend,
        "support": support,
        "resistance": resistance,
        "call_zone": (call_low, call_high),
        "put_zone": (put_low, put_high),
        "call_targets": (call_t1, call_t2),
        "put_targets": (put_t1, put_t2),
        "call_confirmation": "إغلاق شمعة 15 دقيقة فوق المقاومة",
        "put_confirmation": "إغلاق شمعة 15 دقيقة تحت الدعم",
        "call_invalidation": support,
        "put_invalidation": resistance,
        "score": score,
        "volume_ratio": volume_ratio,
        "liquidity_ok": liquidity_ok,
        "liquidity_status": "مقبول" if liquidity_ok else "ضعيف",
    }

def format_result(symbol, result):
    if result.get("status"):
        return f"{symbol}: {result['status']}"

    def p(x):
        return f"{x:.2f}"

    call_a, call_b = result["call_zone"]
    put_a, put_b = result["put_zone"]
    ct1, ct2 = result["call_targets"]
    pt1, pt2 = result["put_targets"]

    return f"""
=== {symbol} | محلل ذكي ===
السعر: {p(result['price'])}
الاتجاه: {result['trend']}
الدعم الرئيسي: {p(result['support'])}
المقاومة الرئيسية: {p(result['resistance'])}

🟢 CALL
منطقة الدخول: {p(call_a)} - {p(call_b)}
التأكيد: {result['call_confirmation']}
الهدف 1: {p(ct1)}
الهدف 2: {p(ct2)}
إلغاء السيناريو: إغلاق تحت {p(result['call_invalidation'])}

🔴 PUT
منطقة الدخول: {p(put_a)} - {p(put_b)}
التأكيد: {result['put_confirmation']}
الهدف 1: {p(pt1)}
الهدف 2: {p(pt2)}
إلغاء السيناريو: إغلاق فوق {p(result['put_invalidation'])}

Volume Ratio: {result['volume_ratio']:.2f}x
فلتر السيولة: {"✅ مقبول" if result["liquidity_ok"] else "⚠️ ضعيف — لا تعتمد الاختراق"}

قوة الإشارة: {result['score']}/100
""".strip()
