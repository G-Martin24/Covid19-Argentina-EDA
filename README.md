🦠 COVID-19 en Argentina – Análisis Exploratorio y Estadístico (EDA)

Este proyecto realiza un análisis exploratorio y estadístico del COVID-19 en Argentina, utilizando datos públicos de casos confirmados.
Incluye:

Limpieza y preparación de datos

Estadísticas descriptivas

Visualizaciones clave

Análisis temporal y por regiones

Interpretación de resultados

Código organizado y reproducible

📁 Estructura del repositorio
Covid19-Argentina-EDA/
├── Covid19Casos/
│   └── ejercicios.py         # Código de análisis
├── censo2022.csv             # Datos adicionales para cruces
├── README.md                 # Documento principal
└── .gitignore


⚠️ El dataset principal (Covid19Casos.csv) no se incluye en el repositorio porque pesa más de 100 MB y GitHub no permite subirlo.

📥 Descarga del Dataset

Para ejecutar el análisis necesitás descargar el dataset original:

👉 📌 Descargar dataset COVID-19 (Google Drive)

Luego colocarlo en la siguiente ubicación dentro del repositorio:

Covid19Casos/Covid19Casos.csv


El proyecto lo detectará automáticamente.

🧪 Cómo ejecutar el análisis
1. Clonar el repositorio
git clone https://github.com/G-Martin24/Covid19-Argentina-EDA.git
cd Covid19-Argentina-EDA

2. Colocar el archivo CSV descargado en:
Covid19Casos/Covid19Casos.csv

3. Opcional: Crear un entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

4. Instalar dependencias (si las hubiera)
pip install -r requirements.txt


(Si querés puedo generarte también un requirements.txt.)

5. Ejecutar el script
python Covid19Casos/ejercicios.py


o abrirlo en Jupyter Notebook.

📊 Resultados principales

El análisis incluye:

Tendencias de casos confirmados a lo largo del tiempo

Comparación entre regiones del país

Detección de picos de contagios

Distribuciones estadísticas

Correlaciones entre variables

Gráficos descriptivos para facilitar la interpretación

🧠 Objetivo del proyecto

Este trabajo se realizó como parte de un trabajo práctico de Estadística, aplicando técnicas de:

Estadística descriptiva

Manipulación de datos (pandas)

Visualización (matplotlib / seaborn)

Análisis exploratorio

Limpieza y preparación de datasets reales

El propósito es desarrollar habilidades prácticas en análisis de datos reales, utilizando Python.

📌 Créditos y fuentes de datos

Los datos provienen de fuentes oficiales del gobierno argentino:

👉 https://datos.gob.ar/

📬 Contacto

Autor: Martín Galbán
GitHub: https://github.com/G-Martin24
