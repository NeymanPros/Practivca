import pandas as pd

products = pd.read_csv('/content/big_no_R.csv')
brands = pd.read_csv('/content/brand_rating.csv')

brands = brands.rename(columns={
    'id': 'brand_id',
    'rating': 'brand_rating',
    'reviews': 'brand_reviews',
    'name': 'brand_name'
})

brands_unique = brands.drop_duplicates(subset=['brand_id'], keep='first')

merged = products.merge(
    brands_unique,
    how='left',
    left_on='brand_id',
    right_on='brand_id'
)

merged = merged.drop(columns=['brand_name_y'])

print(f"Исходная таблица: {products.shape[0]} строк")
print(f"После удаления дубликатов в брендах: {brands_unique.shape[0]} строк")
print(f"После объединения: {merged.shape[0]} строк")
merged.to_csv('big_with_brand_info.csv', index=False)

     
only_rating = pd.read_csv('/content/only_rating.csv')
merged_rating = merged.merge(
    only_rating,
    how='left',
    left_on='Артикул',
    right_on='id'
)

print(f"Исходная таблица: {merged_rating.shape[0]} строк")
print(f"После удаления дубликатов в брендах: {only_rating.shape[0]} строк")
print(f"После объединения: {merged_rating.shape[0]} строк")
merged_rating.to_csv('merged_with_rating.csv', index=False)


seller_rating = pd.read_csv('/content/seller_rating.csv')
seller_rating = seller_rating.rename(columns={
    'id': 'seller_id',
    'rating': 'seller_rating',
    'reviews': 'seller_reviews',
    'name': 'seller_name'
})

seller_unique = seller_rating.drop_duplicates(subset=['seller_id'], keep='first')

final_merged = merged_rating.merge(
    seller_unique,
    how='left',
    left_on='seller_id',
    right_on='seller_id'
)

print(f"Исходная таблица: {merged_rating.shape[0]} строк")
print(f"После удаления дубликатов в брендах: {seller_unique.shape[0]} строк")
print(f"После объединения: {final_merged.shape[0]} строк")
final_merged.to_csv('final_merged.csv', index=False)
