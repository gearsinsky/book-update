import pandas as pd
from woocommerce import API
import glob

# WooCommerce API 設定
wcapi = API(
    url="http://54.199.115.191/",  # 替換為你的 WooCommerce 網址
    consumer_key="ck_7987669dbd82ab57e3e9a5f7b544a7dcbb603f3a", # 替換為你的 Consumer Key
    consumer_secret="cs_0b7d56a082508cc8543aab6765c5794698d7e5c3",   # 替換為你的 Consumer Secret
    version="wc/v3"
)

# 讀取 CSV 檔案
csv_file_path_pattern = "/home/ubuntu/books/refresh/3/*.csv"  # 替換為你的 CSV 檔案路徑
csv_files = glob.glob(csv_file_path_pattern)

# 檢查是否找到 CSV 檔案
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in path: {csv_file_path_pattern}")

# 讀取找到的第一個 CSV 檔案
df = pd.read_csv(csv_files[0])

# 檢查 CSV 中是否包含 'Title' 欄位
if 'Title' not in df.columns:
    raise KeyError("The CSV file does not contain a 'title' column.")

# 獲取所有的書名從 CSV 中
titles = df['Title'].tolist()

# 遍歷書名檢查 WooCommerce 是否存在
for title in titles:
    # 使用 WooCommerce API 根據標題查詢產品
    response = wcapi.get("products", params={"search": title})
    
    if response.status_code == 200:
        products = response.json()
        
        # 如果找到相應的產品
        if products:
            # 假設找到的第一個產品即為目標產品
            product_id = products[0]['id']
            
            # 更新庫存狀態為售空並新增簡短說明
            data = {
                "stock_quantity": 0,
                "stock_status": "outofstock",
                "short_description": "尚無庫存，歡迎聯繫調貨"  # 新增的簡短說明
            }
            update_response = wcapi.put(f"products/{product_id}", data)

            if update_response.status_code == 200:
                print(f"書名 '{title}' 已標示為 '售空' 並更新了簡短說明。")
            else:
                print(f"無法更新書名 '{title}' 的產品。錯誤: {update_response.status_code}")
    else:
        print(f"無法查詢書名 '{title}' 的產品。錯誤: {response.status_code}")

