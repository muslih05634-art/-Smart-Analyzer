from config import SYMBOLS, TIMEFRAME
from market_data import get_data
from analyzer import analyze, format_result

def main():
    print("================================")
    print("       محلل ذكي | Smart Analyzer")
    print("================================")
    print("الفريم:", TIMEFRAME)
    print()

    for symbol in SYMBOLS:
        try:
            df = get_data(symbol, interval=TIMEFRAME)
            result = analyze(df)
            print(format_result(symbol, result))
            print()
        except Exception as e:
            print(f"{symbol}: خطأ - {e}")

if __name__ == "__main__":
    main()
