import csv
import requests
from woocommerce import API
from urllib.parse import urlparse, parse_qs

# 設定 WooCommerce API 憑證
wcapi = API(
    url="http://52.192.228.25/",  # 替換為你的 WooCommerce 網站 URL
    consumer_key="ck_2ba733f257100d48cd27e9553befe870cfff9694",  # 替換為你的 API Key
    consumer_secret="cs_78573ea041f71c9005bfcf14896e654e0de628b9",  # 替換為你的 API Secret
    version="wc/v3"
)

# 讀取 CSV 文件
def read_csv_file(csv_file_path):
    products = []
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)
    return products

# 提取實際圖片 URL
def extract_image_url(image_url):
    parsed_url = urlparse(image_url)
    query_params = parse_qs(parsed_url.query)
    if 'i' in query_params:
        return query_params['i'][0]  # 提取圖片的實際 URL
    return image_url

# 處理價格的輔助函數，確保價格是數字字符串
def clean_price(price):
    return price.replace('NT$', '').replace('$', '').strip()

def is_valid_product(product):
    return all(value != 'N/A' for value in [product['title'], product['price'], product['image_url']])

# 將每個產品上傳到 WooCommerce
def upload_product_to_woocommerce(product):
    if not is_valid_product(product):
        print(f"跳過此商品，因為有 N/A 值: {product['title']}")
        return

    # 處理價格
    price = clean_price(product['price'])

    # 提取並處理圖片 URL
    image_url = extract_image_url(product['image_url'])

    data = {
        "name": product['title'],  # 只使用 title
        "type": "simple",
        "regular_price": price,  # 價格必須是字符串格式
        "images": [{"src": image_url}],  # 使用處理後的圖片 URL
    }

    # 發送 API 請求創建產品
    try:
        response = wcapi.post("products", data)
        if response.status_code == 201:
            print(f"成功上傳產品: {product['title']}")
        else:
            print(f"上傳失敗: {product['title']}，錯誤: {response.json()}")
    except Exception as e:
        print(f"發生錯誤: {str(e)} 在上傳產品: {product['title']}")

if __name__ == '__main__':
    # 讀取 books.csv 文件
    csv_file_path = '/home/ubuntu/books/books.csv'  # 替換為你的 CSV 文件的路徑
    products = read_csv_file(csv_file_path)

    # 確認 CSV 檔案是否成功載入
    if len(products) == 0:
        print("CSV 文件沒有讀取到任何產品，請檢查文件格式或路徑是否正確。")
    else:
        # 遍歷所有產品並上傳
        for product in products:
            upload_product_to_woocommerce(product)

