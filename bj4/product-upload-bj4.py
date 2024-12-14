import csv
import os
from woocommerce import API
from urllib.parse import urlparse
from dotenv import load_dotenv
import os
import pandas as pd


load_dotenv(dotenv_path="/home/ubuntu/books/.env")

# 讀取變數
woocommerce_key = os.getenv("CONSUMER_KEY")
woocommerce_secret = os.getenv("CONSUMER_SECRET")
print("woocommerce_key", os.getenv("CONSUMER_KEY"))
print("woocommerce_secret", os.getenv("CONSUMER_SECRET"))


# 設定 WooCommerce API 憲證
wcapi = API(
    url="https://www.rising-shop-dg.com/",
    consumer_key=woocommerce_key,  # 替換為你的 API Key
    consumer_secret=woocommerce_secret,  # 替換為你的 API iSecret
    version="wc/v3"
)

# 讀取 CSV 文件
def read_csv_file(csv_file_path):
    products = []
    with open(csv_file_path, 'r', encoding='utf-8-sig') as f:  # 使用 'utf-8-sig' 去除 BOM
        reader = csv.DictReader(f)
        # 去除 BOM 對欄位名稱的影響，並進一步去除隱藏字符
        reader.fieldnames = [field.strip().replace('﻿', '') for field in reader.fieldnames]
        # 檢查 CSV 文件的欄位名稱
        print(f"讀取到的 CSV 欄位名稱: {reader.fieldnames}")
        for row in reader:
            products.append(row)
    return products

# 將多個產品上傳到 WooCommerce
def upload_products_from_multiple_csvs(csv_folder_path):
    existing_titles = set()
    for filename in os.listdir(csv_folder_path):
        if filename.endswith(".csv"):
            csv_file_path = os.path.join(csv_folder_path, filename)
            print(f"正在讀取文件: {filename}")
            products = read_csv_file(csv_file_path)
            if len(products) == 0:
                print(f"CSV 文件 {filename} 沒有讀取到任何產品，請檢查文件格式或路徑是否正確。")
                continue

            # 遍檢所有產品並上傳
            for product in products:
                upload_product_to_woocommerce(product, existing_titles)

# 判斷商品是否有效
def is_valid_product(product):
    required_fields = ['Title', 'Price', 'Image URL']
    missing_fields = [field for field in required_fields if field not in product or not product[field] or product[field] == 'N/A']
    if missing_fields:
        print(f"跳過此商品，因為缺少以下必填欄位: {missing_fields}, 商品資料: {product}")
        return False
    return True

# 判斷商品名稱是否重複
def is_duplicate_title(title, existing_titles):
    return title in existing_titles

# 將每個產品上傳到 WooCommerce
def upload_product_to_woocommerce(product, existing_titles):
    if not is_valid_product(product):
        print(f"跳過此商品，因為有 N/A 值或缺少必填欄位: {product.get('Title', '未知標題')}")
        return

    if is_duplicate_title(product['Title'], existing_titles):
        print(f"跳過此商品，因為名稱重複: {product['Title']}")
        return
    # 去除商品名稱中的 "BJ4動漫"
    product['Title'] = product['Title'].replace('│BJ4動漫', '').strip()

    if is_duplicate_title(product['Title'], existing_titles):
        print(f"跳過此商品，因為名稱重複: {product['Title']}")
        return

    # 處理價格
    price = product['Price'].replace('NT$', '').replace('$', '').strip()
    try:
        modified_price = str(round((float(price) * 0.85 / 4.2 * 2), 2))  # 價格修改為除以4.2再乘以2
    except ValueError:
        print(f"跳過此商品，因為價格無法轉換為數字: {product['Title']}")
        return
    
    # 提取並處理圖片 URL
    image_url = product['Image URL']

    # 數據符合 WooCommerce 規格
    data = {
        "name": product['Title'],
        "type": "simple",
        "regular_price": modified_price,
        "images": [
            {
                "src": image_url
            }
        ],
        "categories": [
            {
                "id": 35  # 預購分類的實際分類 ID
            }
        ]
    }

    # 發送 API 請求創建產品
    try:
        response = wcapi.post("products", data)
        if response.status_code == 201:
            print(f"成功上傳產品: {product['Title']}")
            existing_titles.add(product['Title'])  # 添加已上傳的商品名稱到集合中
        else:
            print(f"上傳失敗: {product['Title']}，錯誤: {response.json()}")
    except Exception as e:
        print(f"發生錯誤: {str(e)} 在上傳產品: {product['Title']}")

if __name__ == '__main__':
    # 設定 CSV 文件夾的路徑
    csv_folder_path = '/home/ubuntu/books/bj4/'  # 替換為包含所有 CSV 文件的文件夾路徑

    # 從多個 CSV 文件讀取並上傳產品
    upload_products_from_multiple_csvs(csv_folder_path)

