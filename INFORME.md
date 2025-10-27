# Informe Técnico: Detector de Landmarks Faciales

**Proyecto:** Aplicación web para la detección de 478 landmarks faciales.
**Autor:** Orlando Vergara
**Tecnologías:** Python, Streamlit, MediaPipe, OpenCV

---

## 1. Introducción

### ¿Qué son los Landmarks Faciales?

Los landmarks (o puntos clave) faciales son un conjunto de puntos predefinidos que se localizan en los componentes de un rostro humano. En este proyecto, utilizamos la solución **MediaPipe Face Mesh**, que identifica **478 puntos clave** en 3D.

Estos puntos no son aleatorios; mapean con alta precisión la geometría de la cara, incluyendo:

* **Contorno facial:** La mandíbula, frente y mejillas.
* **Ojos:** El contorno de los ojos, párpados e iris.
* **Cejas:** La forma y posición de las cejas.
* **Nariz:** El puente, la punta y las fosas nasales.
* **Boca:** El contorno exterior e interior de los labios.

### Importancia y Aplicaciones

La capacidad de mapear un rostro en tiempo real es fundamental para la visión por computadora (Computer Vision). Su importancia radica en que "digitaliza" la expresión y estructura facial, permitiendo un análisis detallado para aplicaciones como:

* **Realidad Aumentada (AR):** Es la tecnología base de los filtros de Instagram o Snapchat, donde se superponen máscaras, maquillaje o efectos 3D sobre la cara del usuario.
* **Análisis de Expresiones:** Al rastrear el movimiento de los labios y ojos, se puede inferir el estado de ánimo (felicidad, sorpresa, enojo).
* **Accesibilidad:** Permite crear sistemas donde personas con discapacidades motoras pueden controlar un dispositivo usando movimientos faciales (ej. parpadear para hacer clic).
* **Animación y Avatares:** Se utiliza para transferir las expresiones de un actor a un personaje digital (como en los "Animojis").
* **Autenticación Biométrica:** Como un componente avanzado del reconocimiento facial.

---

## 2. Arquitectura del Proyecto

Para este proyecto, se adoptó una arquitectura limpia que separa la lógica de la aplicación (el "backend" de visión por computadora) de la interfaz de usuario (el "frontend" web).

La estructura de archivos principal es la siguiente:

facial-landmarks-app/ │ ├── app.py # Script principal de Streamlit (Interfaz de Usuario) ├── requirements.txt # Dependencias de Python (pip) ├── packages.txt # Dependencias del sistema (apt - para Streamlit Cloud) │ └── src/ # Paquete de código fuente (Lógica de la app) ├── init.py ├── detector.py # Clase FaceLandmarkDetector (usa MediaPipe) ├── utils.py # Funciones (conversión PIL<->CV2, redimensionar) └── config.py # Constantes (ej. TOTAL_LANDMARKS)

**Diagrama de Flujo de Datos:**

1.  **Usuario** sube una imagen a `app.py` (Streamlit).
2.  `app.py` convierte la imagen (PIL) a un formato `cv2` (numpy array) usando una función de `src/utils.py`.
3.  `app.py` instancia `FaceLandmarkDetector` de `src/detector.py`.
4.  `app.py` llama al método `.detect()` pasándole la imagen `cv2`.
5.  `detector.py` procesa la imagen con **MediaPipe**.
6.  `detector.py` dibuja los landmarks en la imagen usando **OpenCV**.
7.  `detector.py` devuelve la imagen procesada y la información (conteo de puntos).
8.  `app.py` muestra la imagen original y la imagen procesada al usuario.

---

## 3. Decisiones de Diseño

La estructura del código no fue casual. Se tomaron decisiones clave para asegurar que el proyecto sea mantenible, escalable y robusto.

* **Separación de Responsabilidades:** El pilar del diseño.
    * `app.py` solo se encarga de la **interfaz web**. No sabe *cómo* se detectan los puntos. Solo sabe pedirle a un "detector" que lo haga.
    * `src/detector.py` solo se encarga de la **visión por computadora**. No sabe nada de Streamlit, botones o sliders. Podría ser importado en un script de Jupyter Notebook o una app de escritorio sin cambiar una línea.

* **Modularidad (Código Reutilizable):**
    * Al crear una clase `FaceLandmarkDetector`, encapsulamos toda la lógica de MediaPipe. Si quisiéramos cambiar el color de los puntos o el grosor de la línea, solo modificamos el método `.draw_landmarks()` dentro de esa clase.
    * Las `src/utils.py` (como `pil_to_cv2`) son funciones genéricas que se pueden reutilizar en cualquier proyecto que combine PIL y OpenCV.

* **Gestión de Dependencias Explícita:**
    * `requirements.txt` lista solo las librerías de Python *directamente* necesarias (`streamlit`, `mediapipe`, `opencv-contrib-python`, `pillow`). Esto evita "inflar" el entorno y deja que `pip` resuelva las sub-dependencias.
    * `packages.txt` se creó para el despliegue en Streamlit Cloud, declarando explícitamente las librerías de sistema (Linux) que OpenCV necesita para funcionar (`libgl1-mesa-glx`, `ffmpeg`, etc.).

---

## 4. Desafíos y Soluciones

El desarrollo local fue fluido, pero el despliegue en **Streamlit Cloud** presentó la mayor parte de los desafíos. Fue una verdadera "batalla de configuración" contra un entorno de producción en Linux.

### Desafío 1: El Conflicto de OpenCV

* **Problema:** Mi `requirements.txt` original (generado con `pip freeze`) contenía `opencv-python` y `opencv-contrib-python` al mismo tiempo.
* **Error:** El despliegue fallaba con un error críptico (`non-zero exit code`).
* **Solución:** Aprendí que estos dos paquetes son mutuamente excluyentes. `opencv-contrib-python` ya incluye todo lo de `opencv-python`. La solución fue eliminar `opencv-python` y dejar solo la versión `contrib`.

### Desafío 2: El "Muro" de Streamlit Cloud (Dependencias de Sistema)

* **Problema:** Tras solucionar el Desafío 1, la instalación seguía fallando. El log de `pip` mostraba que `opencv` no se podía instalar.
* **Diagnóstico:** OpenCV no es solo Python; necesita librerías del sistema operativo (en el caso de Streamlit Cloud, Debian/Linux) para manejar video, gráficos y ventanas (como `libgl1`, `ffmpeg`, etc.).
* **Solución:** Crear un archivo `packages.txt` en la raíz del repositorio para indicarle a Streamlit (usando `apt-get`) qué paquetes de sistema debía instalar *antes* de intentar instalar los paquetes de Python.

### Desafío 3: El "Jefe Final" - Incompatibilidad de Versiones

* **Problema:** Con los `requirements.txt` y `packages.txt` correctos, ¡la app seguía fallando!
* **Diagnóstico:** Esta vez, el error en los logs era diferente: `ERROR: No matching distribution found for mediapipe`.
* **Investigación:** Analizando los logs, descubrí que Streamlit estaba intentando usar **Python 3.13** (la versión más nueva). Sin embargo, `mediapipe` (en ese momento) aún no tenía una versión compilada para Python 3.13.
* **Solución:** Forzar a Streamlit Cloud a usar una versión de Python compatible. Fui a `Manage App > Settings > Python version` y seleccioné **Python 3.11**. Al reiniciar la app, `pip` encontró `mediapipe` sin problemas y la aplicación se desplegó con éxito.

---

## 5. Uso del Agente AI (Kilo / Gemini)

Durante la fase de "Desafíos", el uso de un agente de IA fue fundamental para el *debugging*. Los mensajes de error de Streamlit Cloud pueden ser confusos, y la IA me ayudó a interpretarlos.

*(**Instrucción para vos:** Aquí es donde debés pegar tus capturas de pantalla. Mostrá cómo le pasaste los logs de error al chat y cómo te dio las soluciones.)*

**Ejemplo de Interacción 1: Diagnóstico del `requirements.txt`**

*Pega aquí tu captura donde te sugiere eliminar `opencv-python`.*

**Ejemplo de Interacción 2: Sugerencia de `packages.txt`**

*Pega aquí tu captura donde te explica por qué `opencv` falla en Linux y te da la lista para `packages.txt`.*

**Ejemplo de Interacción 3: Diagnóstico de Versión de Python**

*Pega aquí tu captura donde te explica el error `No matching distribution found for mediapipe` y te sugiere cambiar a Python 3.11.*

---

## 6. Conclusiones y Aprendizajes

Este proyecto fue un viaje completo desde la idea hasta la producción. Mis aprendizajes principales no fueron solo sobre código, sino sobre el ecosistema que lo rodea:

1.  **El Código Funciona" no es el Final:** Que un script funcione en mi máquina local (Windows/macOS) no significa nada para un servidor (Linux). El entorno es todo.
2.  **Leer Logs es una Habilidad:** El verdadero error no es el `non-zero exit code`. El error real está escondido 20 líneas más arriba en el log. Aprendí a buscar el *primer* `ERROR:` que aparece en la traza.
3.  **Las Dependencias son en Capas:** Aprendí que existen dependencias de Python (`pip`) y dependencias de Sistema Operativo (`apt`), y que las primeras a menudo dependen de las segundas.
4.  **Productividad:** Logré canalizar mi enfoque en un problema complejo (el despliegue) y resolverlo paso a paso. Superar los errores de configuración se sintió como resolver un "puzzle" o un "jefe de nivel", demostrando ser una aplicación muy productiva de mis habilidades de resolución de problemas.

---

## 7. Referencias

* **Streamlit:** [Documentación Oficial](https://streamlit.io/)
* **MediaPipe:** [Google | MediaPipe Face Mesh](https://developers.google.com/mediapipe/solutions/vision/face_landmarker)
* **OpenCV:** [OpenCV Library](https://opencv.org/)