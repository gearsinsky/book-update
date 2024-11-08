from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

# 設定 Selenium 遠端 WebDriver 配置
selenium_hub_url = "http://localhost:4444/wd/hub"

# 設定 ChromeOptions，例如無頭模式等
chrome_options = Options()
chrome_options.add_argument("--headless")  # 可以選擇是否使用無頭模式
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 防止被檢測到是自動化工具
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# 使用 Remote WebDriver 來連接到 Selenium 容器
driver = webdriver.Remote(
    command_executor=selenium_hub_url,
    options=chrome_options
)

# 使用 JavaScript 來隱藏 webdriver 痕跡
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# 設定要抓取的頁數
start_page = 0
end_page = 4  # 抓取第 1 至第 5 頁

# 保存商品的資料
product_data = []

# 遍歷從第 start_page 到 end_page 的網頁
for page in range(start_page, end_page + 1):
    # Step 1: 載入 Shopee 商店頁面
    try:
        url = f"https://shopee.tw/kababan1234?categoryId=100643&itemId=18930271048&page={page}&sortBy=ctime&tab=0&upstream=search"
        driver.get(url)
        wait = WebDriverWait(driver, 30)  # 增加等待時間到 30 秒
        
        # 使用 JavaScript 等待頁面完全加載
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # 等待商品列表元素出現
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'shop-page__all-products-section')]")))  # 等待商品列表加載
        time.sleep(10)  # 額外等待頁面完全加載，增加到 10 秒以應對頁面延遲  # 額外等待頁面完全加載
    except TimeoutException:
        print(f"商品頁面加載超時，頁面：{page}，請檢查網頁是否正常加載或者網絡是否穩定。")
        continue
    except Exception as e:
        print(f"進入商品頁面過程中發生錯誤：{e}，頁面：{page}，請檢查網頁結構是否更改或者網絡是否穩定。")
        continue

    # Step 2: 抓取商品資訊
    try:
        products = driver.find_elements(By.XPATH, "//a[contains(@class, 'contents')]")
        for product in products:
            # 書名（商品名稱）
            try:
                title_element = product.find_element(By.XPATH, ".//div[contains(@class, 'whitespace-normal line-clamp-2')]")
                title = title_element.text
            except NoSuchElementException as e:
                title = "N/A"
                print(f"無法找到書名元素，頁面：{page}，錯誤：{e}")

            # 圖片 URL
            try:
                image_element = product.find_element(By.XPATH, ".//img")
                image_url = image_element.get_attribute("src")
            except NoSuchElementException as e:
                image_url = "N/A"
                print(f"無法找到圖片元素，頁面：{page}，錯誤：{e}")

            # 價格
            try:
                price_element = product.find_element(By.XPATH, ".//span[contains(@class, 'text-xs/sp4')]")
                price = price_element.text
            except NoSuchElementException as e:
                price = "N/A"
                print(f"無法找到價格元素，頁面：{page}，錯誤：{e}")

            # 收集商品資訊
            product_info = {
                "Title": title,
                "Image URL": image_url,
                "Price": price
            }
            product_data.append(product_info)

            # 列出抓取的商品資訊
            print(product_info)

    except NoSuchElementException as e:
        print(f"無法找到商品元素，頁面：{page}，錯誤：{e}")
    except Exception as e:
        print(f"抓取商品資訊過程中發生錯誤，頁面：{page}，錯誤：{e}")

    # Step 3: 每頁資料完成後匯出成 CSV
    df = pd.DataFrame(product_data)
    csv_filename = f"shopee_products_page_{page}.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
    print(f"資料已匯出至 {csv_filename}")

# 關閉瀏覽器
driver.quit()

