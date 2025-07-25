import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import shap

df = pd.read_csv("training.csv", sep=',')

TARGET_COLUMN = 'Позиция в выдаче'

print(f"ЦЕЛЕВАЯ ПЕРЕМЕННАЯ: {TARGET_COLUMN}")

if TARGET_COLUMN not in df.columns:
    print(f"ОШИБКА: Колонка '{TARGET_COLUMN}' не найдена!")
    exit()

print("\n" + "="*50)
print("ПОДГОТОВКА ДАННЫХ")
print("="*50)

data = df.copy()

unique_values = data[TARGET_COLUMN].nunique()
is_classification = unique_values < 20 and data[TARGET_COLUMN].dtype == 'object' or unique_values < 10

print(f"Тип задачи: {'Классификация' if is_classification else 'Регрессия'}")
print(f"Уникальных значений в целевой переменной: {unique_values}")

X = data.drop(TARGET_COLUMN, axis=1)
y = data[TARGET_COLUMN]

print(f"Количество признаков для обучения: {X.shape[1]}")
print(f"Признаки: {list(X.columns)}")

categorical_columns = X.select_dtypes(include=['object']).columns
if len(categorical_columns) > 0:
    print(f"\nОбработка категориальных признаков: {list(categorical_columns)}")
    le_dict = {}
    for col in categorical_columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        le_dict[col] = le

if is_classification and y.dtype == 'object':
    le_target = LabelEncoder()
    y = le_target.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\nОбучающая выборка: {X_train.shape[0]} записей")
print(f"Тестовая выборка: {X_test.shape[0]} записей")

# ============= ОБУЧЕНИЕ МОДЕЛИ =============
print("\n" + "="*50)
print("ОБУЧЕНИЕ МОДЕЛИ")
print("="*50)

if is_classification:
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print(f"Точность модели: {accuracy_score(y_test, y_pred):.4f}")
    print("\nОтчет по классификации:")
    print(classification_report(y_test, y_pred))
else:
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")

# ============= АНАЛИЗ ВАЖНОСТИ ПРИЗНАКОВ =============
print("\n" + "="*50)
print("АНАЛИЗ ВАЖНОСТИ ПРИЗНАКОВ")
print("="*50)

feature_importance = model.feature_importances_
feature_names = X.columns

importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': feature_importance
}).sort_values('importance', ascending=False)

print("ТОП-10 самых важных признаков:")
print(importance_df.head(10))

print("\n" + "="*50)
print("SHAP АНАЛИЗ (детальное объяснение)")
print("="*50)

# Создание SHAP explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test[:100])  # Анализируем первые 100 записей

if is_classification and len(shap_values) > 1:
    shap_values = shap_values[1]

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test[:100], feature_names=feature_names, plot_type="bar", show=False)
plt.title('SHAP Bar Plot - Средняя важность признаков')
plt.tight_layout()
plt.show()

# ============= СВОДНЫЙ ОТЧЁТ =============
print("\n" + "="*50)
print("СВОДНЫЙ ОТЧЁТ")
print("="*50)

print(f"Тип задачи: {'Классификация' if is_classification else 'Регрессия'}")
print(f"Количество записей: {len(data)}")
print(f"Количество признаков: {len(feature_names)}")

if is_classification:
    print("\n" + "-"*50)
    print(f"ТОЧНОСТЬ МОДЕЛИ (ACCURACY): {accuracy_score(y_test, y_pred):.4f}")
    print("-"*50 + "\n")
else:
    from sklearn.metrics import mean_absolute_error
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print("\n" + "-"*50)
    print("МЕТРИКИ КАЧЕСТВА РЕГРЕССИИ:")
    print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
    print(f"MAE (Средняя абсолютная ошибка): {mae:.4f}")
    print(f"RMSE (Среднеквадратичная ошибка): {rmse:.4f}")
    print("-"*50 + "\n")

    if len(y_test) > 0:
        mean_y = np.mean(y_test)
        print(f"Среднее значение целевой переменной: {mean_y:.2f}")
        print(f"MAE составляет {mae/mean_y*100:.1f}% от среднего значения")
        print(f"RMSE составляет {rmse/mean_y*100:.1f}% от среднего значения\n")

print(f"\nТОП-5 самых важных признаков:")
for i, row in importance_df.head(5).iterrows():
    print(f"{row['feature']}: {row['importance']:.4f}")


print("\n" + "="*50)
print("СОХРАНЕНИЕ МОДЕЛИ")
print("="*50)

import joblib
joblib.dump(model, 'sales_model.pkl')

importance_df.to_csv('feature_importance.csv', index=False)
