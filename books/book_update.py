
import requests
from bs4 import BeautifulSoup
import csv
def fetch_books():
    url = 'https://www.books.com.tw/web/books_bmidm_1618/?pd=2&o=1&v=1'
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    books = []
    for item in soup.find_all(class_='item'):
        
        title_tag = item.find('h4')
        if title_tag and title_tag.find('a'):
            title = title_tag.find('a').get_text(strip=True)
        else:
            title = 'N/A'
        
        price_tags = item.find_all('strong')
        if len(price_tags) > 1:
            price = price_tags[1].get_text(strip=True) 
        else:
            price = 'N/A'
        
        image_tag = item.find('img', class_='cover')
        if image_tag:
            image_url = image_tag['src']
        else:
            image_url = 'N/A'

        books.append({
            'title': title,
            'price': price,
            'image_url': image_url
        
        })
    return books

if __name__ == '__main__':
        books = fetch_books()
        with open('books.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'price', 'image_url'])
            writer.writeheader()
            writer.writerows(books)

        print("書籍資料已成功寫入 books.csv")
