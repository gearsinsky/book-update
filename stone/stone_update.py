from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# 設定 Selenium 遠端 WebDriver 配置
selenium_hub_url = "http://localhost:4444/wd/hub"

# 設定 ChromeOptions，例如無頭模式等
chrome_options = Options()
chrome_options.add_argument("--headless")  # 可以選擇是否使用無頭模式
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 使用 Remote WebDriver 來連接到 Selenium 容器
driver = webdriver.Remote(
    command_executor=selenium_hub_url,
    options=chrome_options
)

# Step 1: 登入金石堂網站
driver.get("https://www.kingstone.com.tw/login")
time.sleep(2)  # 等待頁面加載

# 輸入帳號
email_input = driver.find_element(By.ID, "loginID")
email_input.send_keys("gearsinsky@gmail.com")

# 輸入密碼
password_input = driver.find_element(By.ID, "loginPW")
password_input.send_keys("qazwsx123e")
password_input.send_keys(Keys.RETURN)  # 提交表單
time.sleep(3)  # 等待登入完成

# Step 2: 進入書籍頁面
driver.get("https://www.kingstone.com.tw/book/ra")
time.sleep(3)  # 等待頁面加載

# Step 3: 抓取書籍連結並進入
book_links = []
books = driver.find_elements(By.CLASS_NAME, "coverbox")  # 找到所有包含書籍連結的元素

for book in books:
    link_element = book.find_element(By.TAG_NAME, "a")
    book_link = link_element.get_attribute("href")
    book_links.append(book_link)


# Step 4: 抓取每本書的資訊

book_data = []
for link in book_links:
    driver.get(link)  # 點擊進入每個書籍連結
    time.sleep(2)  # 等待頁面加載

    try:
        # 書名
        title_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pdname_basic")))
        title = title_element.text
        # 圖片 URL
        image_element = driver.find_element(By.CSS_SELECTOR, "img.imgFrame")
        image_url = image_element.get_attribute("src")
        
        # 價格
        price = driver.find_element(By.CLASS_NAME, "sty2.txtSize2").text
        
        # 內容簡介
        description = driver.find_element(By.CLASS_NAME, "pdintro_txtfield").text
        
        # 分級
        grade_elements = driver.find_elements(By.CLASS_NAME, "table_2col_deda")
        grade = ""
        for element in grade_elements:
            label = element.find_element(By.CLASS_NAME, "table_th").text
            if label == "分級":
                grade = element.find_element(By.CLASS_NAME, "table_td").text
                break
        
        # 商品規格
        specs = ""
        for element in grade_elements:
            label = element.find_element(By.CLASS_NAME, "table_th").text
            if label == "商品規格":
                specs = element.find_element(By.CLASS_NAME, "table_td").text
                break

        # 收集資料
        book_data.append({
            "Title": title,
            "Image URL": image_url,
            "Price": price,
            "Description": description,
            "Grade": grade,
            "Specification": specs,
            "Link": link
        })
    except Exception as e:
        print(f"無法抓取資料：{link}，錯誤：{e}")

# Step 5: 匯出成 CSV
df = pd.DataFrame(book_data)
df.to_csv("kingstone_books.csv", index=False, encoding="utf-8-sig")

print("資料已匯出至 kingstone_books.csv")

# 關閉瀏覽器
driver.quit()
