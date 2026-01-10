#!python

import easyocr

def parse_with_easyocr(image_path):
    # Ініціалізація читача (мови: англійська та українська, бо там є "по" і "Група")
    reader = easyocr.Reader(['en', 'uk']) 
    
    # detail=0 повертає тільки текст списком
    # paragraph=True намагається згрупувати текст у блоки
    results = reader.readtext(image_path, detail=0, paragraph=True)
    
    # EasyOCR поверне список рядків. Далі їх треба просто відфільтрувати.
    for line in results:
        print(line)

# Запуск
parse_with_easyocr("695de13768dac_GPV.png")
