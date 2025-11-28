import requests
import base64
from PIL import Image
import io
import tkinter as tk
from tkinter import filedialog
import os

def select_image_file():
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Выберите изображение стола",
        filetypes=[
            ("Изображения", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("Все файлы", "*.*")
        ]
    )
    
    root.destroy()
    return file_path

def classify_table(image_path):
    try:
        if not os.path.exists(image_path):
            print(f"Файл не найден: {image_path}")
            return None
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(
                'http://localhost:5000/api/classify',
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка сервера: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

if __name__ == "__main__":
    
    image_path = select_image_file()
    
    if not image_path:
        print("Файл не выбран")
        exit()
    
    print(f"Выбран файл: {os.path.basename(image_path)}")
    
    result = classify_table(image_path)
    
    if result and result.get('status') == 'success':
        prediction = result['prediction']
        # confidence = result['confidence']
        
        if prediction == 'clean':
            print("Стол чистый")
        else:
            print("Стол грязный")
            
        #print(f"Вероятность: {confidence:.1%}")
        
            
    elif result and result.get('status') == 'error':
        print(f"Ошибка: {result.get('error', 'Unknown error')}")
    else:
        print("Не удалось получить результат")
        