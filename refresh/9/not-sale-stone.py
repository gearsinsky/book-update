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
chrome_options.add_argument("--headless")  # 可以選擇是否使用無頭模式
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 使用 Remote WebDriver 來連接到 Selenium 容器
try:
    driver = webdriver.Remote(
        command_executor=selenium_hub_url,
        options=chrome_options
    )
except Exception as e:
    print(f"無法連接到 Selenium Hub：{e}")
    exit(1)

# 設定要抓取的頁數
start_page = 1
end_page = 3

# 迴圈遍歷每一頁
for page in range(start_page, end_page + 1):
    # Step 2: 進入書籍頁面
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        try:
            driver.get(f"https://www.kingstone.com.tw/book/pk/?buy=b1&page={page}")
            wait = WebDriverWait(driver, 30)  # 增加等待時間
            
            # 第一頁特別加入額外的等待
            if page == 1:
                time.sleep(5)  # 額外等待以確保 JavaScript 加載完成
            
            wait.until(EC.presence_of_element_located((By.ID, "displayCSS")))  # 等待主要容器加載
            break  # 成功加載，退出重試循環
        except TimeoutException:
            print(f"書籍頁面加載超時，頁面：{page}，重試中（{retry_count + 1}/{max_retries}）...")
            retry_count += 1
            time.sleep(5)  # 等待後再重試
    if retry_count == max_retries:
        print(f"頁面 {page} 加載失敗，跳過此頁")
        continue

    # Step 3: 抓取書籍資訊
    book_titles = []
    try:
        container = driver.find_element(By.ID, "displayCSS")  # 找到包含所有書籍的主要容器
        books = container.find_elements(By.CLASS_NAME, "mod_prod_card")  # 找到所有包含書籍的元素
        for book in books:
            try:
                title_element = book.find_element(By.CSS_SELECTOR, "h3.pdnamebox a")  # 找到書籍標題元素
                title = title_element.text
                book_titles.append(title)
            except NoSuchElementException:
                print(f"無法找到書名元素：{book}")
            except Exception as e:
                print(f"抓取書名過程中發生錯誤：{e}")
    except NoSuchElementException as e:
        print(f"無法找到主要容器元素：{e}")
    except Exception as e:
        print(f"抓取書籍資訊過程中發生錯誤：{e}")

    # Step 4: 匯出成 CSV
    df = pd.DataFrame(book_titles, columns=["Title"])
    csv_filename = f"kingstone_books_titles_page_{page}.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")

    print(f"資料已匯出至 {csv_filename}")

# 關閉瀏覽器
driver.quit()

