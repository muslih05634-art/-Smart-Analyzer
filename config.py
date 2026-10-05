SYMBOLS = [
    "SPX",
    "NDX",
    "META",
    "DELL",
    "MU",
    "AMD",
    "MRNA",
    "TSLA",
    "SPCX",
]

TIMEFRAME = "15m"
LOOKBACK = "120"
EMA_FAST = 20
EMA_SLOW = 50
EMA_TREND = 200

# هامش تقريبي حول الدعم/المقاومة لتكوين منطقة دخول
ZONE_PCT = 0.0025

# أقل درجة لإظهار إشارة
MIN_SIGNAL_SCORE = 65

# فلتر السيولة: الحجم الحالي يجب أن يتجاوز متوسط 20 شمعة بهذه النسبة
VOLUME_PERIOD = 20
MIN_VOLUME_RATIO = 1.20
STRONG_VOLUME_RATIO = 1.50
