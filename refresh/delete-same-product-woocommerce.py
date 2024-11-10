import requests
from requests.auth import HTTPBasicAuth

# 設定 API Key 和 API Secret
API_URL = "https://54.199.115.191/wp-json/wc/v3/products"
API_KEY = "ck_7987669dbd82ab57e3e9a5f7b544a7dcbb603f3a"
API_SECRET = "cs_0b7d56a082508cc8543aab6765c5794698d7e5c3"

# 獲取所有商品
response = requests.get(API_URL, auth=HTTPBasicAuth(API_KEY, API_SECRET), verify=False)

if response.status_code == 200:
    products = response.json()
    product_dict = {}
    duplicate_found = False

    # 找到重複商品
    for product in products:
        name = product['name']
        if name in product_dict:
            duplicate_found = True
            print(f"找到重複商品: {name}")
            # 刪除重複商品
            duplicate_id = product['id']
            delete_response = requests.delete(f"{API_URL}/{duplicate_id}", auth=HTTPBasicAuth(API_KEY, API_SECRET), verify=False)
            if delete_response.status_code == 200:
                print(f"成功刪除商品: {name} (ID: {duplicate_id})")
            else:
                print(f"刪除失敗: {name} (ID: {duplicate_id})")
        else:
            product_dict[name] = product['id']

    if not duplicate_found:
        print("沒有重複商品")
else:
    print(f"無法獲取商品列表，錯誤碼: {response.status_code}")

