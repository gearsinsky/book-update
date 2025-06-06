import requests
import collections
import base64
from dotenv import load_dotenv
import os
import pandas as pd


load_dotenv(dotenv_path="/home/ubuntu/books/.env")

# 讀取變數
woocommerce_key = os.getenv("CONSUMER_KEY")
woocommerce_secret = os.getenv("CONSUMER_SECRET")
print("woocommerce_key", os.getenv("CONSUMER_KEY"))
print("woocommerce_secret", os.getenv("CONSUMER_SECRET"))

# 配置 API 的基本資訊
API_URL = "https://www.rising-shop-dg.com/wp-json/wc/v3/products"
API_KEY =  woocommerce_key
API_SECRET =  woocommerce_secret

# 創建基本授權頭
auth = base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}"
}

# 獲取所有商品（使用分頁）
products = []
page = 1
while True:
    response = requests.get(API_URL, headers=headers, params={"per_page": 100, "page": page})
    
    # 驗證請求是否成功
    if response.status_code != 200:
        print(f"無法獲取商品，錯誤代碼：{response.status_code}")
        exit()

    # 將當前頁面的商品加入總列表
    page_products = response.json()
    if not page_products:
        # 如果當前頁面沒有商品，說明已經到達最後一頁
        break

    products.extend(page_products)
    page += 1

print(f"總共獲取到 {len(products)} 個商品。")

# 商品名稱標準化函數（保留括號中的數字）
def normalize_name(name):
    # 去掉空格和一些不影響區分的特殊字符，但保留括號和其中的數字
    return name.replace(' ', '').lower()

# 構建商品名稱對應的商品列表
product_dict = collections.defaultdict(list)
for product in products:
    normalized_name = normalize_name(product['name'])
    product_dict[normalized_name].append(product)

# 找出重複的商品並刪除
deleted_products = []
for product_name, product_list in product_dict.items():
    if len(product_list) > 1:
        # 保留第一個商品，刪除其餘的重複項
        for product in product_list[1:]:
            product_id = product['id']
            delete_url = f"{API_URL}/{product_id}"
            delete_response = requests.delete(delete_url, headers=headers, params={"force": True})
            if delete_response.status_code == 200:
                deleted_products.append(product['name'])
            else:
                print(f"無法刪除商品 {product['name']}，錯誤代碼：{delete_response.status_code}")

# 輸出被刪除的商品名稱
if deleted_products:
    print("刪除以下重複商品：")
    for product_name in deleted_products:
        print(product_name)
else:
    print("沒有發現需要刪除的重複商品。")

