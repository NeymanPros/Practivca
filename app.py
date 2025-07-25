from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

# Глобальная переменная для модели
model = None

def load_model():
    """Загружает модель при запуске приложения"""
    global model
    try:
        model = joblib.load('/home/alexe/AAA/sales_model.pkl')
        print("Модель успешно загружена!")
    except FileNotFoundError:
        print("Ошибка: файл sales_model.pkl не найден!")
        model = None
    except Exception as e:
        print(f"Ошибка при загрузке модели: {e}")
        model = None

@app.route('/')
def index():
    """Главная страница с формой"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Обработка предсказания модели"""
    if model is None:
        return jsonify({
            'error': 'Модель не загружена. Проверьте наличие файла sales_model.pkl'
        }), 500
    
    try:
        # Получаем данные из формы
        features = []
        for i in range(1, 19):  # параметры от param1 до param18
            param_value = request.form.get(f'param{i}')
            if param_value is None or param_value == '':
                return jsonify({
                    'error': f'Параметр {i} не может быть пустым'
                }), 400
            features.append(float(param_value))
        
        # Преобразуем в numpy array для модели
        input_data = np.array(features).reshape(1, -1)
        
        # Делаем предсказание
        prediction = model.predict(input_data)[0]
        
        # Если модель возвращает вероятности (классификация)
        try:
            prediction_proba = model.predict_proba(input_data)[0]
            return jsonify({
                'prediction': float(prediction),
                'probabilities': prediction_proba.tolist(),
                'features': features
            })
        except:
            # Для регрессии или моделей без predict_proba
            return jsonify({
                'prediction': float(prediction),
                'features': features
            })
            
    except ValueError as e:
        return jsonify({
            'error': f'Ошибка в данных: {str(e)}. Убедитесь, что все поля содержат числа.'
        }), 400
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при предсказании: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Загружаем модель при запуске
    load_model()
    
    # Запускаем приложение
    app.run(debug=True, host='0.0.0.0', port=5000)
    
