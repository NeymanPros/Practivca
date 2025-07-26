

import os
import requests
import time
from datetime import datetime, timedelta
import pandas as pd
import csv
from datetime import datetime, timedelta


if not all([AUTH_TOKEN, COMPANY_ID, USER_ID]):
    raise ValueError("Необходимо задать все переменные окружения в .env файле (AUTH_TOKEN, COMPANY_ID, USER_ID)")

HEADERS = {
    'Authorization': AUTH_TOKEN,
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'CompanyID': COMPANY_ID,
    'UserID': USER_ID,
    'Referer': 'https://wildbox.ru/dashboard/search-tops-analysis/formed',
    'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin',
    'Time-Zone': 'Europe/Moscow',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
}


DATE_TO = datetime.now().strftime('%Y-%m-%d')
DATE_FROM = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')


def get_product_details(product_id: int) -> dict:
    """Получает детальную информацию по одному товару."""
    url = "https://wildbox.ru/api/wb_dynamic/products/"
    extra_fields = ('orders,proceeds,in_stock_percent,lost_proceeds,orders_dynamic,proceeds_dynamic,quantity,price,discount,weighted_price,rating,seller,brand,subject,images,promos,sales_speed,old_price')
    params = {'product_ids': product_id, 'date_from': DATE_FROM, 'date_to': DATE_TO, 'extra_fields': extra_fields}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        results = response.json().get('results', [])
        return results[0] if results else {}
    except requests.exceptions.RequestException: return {}


INPUT_CSV = '/content/articls.csv'     
OUTPUT_CSV = 'product_data_output.csv'  
ID_COLUMN_NAME = 'Артикул'         

df_ids = pd.read_csv(INPUT_CSV)
product_ids = df_ids[ID_COLUMN_NAME]
results = []

i = 0

for pid in product_ids:
    i += 1
    try:
        product_data = get_product_details(int(pid))
        if product_data:
            results.append(product_data)
        else:
            print(f'Нет данных для ID: {pid}')
    except Exception as e:
        print(f'Ошибка при обработке ID {pid}: {e}')
    if i > 2:
      break

all_products = []
for product_list in results:
    all_products.extend(product_list)

fields = [
    "id", "orders", "proceeds", "quantity", "price",
    "old_price", "discount", "weighted_price",
    "name", "rating", "count_day_promos",
    "sales_speed", "seller_id", "seller_name", "brand_id", "brand_name",
    "count_images", "subject"
]

rows = []
for p in results:
    total_days = 0
    for promo in p.get('promos', []):
      start = datetime.strptime(promo['start_date'], '%Y-%m-%d')
      end = datetime.strptime(promo['end_date'], '%Y-%m-%d')
      duration = (end - start).days + 1  
      total_days += duration

    row = {
        "id": p.get("id"),
        "orders": p.get("orders"),
        "proceeds": p.get("proceeds"),
        "quantity": p.get("quantity"),
        "price": p.get("price"),
        "old_price": p.get("old_price"),
        "discount": p.get("discount"),
        "weighted_price": p.get("weighted_price"),
        "name": p.get("name"),
        "rating": p.get("rating"),
        "count_day_promos": total_days,
        "seller_id": p.get("seller", {}).get("id") if isinstance(p.get("seller"), dict) else None,
        "seller_name": p.get("seller", {}).get("name") if isinstance(p.get("seller"), dict) else None,
        "brand_id": p.get("brand", {}).get("id") if isinstance(p.get("brand"), dict) else None,
        "brand_name": p.get("brand", {}).get("name") if isinstance(p.get("brand"), dict) else None,
        "count_images": len(p.get("images")),
        "subject": p.get("subject")
    }
    rows.append(row)

csv_filename = "products_info_large.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
     

df1 = pd.read_csv("/content/final_dataset.csv")
df2 = pd.read_csv("/content/products_info.csv")

merged_df = df1.merge(df2, left_on="Артикул", right_on="id", how="inner")
merged_df.to_csv("merged_dataset.csv", index=False, encoding='utf-8-sig')
     
seller_df = pd.read_csv("/mnt/data/seller_rating.csv")
seller_df = seller_df.rename(columns={
    'name': 'Поставщик',
    'rating': 'seller_rating',
    'reviews': 'seller_reviews'
})

united_df = pd.read_csv("/mnt/data/united_R.csv")

merged_df = united_df.merge(
    seller_df[['Поставщик', 'seller_rating', 'seller_reviews']],
    on='Поставщик',
    how='left'
)

merged_df
