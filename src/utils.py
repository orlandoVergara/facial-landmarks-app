# src/utils.py
"""
Funciones auxiliares para el manejo de imágenes (PIL y OpenCV).
"""

import cv2
import numpy as np
from PIL import Image

def pil_to_cv2(pil_image):
    """
    Convierte una imagen de formato PIL (RGB) a formato OpenCV (BGR).
    """
    # Convertir de PIL a numpy array
    img_array = np.array(pil_image)
    
    # Si la imagen tiene canal Alfa (PNG), descartarlo
    if img_array.shape[2] == 4:
        img_array = img_array[:, :, :3]
        
    # Convertir de RGB (PIL) a BGR (OpenCV)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    return img_bgr

def cv2_to_pil(cv2_image):
    """
    Convierte una imagen de formato OpenCV (BGR) a formato PIL (RGB).
    """
    # Convertir de BGR (OpenCV) a RGB (PIL)
    img_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    
    # Convertir de numpy array a imagen PIL
    return Image.fromarray(img_rgb)

def resize_image(image, max_width=800):
    """
    Redimensiona una imagen (formato OpenCV) si excede un ancho máximo,
    manteniendo la relación de aspecto.
    """
    alto, ancho = image.shape[:2]
    
    # Si la imagen ya es más pequeña que el máximo, no hacer nada
    if ancho <= max_width:
        return image
    
    # Calcular la nueva altura manteniendo la relación de aspecto
    ratio = max_width / float(ancho)
    nuevo_alto = int(alto * ratio)
    nuevo_ancho = max_width
    
    # Redimensionar la imagen
    imagen_redimensionada = cv2.resize(image, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)
    
    return imagen_redimensionada