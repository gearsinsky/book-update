import requests
from bs4 import BeautifulSoup

def get_book_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 抓取內容簡介
        description_section = soup.find("div", class_="bd")
        if description_section:
            description = description_section.get_text(strip=True)
        else:
            description = "無法找到內容簡介"
        
        # 抓取詳細資料
        detail_section = soup.find("div", class_="type02_p003 clearfix")
        if detail_section:
            details = detail_section.get_text(strip=True)
        else:
            details = "無法找到詳細資料"
        
        return {
            "description": description,
            "details": details
        }
    else:
        return {"error": f"無法獲取頁面，狀態碼：{response.status_code}"}

# 書籍頁面 URL
url = "https://www.books.com.tw/products/0010999782?loc=P_0019_001"
book_info = get_book_info(url)

if "error" in book_info:
    print(book_info["error"])
else:
    print("內容簡介:", book_info["description"])
    print("詳細資料:", book_info["details"])

