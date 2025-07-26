import pandas as pd
import os
import requests
import time
from datetime import datetime, timedelta
import pandas as pd
import csv
from datetime import datetime, timedelta

df = pd.read_csv('/content/merged_dataset.csv')

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



def get_brand_details(brand_id: int) -> dict:
    """Получает информацию по бренду."""
    url = "https://wildbox.ru/api/wb_dynamic/brands/"
    params = {'brand_ids': brand_id, 'date_from': DATE_FROM, 'date_to': DATE_TO, 'extra_fields': 'rating,reviews'}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        results = response.json().get('results', [])
        return results[0] if results else {}
    except requests.exceptions.RequestException: return {}
     

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
     

def get_seller_details(brand_id: int) -> dict:
    """Получает информацию по селлеру."""
    url = "https://wildbox.ru/api/wb_dynamic/sellers/"
    params = {'seller_ids': brand_id, 'date_from': DATE_FROM, 'date_to': DATE_TO, 'extra_fields': 'rating,reviews, name'}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        results = response.json().get('results', [])
        return results[0] if results else {}
    except requests.exceptions.RequestException: return {}
     
product_ids = df['Артикул']

results = []

for pid in product_ids:
    try:
        product_data = get_product_details(int(pid))
        if product_data:
            results.append(product_data)
        else:
            print(f'Нет данных для ID: {pid}')
    except Exception as e:
        print(f'Ошибка при обработке ID {pid}: {e}')

all_products = []
for product_list in results:
    all_products.extend(product_list)
fields = [
    "id", "rating"
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
        "rating": p.get("rating"),
    }
    rows.append(row)

csv_filename = "products_info_only_rating.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

seller_ids = df['seller_id']

results = []
i = 0
for pid in seller_ids:
    i += 1
    try:
        seller_data = get_seller_details(int(pid))
        if seller_data:
            results.append(seller_data)
            print(f"Получена {i}-ая строка")
        else:
            print(f'Нет данных для ID: {pid}')
    except Exception as e:
        print(f'Ошибка при обработке ID {pid}: {e}')

all_seller = []
for seller_list in results:
    all_seller.extend(seller_list)
fields = [
    "id", "rating", "reviews", "name"
]

rows = []
for p in results:
    row = {
        "id": p.get("id"),
        "rating": p.get("rating"),
        "reviews": p.get("reviews"),
        "name": p.get("name")
    }
    rows.append(row)


csv_filename = "seller_rating.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

brand_ids = df['brand_id']

results = []

i = 0
for pid in brand_ids:
    i += 1
    try:
        brand_data = get_brand_details(int(pid))
        if brand_data:
            results.append(brand_data)
            print(f"Получена {i}-ая строка")
        else:
            print(f'Нет данных для ID: {pid}')
    except Exception as e:
        print(f'Ошибка при обработке ID {pid}: {e}')

all_brand = []
for brand_list in results:
    all_brand.extend(brand_list)
fields = [
    "id", "rating", "reviews", "name"
]

rows = []
for p in results:
    row = {
        "id": p.get("id"),
        "rating": p.get("rating"),
        "reviews": p.get("reviews"),
        "name": p.get("name")
    }
    rows.append(row)

csv_filename = "brand_rating.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)


#==============================
# Объединение таблиц
#==============================
seller_df = pd.read_csv("/content/seller_rating.csv")
seller_df = seller_df.rename(columns={
    'name': 'Поставщик',
    'rating': 'seller_rating',
    'reviews': 'seller_reviews'
})

united_df = pd.read_csv("/content/united_R.csv")

merged_df = united_df.merge(
    seller_df[['Поставщик', 'seller_rating', 'seller_reviews']],
    on='Поставщик',
    how='left'
)

merged_df
