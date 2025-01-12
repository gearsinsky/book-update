from datetime import datetime
import requests
from dotenv import load_dotenv
import os

# 加載 .env 檔案中的環境變數
load_dotenv(dotenv_path="/home/ubuntu/books/.env")

# 讀取環境變數
woocommerce_key = os.getenv("CONSUMER_KEY")
woocommerce_secret = os.getenv("CONSUMER_SECRET")

if not woocommerce_key or not woocommerce_secret:
    raise ValueError("無法從環境變數中讀取 CONSUMER_KEY 或 CONSUMER_SECRET")

# WooCommerce API 設定
API_URL = "https://www.rising-shop-dg.com/wp-json/wc/v3/orders"

def get_orders_total_by_month(year, month):
    """
    根據指定年份與月份查詢 WooCommerce 訂單總金額（不篩選狀態）
    """
    # 設定日期範圍
    start_date = f"{year}-{month:02d}-01T00:00:00"
    if month == 12:
        end_date = f"{year+1}-01-01T00:00:00"
    else:
        end_date = f"{year}-{month+1:02d}-01T00:00:00"

    # API 請求參數
    params = {
        "consumer_key": woocommerce_key,
        "consumer_secret": woocommerce_secret,
        "after": start_date,
        "before": end_date,
        "per_page": 100  # 一次最多取回 100 筆
    }

    total_amount = 0.0
    page = 1

    while True:
        # 增加分頁參數
        params["page"] = page
        response = requests.get(API_URL, params=params)

        if response.status_code != 200:
            raise Exception(f"API 請求失敗: {response.status_code} - {response.text}")

        orders = response.json()

        if not orders:
            break

        # 計算總金額
        for order in orders:
            total_amount += float(order["total"])

        page += 1

    return total_amount

if __name__ == "__main__":
    # 提示使用者輸入年份和月份
    user_input = input("請輸入查詢的年份與月份 (格式: YYYY/MM): ")
    try:
        year, month = map(int, user_input.split('/'))
        if month < 1 or month > 12:
            raise ValueError("月份必須介於 1 到 12 之間。")

        total = get_orders_total_by_month(year, month)
        print(f"{year} 年 {month} 月的 WooCommerce 訂單總金額為: ${total:.2f}")
    except ValueError:
        print("輸入格式錯誤，請使用 YYYY/MM 格式，例如 2024/12。")
    except Exception as e:
        print(f"查詢失敗: {e}")

