from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

# 迴圈遍歷每一頁
for page in range(start_page, end_page + 1):
    # Step 1: 登入金石堂網站
    try:
        driver.get("https://www.kingstone.com.tw/login")
        wait = WebDriverWait(driver, 10)

        # 使用顯式等待等待輸入框出現
        email_input = wait.until(EC.presence_of_element_located((By.ID, "loginID")))
        email_input.send_keys("gearsinsky@gmail.com")

        # 輸入密碼
        password_input = driver.find_element(By.ID, "loginPW")
        password_input.send_keys("qazwsx123e")
        password_input.send_keys(Keys.RETURN)  # 提交表單

        # 等待登入完成
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "coverbox")))
    except TimeoutException:
        print("登入超時，請檢查網頁是否正常加載。")
    except Exception as e:
        print(f"登入過程中發生錯誤：{e}")

    # Step 2: 進入書籍頁面
    try:
        driver.get(f"https://www.kingstone.com.tw/book/pb/?buy=b0&page={page}")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "coverbox")))  # 等待書籍列表加載
    except TimeoutException:
        print(f"書籍頁面加載超時，頁面：{page}")
        continue
    except Exception as e:
        print(f"進入書籍頁面過程中發生錯誤：{e}")
        continue

    # Step 3: 抓取書籍連結並進入
    book_links = []
    try:
        books = driver.find_elements(By.CLASS_NAME, "coverbox")  # 找到所有包含書籍連結的元素
        for book in books:
            link_element = book.find_element(By.TAG_NAME, "a")
            book_link = link_element.get_attribute("href")
            book_links.append(book_link)
    except NoSuchElementException as e:
        print(f"無法找到書籍連結元素：{e}")
    except Exception as e:
        print(f"抓取書籍連結過程中發生錯誤：{e}")

    # Step 4: 抓取每本書的資訊
    book_data = []
    for link in book_links:
        try:
            driver.get(link)  # 點擊進入每個書籍連結
            wait = WebDriverWait(driver, 10)

            # 書名
            try:
                title_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pdname_basic")))
                title = title_element.text
            except NoSuchElementException:
                print(f"無法找到書名元素：{link}")
                title = "N/A"

            # 圖片 URL
            try:
                image_element = driver.find_element(By.CLASS_NAME, "glightbox")
                image_url = image_element.get_attribute("href")
            except NoSuchElementException:
                print(f"無法找到圖片元素：{link}")
                image_url = "N/A"

            # 價格
            try:
                price_element = driver.find_element(By.CLASS_NAME, "sty2.txtSize2")
                price = price_element.text
            except NoSuchElementException:
                print(f"無法找到價格元素：{link}")
                price = "N/A"

            # 內容簡介
            try:
                description_element = driver.find_element(By.CLASS_NAME, "pdintro_txt1field.panelCon")
                description = description_element.text
            except NoSuchElementException:
                print(f"無法找到內容簡介元素：{link}")
                description = "N/A"

            # 分級和商品規格
            grade = "N/A"
            specs = "N/A"
            try:
                # 找到所有包含分級和商品規格的元素
                table_units = driver.find_elements(By.CLASS_NAME, "table_1unit_deda")
                if len(table_units) >= 3:
                    # 提取第二個 table_1unit_deda 中的第二個 table_td 值作為分級
                    try:
                        grade_element = table_units[1].find_elements(By.CLASS_NAME, "table_td")[1]
                        grade = grade_element.text.strip()
                    except (IndexError, NoSuchElementException):
                        print(f"無法找到分級元素：{link}")
                        grade = "N/A"

                    # 提取第三個 table_1unit_deda 中的第二個 table_td 值作為商品規格
                    try:
                        specs_element = table_units[2].find_elements(By.CLASS_NAME, "table_td")[1]
                        specs = specs_element.text.strip()
                    except (IndexError, NoSuchElementException):
                        print(f"無法找到商品規格元素：{link}")
                        specs = "N/A"
            except NoSuchElementException:
                print(f"無法找到分級或商品規格元素：{link}")

            # 收集資料
            book_info = {
                "Title": title,
                "Image URL": image_url,
                "Price": price,
                "Description": description,
                "Grade": grade,
                "Specification": specs,
                "Link": link
            }
            book_data.append(book_info)

            # 列出抓取的書籍資訊
            print(book_info)

        except TimeoutException:
            print(f"無法抓取資料：{link}，原因：等待元素超時")
        except NoSuchElementException as e:
            print(f"無法找到某個元素：{link}，錯誤：{e}")
        except Exception as e:
            print(f"無法抓取資料：{link}，錯誤：{e}")

    # Step 5: 匯出成 CSV
    df = pd.DataFrame(book_data)
    csv_filename = f"/home/ubuntu/books/stone/comics/1/stone_books_comics_page_{page}.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")

    print(f"資料已匯出至 {csv_filename}")

# 關閉瀏覽器
driver.quit()

