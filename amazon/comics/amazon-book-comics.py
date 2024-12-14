from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd

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

# 設定要抓取的頁數
start_page = 1
end_page = 2

# 保存書的資料
book_data = []

# 過濾從第 start_page 到 end_page 的網頁
for page in range(start_page, end_page + 1):
    # Step 1: 載入 Amazon 書籍頁面
    try:
        driver.get(f"https://www.amazon.co.jp/s?i=stripbooks&rh=n%3A2278488051%2Cp_72%3A2227295051&s=featured-rank&language=zh&ref=Oct_d_otopr_S&page={page}")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "s-main-slot")))  # 等待主要書籍清單加載
    except TimeoutException:
        print(f"書籍頁面加載超時，頁面：{page}")
        continue
    except Exception as e:
        print(f"進入書籍頁面過程中發生錯誤：{e}")
        continue

    # Step 2: 抓取書籍資訊
    try:
        books = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
        for book in books:
            # 書名

            try:
                image_element = book.find_element(By.XPATH, ".//img[@class='s-image']")
                title = image_element.get_attribute("alt")  # 從 alt 屬性抓書名
            except NoSuchElementException:
                title = "N/A"

        # 圖片 URL
            try:
                image_url = image_element.get_attribute("src")
            except NoSuchElementException:
                image_url = "N/A"

            # 價格
            try:
                price_element = book.find_element(By.XPATH, ".//span[@class='a-price-whole']")
                price = price_element.text
            except NoSuchElementException:
                price = "N/A"

            # 收集書籍資訊
            book_info = {
                "Title": title,
                "Image URL": image_url,
                "Price": price
            }
            book_data.append(book_info)

            # 列出抓取的書籍資訊
            print(book_info)

    except NoSuchElementException as e:
        print(f"無法找到書籍元素：{e}")
    except Exception as e:
        print(f"抓取書籍資訊過程中發生錯誤：{e}")

    # Step 3: 每頁資料完成後出口成 CSV
    df = pd.DataFrame(book_data)
    csv_filename = f"/home/ubuntu/books/amazon/comics/amazon_books_comics_page_{page}.csv" 
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
    print(f"資料已匯出至 {csv_filename}")

# 關閉瀏覽器
driver.quit()
