from flask import Flask, request, jsonify, send_from_directory
from ultralytics import YOLO
import cv2
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Загрузка модели YOLOv8
print("Загрузка модели YOLOv8...")
model = YOLO('yolov8n.pt')
print("Модель загружена!")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Изображение не загружено'}), 400

    file = request.files['image']
    
    # Чтение изображения
    img_array = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    # Запуск детекции
    results = model(img)
    annotated_frame = results[0].plot()
    
    # Классы потенциально брошенных предметов
    # 24 - backpack (рюкзак), 25 - umbrella (зонт)
    # 26 - handbag (сумка), 28 - suitcase (чемодан)
    SUSPICIOUS_CLASSES = [24, 25, 26, 28]
    PERSON_CLASS = 0
    
    suspicious_items = []
    persons = []
    
    # Сбор координат людей и подозрительных предметов
    for r in results[0].boxes:
        class_id = int(r.cls)
        box = r.xyxy[0].tolist()
        if class_id == PERSON_CLASS:
            persons.append(box)
        elif class_id in SUSPICIOUS_CLASSES:
            suspicious_items.append({
                'class': model.names[class_id],
                'bbox': box,
                'class_id': class_id
            })
    
    # Проверка наличия людей рядом с подозрительными предметами
    abandoned_items = []
    for item in suspicious_items:
        item_center_x = (item['bbox'][0] + item['bbox'][2]) / 2
        item_center_y = (item['bbox'][1] + item['bbox'][3]) / 2
        is_abandoned = True
        
        for person in persons:
            person_center_x = (person[0] + person[2]) / 2
            person_center_y = (person[1] + person[3]) / 2
            distance = ((item_center_x - person_center_x)**2 + (item_center_y - person_center_y)**2)**0.5
            
            # Если человек рядом (расстояние менее 200 пикселей)
            if distance < 200:
                is_abandoned = False
                break
        
        if is_abandoned:
            abandoned_items.append(item)
    
    # Вывод предупреждения в терминал
    if abandoned_items:
        print("ВНИМАНИЕ! Обнаружены потенциально брошенные предметы:")
        for item in abandoned_items:
            print(f"   - {item['class']}")
    else:
        print("Брошенных предметов не обнаружено")
    
    # Сохранение обработанного изображения
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    result_filename = f'result_{timestamp}.jpg'
    result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
    cv2.imwrite(result_path, annotated_frame)
    
    # Сбор статистики по всем обнаруженным объектам
    detected_classes = {}
    for r in results[0].boxes:
        class_id = int(r.cls)
        class_name = model.names[class_id]
        detected_classes[class_name] = detected_classes.get(class_name, 0) + 1
    
    total_objects = len(results[0].boxes)
    abandoned_list = [item['class'] for item in abandoned_items]
    
    return jsonify({
        'success': True,
        'result_image': f'/static/{result_filename}',
        'total_objects': total_objects,
        'detected_classes': detected_classes,
        'abandoned_items': abandoned_list,
        'abandoned_count': len(abandoned_items)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)