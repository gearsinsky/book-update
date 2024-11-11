#!/bin/bash
# 執行腳本
# 新增stone/bl新書
source /home/ubuntu/books/venv/bin/activate
nohup python3 /home/ubuntu/books/stone/bl/stone-update-page.py > /home/ubuntu/logs/stone-update-page.log 2>&1 &
nohup python3 /home/ubuntu/books/stone/bl/product-upload-all-csv.py > /home/ubuntu/logs/product-upload-all-csv.log 2>&1 &
# rm /home/ubuntu/books/stone/bl/*.csv  # 保留 CSV 文件，以便覆蓋

# 新增stone/comics新書
for i in {1..9}
do
    nohup python3 /home/ubuntu/books/stone/comics/${i}/stone-update-page.py > /home/ubuntu/logs/stone-comics-${i}-update.log 2>&1 &
    nohup python3 /home/ubuntu/books/stone/comics/${i}/product-upload.py > /home/ubuntu/logs/product-upload-comics-${i}.log 2>&1 &
    # rm /home/ubuntu/books/stone/comics/${i}/*.csv  # 保留 CSV 文件，以便覆蓋
done

# amazon 更新
nohup python3 /home/ubuntu/books/amazon/bl/amazon-book-bl.py > /home/ubuntu/logs/amazon-book-bl.log 2>&1 &
nohup python3 /home/ubuntu/books/amazon/bl/product-upload-bl.py > /home/ubuntu/logs/product-upload-bl.log 2>&1 &
# rm /home/ubuntu/books/amazon/bl/*.csv  # 保留 CSV 文件，以便覆蓋

nohup python3 /home/ubuntu/books/amazon/comics/amazon-book.py > /home/ubuntu/logs/amazon-book.log 2>&1 &
nohup python3 /home/ubuntu/books/amazon/comics/product-upload-comics.py > /home/ubuntu/logs/product-upload-comics.log 2>&1 &
# rm /home/ubuntu/books/amazon/comics/*.csv  # 保留 CSV 文件，以便覆蓋

# BJ4 更新
nohup python3 /home/ubuntu/books/bj4/bj4-book-update.py > /home/ubuntu/logs/bj4-book-update.log 2>&1 &
nohup python3 /home/ubuntu/books/bj4/product-upload-bj4.py > /home/ubuntu/logs/product-upload-bj4.log 2>&1 &
# rm /home/ubuntu/books/bj4/*.csv  # 保留 CSV 文件，以便覆蓋

# 下架產品抓取
nohup python3 /home/ubuntu/books/refresh/not-sale-product-stone-bl.py > /home/ubuntu/logs/not-sale-product-stone-bl.log 2>&1 &
nohup python3 /home/ubuntu/books/refresh/delete-same-product-csv.py > /home/ubuntu/logs/delete-same-product-csv.log 2>&1 &
nohup python3 /home/ubuntu/books/refresh/delete-same-product-woocommerce.py > /home/ubuntu/logs/delete-same-product-woocommerce.log 2>&1 &
# rm /home/ubuntu/books/refresh/*.csv  # 保留 CSV 文件，以便覆蓋

# 清理重複商品
nohup python /path/to/refresh/delete-same-product-csv.py > /home/ubuntu/logs/delete-same-product-csv-refresh.log 2>&1 &
nohup python /path/to/stone/bl/product-upload-all-csv.py > /home/ubuntu/logs/product-upload-all-csv-refresh.log 2>&1 &
