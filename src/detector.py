"""
Detector de landmarks faciales usando MediaPipe.
"""
import cv2
import math
import mediapipe as mp
from .config import FACE_MESH_CONFIG, LANDMARK_COLOR, LANDMARK_RADIUS, LANDMARK_THICKNESS


class FaceLandmarkDetector:
    """
    Clase para detectar y visualizar landmarks faciales.
    """
    
    def __init__(self):
        """Inicializa el detector de MediaPipe."""
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(**FACE_MESH_CONFIG)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # --- CONSTANTES PARA DIBUJO (Opción A) ---
        # Definir los estilos de dibujo que usaremos
        self.spec_puntos = self.mp_drawing.DrawingSpec(
            color=LANDMARK_COLOR, 
            thickness=LANDMARK_THICKNESS, 
            circle_radius=LANDMARK_RADIUS
        )
        self.spec_malla = self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
        self.spec_contornos = self.mp_drawing_styles.get_default_face_mesh_contours_style()

    
    def _distancia(self, p1_idx, p2_idx, landmarks, alto, ancho):
        """
        (Opción B) Helper para calcular la distancia euclidiana 2D entre dos landmarks.
        """
        p1 = landmarks.landmark[p1_idx]
        p2 = landmarks.landmark[p2_idx]
        x1, y1 = p1.x * ancho, p1.y * alto
        x2, y2 = p2.x * ancho, p2.y * alto
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    
    def analizar_expresiones(self, landmarks, alto, ancho):
        """
        (Opción B) Calcula métricas simples de expresión facial.
        
        Args:
            landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList):
                Lista de landmarks del rostro.
            alto (int): Alto de la imagen.
            ancho (int): Ancho de la imagen.
        
        Returns:
            dict: Diccionario con las métricas calculadas (en píxeles).
        """
        try:
            # 1. Apertura de boca (distancia vertical labios internos)
            # Landmark 13: Labio superior (interno)
            # Landmark 14: Labio inferior (interno)
            apertura_boca = self._distancia(13, 14, landmarks, alto, ancho)
            
            # 2. Apertura de ojos (promedio de distancias verticales)
            # Ojo derecho: 159 (arriba), 145 (abajo)
            apertura_ojo_der = self._distancia(159, 145, landmarks, alto, ancho)
            # Ojo izquierdo: 386 (arriba), 374 (abajo)
            apertura_ojo_izq = self._distancia(386, 374, landmarks, alto, ancho)
            avg_apertura_ojo = (apertura_ojo_der + apertura_ojo_izq) / 2.0
            
            # 3. Inclinación de cabeza (basado en la 'y' de las esquinas de los ojos)
            # p_der = 133 (esquina exterior ojo derecho)
            # p_izq = 362 (esquina exterior ojo izquierdo)
            p_der_y = landmarks.landmark[133].y
            p_izq_y = landmarks.landmark[362].y
            
            # Calculamos la diferencia vertical en píxeles
            inclinacion_px = (p_der_y - p_izq_y) * alto
            
            return {
                "apertura_boca_px": round(apertura_boca, 2),
                "apertura_ojos_px": round(avg_apertura_ojo, 2),
                "inclinacion_cabeza_px": round(inclinacion_px, 2)
            }
        except Exception as e:
            print(f"Error calculando expresiones: {e}")
            return {
                "apertura_boca_px": 0,
                "apertura_ojos_px": 0,
                "inclinacion_cabeza_px": 0
            }

    
    def detect(self, image, draw_style="Puntos"):
        """
        Detecta landmarks faciales en la imagen.
        
        Args:
            image (numpy.ndarray): Imagen en formato BGR (OpenCV)
            draw_style (str): "Puntos", "Malla" o "Contornos"
        
        Returns:
            tuple: (imagen_procesada, landmarks, info)
                - imagen_procesada: imagen con landmarks dibujados
                - landmarks: objeto de landmarks de MediaPipe
                - info: diccionario con información de detección
        """
        # Convertir BGR a RGB para MediaPipe
        imagen_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Procesar la imagen
        resultados = self.face_mesh.process(imagen_rgb)
        
        # Crear copia para dibujar
        imagen_con_puntos = image.copy()
        
        info = {
            "rostros_detectados": 0,
            "total_landmarks": 0,
            "deteccion_exitosa": False,
            "expresiones": {}
        }
        
        # Si se detectaron rostros
        if resultados.multi_face_landmarks:
            info["rostros_detectados"] = len(resultados.multi_face_landmarks)
            
            # Tomar el primer rostro
            rostro = resultados.multi_face_landmarks[0]
            info["total_landmarks"] = len(rostro.landmark)
            info["deteccion_exitosa"] = True
            
            alto, ancho = image.shape[:2]

            # --- LÓGICA DE DIBUJO (Opción A) ---
            
            if draw_style == "Malla":
                # Dibuja la malla de teselación
                self.mp_drawing.draw_landmarks(
                    image=imagen_con_puntos,
                    landmark_list=rostro,
                    connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None, # No dibuja los puntos
                    connection_drawing_spec=self.spec_malla
                )
            
            elif draw_style == "Contornos":
                # Dibuja solo los contornos principales
                # (FACEMESH_CONTOURS ya incluye ojos, cejas, labios y contorno facial)
                self.mp_drawing.draw_landmarks(
                    image=imagen_con_puntos,
                    landmark_list=rostro,
                    connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.spec_contornos
                )
                
                # --- AQUÍ ESTABA EL ERROR ---
                # Las líneas que intentaban dibujar FACEMESH_LIPS y FACEMESH_EYES
                # fueron eliminadas porque no existen y son redundantes.
            
            else: # "Puntos" (Comportamiento original)
                # Dibujar landmarks manualmente (como lo tenías)
                # O usar la función de dibujo de MediaPipe con nuestro spec:
                self.mp_drawing.draw_landmarks(
                    image=imagen_con_puntos,
                    landmark_list=rostro,
                    connections=set(), # No dibujar conexiones
                    landmark_drawing_spec=self.spec_puntos,
                    connection_drawing_spec=None
                )
            
            # --- CÁLCULO DE EXPRESIONES (Opción B) ---
            info["expresiones"] = self.analizar_expresiones(rostro, alto, ancho)
            
            return imagen_con_puntos, rostro, info
        
        # No se detectó rostro
        return imagen_con_puntos, None, info
    
    def close(self):
        """Libera recursos del detector."""
        self.face_mesh.close()
