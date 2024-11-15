#!/bin/bash
# 啟動虛擬環境
source /home/ubuntu/books/venv/bin/activate


# stone/bl 更新
#
nohup python3 /home/ubuntu/books/stone/bl/stone-update-bl.py > /home/ubuntu/logs/stone-update-bl.py.log 2>/home/ubuntu/logs/stone-update-bl.py-error.log &
wait

nohup python3 /home/ubuntu/books/stone/bl/product-upload-with-csv.py > /home/ubuntu/logs/product-upload-with-csv.log 2>/home/ubuntu/logs/product-upload-with-csv-error.log &
wait  # 等待當前指令執行完畢

# stone/comics 新書更新 (循環執行)
for i in {1..9}
do
    nohup python3 /home/ubuntu/books/stone/comics/${i}/stone-update-comics-${i}.py > /home/ubuntu/logs/stone-comics-${i}-update.log 2>/home/ubuntu/logs/stone-comics-${i}-update-error.log &
    wait

    nohup python3 /home/ubuntu/books/stone/comics/${i}/product-upload-stone-${i}.py > /home/ubuntu/logs/product-upload-comics-${i}.log 2>/home/ubuntu/logs/product-upload-comics-${i}-error.log &
    wait
done

# amazon 更新
nohup python3 /home/ubuntu/books/amazon/bl/amazon-book-bl.py > /home/ubuntu/logs/amazon-book-bl.log 2>/home/ubuntu/logs/amazon-book-bl-error.log &
wait

nohup python3 /home/ubuntu/books/amazon/bl/product-upload-amazon-bl.py > /home/ubuntu/logs/product-upload-amazon-bl.log 2>/home/ubuntu/logs/product-upload-amazon-bl-error.log &
wait

nohup python3 /home/ubuntu/books/amazon/comics/amazon-book-comics.py > /home/ubuntu/logs/amazon-book-comics.log 2>/home/ubuntu/logs/amazon-book-comics-error.log &
wait

nohup python3 /home/ubuntu/books/amazon/comics/product-upload-amazon-comics.py > /home/ubuntu/logs/product-upload-amazon-comics.log 2>/home/ubuntu/logs/product-upload-amazon-comics-error.log &
wait

# BJ4 更新
nohup python3 /home/ubuntu/books/bj4/bj4-book-update.py > /home/ubuntu/logs/bj4-book-update.log 2>/home/ubuntu/logs/bj4-book-update-error.log &
wait

nohup python3 /home/ubuntu/books/bj4/product-upload-bj4.py > /home/ubuntu/logs/product-upload-bj4.log 2>/home/ubuntu/logs/product-upload-bj4-error.log &
wait

# 下架產品抓取與重複刪除
nohup python3 /home/ubuntu/books/refresh/stone-not-sale-product-bl.py > /home/ubuntu/logs/stone-not-sale-product-bl.log 2>/home/ubuntu/logs/stone-not-sale-product-bl-error.log &
wait

nohup python3 /home/ubuntu/books/refresh/delete-same-product-with-csv.py > /home/ubuntu/logs/delete-same-product-with-csv.log 2>/home/ubuntu/logs/delete-same-product-with-csv-error.log &
wait

nohup python3 /home/ubuntu/books/refresh/delete-same-product-woocommerce.py > /home/ubuntu/logs/delete-same-product-woocommerce.log 2>/home/ubuntu/logs/delete-same-product-woocommerce-error.log &
wait

