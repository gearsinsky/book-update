from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import requests
import base64

def get_book_info_selenium(url, username, password, captcha_solver_api_key):
    # 使用 webdriver_manager 來自動安裝正確版本的 ChromeDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 使用無頭模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://cart.books.com.tw/member/login")

    # 填寫帳號和密碼，這些元素的選擇器根據實際頁面進行調整
    driver.find_element(By.ID, "login_id").send_keys(username)  # 使用帳號輸入框的 ID，保持小寫一致性
    driver.find_element(By.ID, "login_id").send_keys(password)  # 使用密碼輸入框的 ID，保持小寫一致性

    # 獲取驗證碼圖片
    captcha_img = driver.find_element(By.ID, "captcha_img").find_element(By.TAG_NAME, "img")
    captcha_src = captcha_img.get_attribute("src")
    captcha_response = requests.get(captcha_src)
    
    # 保存驗證碼圖片
    with open("captcha.jpg", "wb") as f:
        f.write(captcha_response.content)

    # 使用 2Captcha 解決驗證碼
    captcha_solver_url = "http://2captcha.com/in.php"
    captcha_payload = {
        "key": captcha_solver_api_key,
        "method": "base64",
        "json": 1,
        "body": base64.b64encode(open("captcha.jpg", "rb").read()).decode("utf-8")
    }
    captcha_solver_response = requests.post(captcha_solver_url, data=captcha_payload).json()
    if captcha_solver_response.get("status") != 1:
        driver.quit()
        return {"error": f"無法提交驗證碼給服務，返回：{captcha_solver_response}"}
    
    captcha_id = captcha_solver_response.get("request")

    # 等待驗證碼結果返回
    time.sleep(15)
    captcha_result_url = f"http://2captcha.com/res.php?key={captcha_solver_api_key}&action=get&id={captcha_id}&json=1"
    captcha_text_response = requests.get(captcha_result_url).json()
    while captcha_text_response.get("status") == 0:
        time.sleep(5)
        captcha_text_response = requests.get(captcha_result_url).json()

    if captcha_text_response.get("status") != 1:
        driver.quit()
        return {"error": f"無法獲取驗證碼解決結果，返回：{captcha_text_response}"}
    
    captcha_text = captcha_text_response.get("request")

    # 自動填寫驗證碼
    captcha_input = driver.find_element(By.NAME, "captcha")
    captcha_input.send_keys(captcha_text)

    # 提交登入
    driver.find_element(By.ID, "books_login").click()
    time.sleep(3)  # 等待頁面加載

    # 登入成功後前往目標頁面
    driver.get(url)
    print("登入成功")
    time.sleep(3)  # 等待頁面加載

    # 獲取網頁內容
    page_source = driver.page_source
    driver.quit()
    print("website ok")

    # 使用 BeautifulSoup 解析頁面
    soup = BeautifulSoup(page_source, 'html.parser')
    description_section = soup.find("div", string=lambda text: text and "內容簡介" in text)
    description = description_section.get_text(strip=True) if description_section else "無法找到內容簡介"

    detail_section = soup.find("div", class_="bd")
    details = detail_section.get_text(strip=True) if detail_section else "無法找到詳細資料"

    return {
        "description": description,
        "details": details
    }

# 書籍頁面 URL
url = "https://www.books.com.tw/products/0010999782?loc=P_0019_001"
username = "gearsinsky"  # 替換為你的帳號
password = "Azkiuop1597@"  # 替換為你的密碼
captcha_solver_api_key = "6506dd88f810b34ecb4e2835250b3bf2"  # 替換為你的 2Captcha API 金鑰

book_info = get_book_info_selenium(url, username, password, captcha_solver_api_key)

if "error" in book_info:
    print(book_info["error"])
else:
    print("內容簡介:", book_info["description"])
    print("詳細資料:", book_info["details"])

# Debug: 提示使用者檢查 debug.html 以了解網頁的實際結構
print("請檢查 debug.html 以了解網頁的實際結構，並確定選擇器是否正確。")

