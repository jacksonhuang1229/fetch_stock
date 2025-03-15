import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
import boto3

def get_stock_data():
    symbols = ['^DJI', '^SOX', 'NVDA', 'SMCI']  # 修改你想要的股票代碼
    data = []

    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            # 修改這裡：獲取2天的數據以確保能計算漲跌幅
            info = stock.history(period="2d")
            
            if len(info) >= 2:
                current_price = info['Close'].iloc[-1]
                previous_close = info['Close'].iloc[-2]
            else:
                print(f"警告: {symbol} 無法獲取足夠的歷史數據")
                continue

            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
            # ... 其餘代碼保持不變 ...
            data.append({
                'timestamp': datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': symbol,
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2)
            })

            # 終端機印出股票資訊
            print(f"股票: {symbol}")
            print(f"時間: {datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"價格: {current_price}")
            print(f"漲跌: {round(change,2)} ({round(change_percent,2)}%)")
            print("-" * 50)

        except Exception as e:
            print(f"取得 {symbol} 資料失敗: {str(e)}")

    return pd.DataFrame(data)

def save_to_s3(df):
    s3 = boto3.client('s3')
    bucket_name = 'your-bucket-name'  # 你的S3桶名
    filename = 'stock_data.csv'

    try:
        # 如果存在資料就合併，不存在則建立新的檔案
        try:
            existing_obj = s3.get_object(Bucket=bucket_name, Key=filename)
            existing_df = pd.read_csv(existing_obj['Body'])
            df = pd.concat([existing_df, df])
        except Exception as e:
            pass  # 檔案不存在就直接建立新的

        # 存到 S3
        csv_buffer = df.to_csv(index=False)
        s3.put_object(Bucket=bucket_name, Key=filename, Body=csv_buffer)
        print("資料已儲存到 S3")
    except Exception as e:
        print(f"儲存到 S3 時發生錯誤: {str(e)}")

if __name__ == "__main__":
    df = get_stock_data()
    print(df.head())
    # save_to_s3(df) # 本機測試可先不存S3
