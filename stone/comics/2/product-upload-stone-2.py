import csv
import os
from woocommerce import API
from urllib.parse import urlparse

# 設定 WooCommerce API 憲註
wcapi = API(
    url="https://www.rising-shop-dg.com/",
    consumer_key="ck_7987669dbd82ab57e3e9a5f7b544a7dcbb603f3a",  # 替換為你的 API Key
    consumer_secret="cs_0b7d56a082508cc8543aab6765c5794698d7e5c3",  # 替換為你的 API Secret
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

# 輔助函數
# 提取實際圖片 URL
def extract_image_url(image_url):
    parsed_url = urlparse(image_url)
    # 檢查是否有版本參數並去掉
    clean_url = parsed_url._replace(query=None).geturl()
    return clean_url

# 處理價格的輔助函數，確保價格是數字字串
def clean_price(price):
    return price.replace('NT$', '').replace('$', '').strip()

# 處理規格的輔助函數，將不同格式的規格轉換為長寬高
def parse_dimensions(specification):
    try:
        # 嘗試將規格轉換為長、寬、高
        if '開' in specification:
            # 例如：55開17*21CM -> 提取尺寸部分
            dimensions = specification.split('開')[-1].strip().replace('CM', '').split('*')
        else:
            # 例如：20*13*1.2
            dimensions = specification.replace('CM', '').split('*')
        
        if len(dimensions) == 3:
            length, width, height = dimensions
        elif len(dimensions) == 2:
            length, width = dimensions
            height = "0"
        else:
            return None, None, None
        
        return length.strip(), width.strip(), height.strip()
    except Exception as e:
        print(f"規格解析錯誤: {specification}，錯誤: {e}")
        return None, None, None

# 取得 WooCommerce 中的分類 ID
def get_category_id_by_name(category_name):
    try:
        response = wcapi.get("products/categories")
        if response.status_code == 200:
            categories = response.json()
            for category in categories:
                if category['name'] == category_name:
                    return category['id']
        print(f"未找到分類: {category_name}")
        return None
    except Exception as e:
        print(f"取得分類 ID 時發生錯誤: {str(e)}")
        return None

# 判斷商品是否有效
def is_valid_product(product):
    required_fields = ['Title', 'Price', 'Image URL', 'Grade', 'Specification', 'Description']
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

    # 處理價格
    price = clean_price(product['Price'])
    try:
        modified_price = str(round((float(price) / 4.2) * 2, 2))  # 價格修改為除以4.2再乘以2
    except ValueError:
        print(f"跳過此商品，因為價格無法轉換為數字: {product['Title']}")
        return

    # 提取並處理圖片 URL
    image_url = extract_image_url(product['Image URL'])

    # 處理規格，將其轉換為長、寬、高
    length, width, height = parse_dimensions(product['Specification'])
    if length is None or width is None or height is None:
        print(f"跳過此商品，因為規格無法解析: {product['Title']}")
        return

    # 判斷作品的分類 ID
    if product['Grade'] == '限制級':
        category_id = 37
    elif product['Grade'] == '普通級':
        category_id = 36
    else:
        category_id = get_category_id_by_name(product['Grade'])
        if category_id is None:
            print(f"跳過此商品，因為分類無法找到: {product['Title']}")
            return

    # 數據符合 WooCommerce 規格
    data = {
        "name": product['Title'],  # 只使用 Title
        "type": "simple",
        "regular_price": modified_price,  # 價格必須是字串格式
        "images": [{"src": image_url}],  # 使用處理後的圖片 URL
        "categories": [{"id": category_id}],  # 使用分類 ID 而不是名稱
        "dimensions": {
            "length": length,
            "width": width,
            "height": height
        },
        "attributes": [
            {
                "name": "Specification",
                "options": [product['Specification']]  # 添加商品規格，使用 Specification 欄位
            }
        ],
        "description": product['Description']  # 添加商品描述，使用 Description 欄位
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
    csv_folder_path = '/home/ubuntu/books/stone/comics/2'  # 替換為包含所有 CSV 文件的文件夾路徑

    # 從多個 CSV 文件讀取並上傳產品
    upload_products_from_multiple_csvs(csv_folder_path)

