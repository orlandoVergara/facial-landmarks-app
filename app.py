# app.py
"""
Aplicación web para detección de landmarks faciales.
"""
import streamlit as st

# Manejo de importaciones con try-except para mejor gestión de errores
try:
    from PIL import Image
    from src.detector import FaceLandmarkDetector
    from src.utils import pil_to_cv2, cv2_to_pil, resize_image
    from src.config import TOTAL_LANDMARKS
    
    SETUP_SUCCESSFUL = True
except ImportError as e:
    st.error(f"""
    ⚠️ Error al cargar las dependencias: {str(e)}
    
    Este error puede ocurrir si algunas dependencias no se instalaron correctamente.
    Por favor, revisa los logs de la aplicación para más detalles.
    """)
    SETUP_SUCCESSFUL = False


# Configuración de la página
st.set_page_config(
    page_title="Detector de Landmarks Faciales",
    layout="wide"
)

# Título y descripción
if not SETUP_SUCCESSFUL:
    st.error("""
    🚨 La aplicación no pudo inicializarse correctamente.
    
    Razones comunes:
    1. Problemas con la instalación de OpenCV o MediaPipe
    2. Conflictos de dependencias
    3. Falta de librerías del sistema
    
    Por favor, contacta al administrador del sistema.
    """)
    st.stop()

st.title("Detector de Landmarks Faciales")
st.markdown("""
Esta aplicación detecta **478 puntos clave** en rostros humanos usando MediaPipe.
Subí una imagen con un rostro y mirá la magia de la visión por computadora.
""")

# Sidebar con información
with st.sidebar:
    st.header("Información")
    st.markdown("""
    ### ¿Qué son los Landmarks?
    Son puntos de referencia que mapean:
    - Ojos (iris, párpados)
    - Nariz (puente, fosas)
    - Boca (labios, comisuras)
    - Contorno facial
    
    ### Aplicaciones
    - Filtros AR (Instagram)
    - Análisis de expresiones
    - Animación facial
    - Autenticación biométrica
    """)
    
    st.divider()
    
    # --- 1. OPCIÓN A: Selector de Estilo de Visualización ---
    # Usamos un diccionario para mapear el texto amigable (lo que ve el usuario)
    # al valor que espera nuestro backend (lo que usa detector.py)
    MAPEO_ESTILOS = {
        "Solo Puntos": "Puntos",
        "Malla Completa": "Malla",
        "Contornos Principales": "Contornos"
    }
    
    # Usamos st.radio para que las opciones sean visibles
    estilo_usuario = st.radio(
        "Estilo de visualización",
        list(MAPEO_ESTILOS.keys()), # Opciones amigables
        index=0
    )
    
    # Obtenemos el valor real para el backend
    estilo_backend = MAPEO_ESTILOS[estilo_usuario]
    
    st.divider()
    st.caption("Desarrollado en el Laboratorio 2 - IFTS24")


# Uploader de imagen
uploaded_file = st.file_uploader(
    "Subí una imagen con un rostro",
    type=["jpg", "jpeg", "png"],
    help="Formatos aceptados: JPG, JPEG, PNG"
)

if uploaded_file is not None:
    # Cargar imagen
    imagen_original = Image.open(uploaded_file)
    
    # Convertir a formato OpenCV
    imagen_cv2 = pil_to_cv2(imagen_original)
    
    # Redimensionar si es muy grande
    imagen_cv2 = resize_image(imagen_cv2, max_width=800)
    
    # Columnas para mostrar antes/después
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Imagen Original")
        st.image(cv2_to_pil(imagen_cv2), use_container_width=True)
    
    # Detectar landmarks
    with st.spinner("Detectando landmarks faciales..."):
        detector = FaceLandmarkDetector()
        
        # --- 2. OPCIÓN A: Pasar el estilo de dibujo al detector ---
        # Nota: el parámetro ahora es 'draw_style'
        imagen_procesada, landmarks, info = detector.detect(
            imagen_cv2, 
            draw_style=estilo_backend 
        )
        detector.close()
    
    with col2:
        st.subheader(f"Landmarks Detectados ({estilo_usuario})") # Título dinámico
        st.image(cv2_to_pil(imagen_procesada), use_container_width=True)
    
    # Mostrar información de detección
    st.divider()
    
    if info["deteccion_exitosa"]:
        st.success("Detección exitosa")
        
        # --- Métricas de Detección (Originales) ---
        st.subheader("Métricas de Detección")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric("Rostros detectados", info["rostros_detectados"])
        
        with metric_col2:
            st.metric("Landmarks detectados", f"{info['total_landmarks']}/{TOTAL_LANDMARKS}")
        
        with metric_col3:
            porcentaje = (info['total_landmarks'] / TOTAL_LANDMARKS) * 100
            st.metric("Precisión", f"{porcentaje:.1f}%")

        # --- 3. OPCIÓN B: Mostrar Análisis de Expresiones ---
        st.subheader("Análisis de Expresiones (Estimado en Píxeles)")
        
        # Extraer el diccionario de expresiones que creamos en detector.py
        metricas_exp = info["expresiones"]
        
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        
        with exp_col1:
            st.metric(
                "Apertura de Boca", 
                f"{metricas_exp['apertura_boca_px']} px"
            )
        
        with exp_col2:
            st.metric(
                "Apertura de Ojos (Avg)", 
                f"{metricas_exp['apertura_ojos_px']} px"
            )
        
        with exp_col3:
            # Añadimos lógica simple para interpretar la inclinación
            inclinacion_px = metricas_exp['inclinacion_cabeza_px']
            umbral = 2.0 # Umbral de píxeles para considerarlo centrado
            
            if inclinacion_px > umbral:
                direccion = "Izquierda ↙️"
            elif inclinacion_px < -umbral:
                direccion = "Derecha ↘️"
            else:
                direccion = "Centrada ⬇️"
                
            st.metric(
                "Inclinación Cabeza",
                f"{abs(inclinacion_px)} px ({direccion})"
            )

    else:
        st.error("No se detectó ningún rostro en la imagen")
        st.info("""
        **Consejos**:
        - Asegurate de que el rostro esté bien iluminado
        - El rostro debe estar mirando hacia la cámara
        - Probá con una imagen de mayor calidad
        """)

else:
    # Mensaje de bienvenida
    st.info("Subí una imagen para comenzar la detección")
    
    # Ejemplo visual
    st.markdown("### Ejemplo de Resultado")
    st.image(
        "https://ai.google.dev/static/mediapilabs/face_mesh_contours.png?hl=es-419",
        caption="Ejemplo de los diferentes modos de visualización.",
        use_container_width=True,
        width=400
    )
