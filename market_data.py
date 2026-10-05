import yfinance as yf

# Yahoo Finance لا يستخدم دائمًا رموز المؤشرات كما تظهر في المنصات.
# يمكن تعديل هذه الخريطة حسب مزود البيانات الذي ستستخدمه لاحقًا.
SYMBOL_MAP = {
    "SPX": "^GSPC",
    "NDX": "^NDX",
    "META": "META",
    "DELL": "DELL",
    "MU": "MU",
    "AMD": "AMD",
    "MRNA": "MRNA",
    "TSLA": "TSLA",
    "SPCX": "SPCX",
}

def get_data(symbol, interval="15m", period="60d"):
    ticker = SYMBOL_MAP.get(symbol, symbol)
    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        auto_adjust=False,
        progress=False,
    )

    if df is None or df.empty:
        return None

    # yfinance قد يرجع MultiIndex للأعمدة
    if hasattr(df.columns, "levels"):
        df.columns = df.columns.get_level_values(0)

    needed = ["Open", "High", "Low", "Close", "Volume"]
    df = df[[c for c in needed if c in df.columns]].dropna()
    return df
