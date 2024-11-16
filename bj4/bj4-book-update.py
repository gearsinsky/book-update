from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import time

# 設定 Selenium 遠端 WebDriver 配置
selenium_hub_url = "http://localhost:4444/wd/hub"

# 設定 ChromeOptions，例如無頭模式等
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 暫時去掉無頭模式以便調試
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 使用 Remote WebDriver 來連接到 Selenium 容器
driver = webdriver.Remote(
    command_executor=selenium_hub_url,
    options=chrome_options
)

# Step 1: 登入網站
login_url = "https://www.myacg.com.tw/login.php?done=http%3A%2F%2Fwww.myacg.com.tw%2Fseller_market.php%3Fseller%3D8350"
driver.get(login_url)

try:
    wait = WebDriverWait(driver, 30)  # 增加等待時間到 30 秒

    # 輸入帳號
    account_input = wait.until(EC.presence_of_element_located((By.ID, "account")))
    account_input.send_keys("gearsinsky")  # 替換為你的帳號

    # 輸入密碼
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys("qazwsx123E")  # 替換為你的密碼

    # 點擊登入按鈕
    login_button = driver.find_element(By.CLASS_NAME, "bt-samp37.login_style")
    print("嘗試點擊登入按鈕")
    driver.execute_script("arguments[0].click();", login_button)
    print("登入按鈕已點擊")

    # 等待登入完成後的頁面加載
    wait.until(EC.url_changes(login_url))  # 等待 URL 變化來確認登入是否成功

except TimeoutException:
    print("登入過程超時，請檢查網頁是否正常加載。")
    driver.quit()
    exit()
except NoSuchElementException as e:
    print(f"登入過程中遇到元素找不到的錯誤：{e}")
    driver.quit()
    exit()

print("登入成功")
cookies = driver.get_cookies()
print("當前的 cookies:", cookies)

# Step 2: 開始抓取書籍的資料
# 設定要抓取的頁數
start_page = 1
end_page = 2

# 設置書籍資料的帳號、價格、圖片 URL 的列表
book_titles = []
book_prices = []
image_urls = []

# 迭例過每一頁
for page in range(start_page, end_page + 1):
    # 訪問指定頁面
    url = f"https://www.myacg.com.tw/seller_market.php?seller=8350&&pageID={page}"
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # 等待頁面加載完成
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list_content")))  # 等待書籍元素出現
    except TimeoutException:
        print(f"頁面 {page} 加載超時，請檢查網頁是否正常加載。")
        continue

    # 滾動頁面以確保所有圖片都被加載
    scroll_pause_time = 2  # 滾動後的等待時間
    while True:
        # 滾動到頁面底部
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(scroll_pause_time)

        # 獲取當前的頁面高度
        current_height = driver.execute_script("return window.scrollY + window.innerHeight")
        total_height = driver.execute_script("return document.body.scrollHeight")

        # 如果滾動到達頁面底部，則跳出迴圈
        if current_height >= total_height:
            break

    # Step 3: 抓取每本書的資訊
    book_data = []  # 書籍的每頁資料
    try:
        # 找到所有書籍元素
        books = driver.find_elements(By.CLASS_NAME, "list_content")  # 找到所有書籍項目
        for book in books:
            try:
                # 書名
                img_element = book.find_element(By.CLASS_NAME, "this_img")
                title = img_element.get_attribute("alt").strip()  # 書名可能在 alt 屬性中

                # 價格
                try:
                    price_element = book.find_element(By.CLASS_NAME, "list_price")
                    price = price_element.text.strip()
                except NoSuchElementException:
                    print(f"無法找到價格元素，設定價格為 'N/A'，請確認 class 名稱是否正確。")
                    price = "N/A"

                # 圖片 URL
                image_url = img_element.get_attribute("src").strip()

                # 收集抓取的資料
                book_info = {
                    'Title': title,
                    'Price': price,
                    'Image URL': image_url
                }
                book_data.append(book_info)

            except NoSuchElementException as e:
                print(f"無法找到某些元素，錯誤: {e}")
    except NoSuchElementException as e:
        print(f"無法找到書籍列表元素，錯誤: {e}")
        continue

    # Step 4: 將當前頁的資料儲存至 CSV 檔
    df = pd.DataFrame(book_data)
    csv_filename = f"/home/ubuntu/books/bj4/bj4_books_bl_page_{page}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"頁面 {page} 的資料已儲存至 {csv_filename}")

# 關閉瀏覽器
driver.quit()

