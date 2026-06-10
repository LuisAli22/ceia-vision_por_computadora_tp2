# TP2 - Detector de Máximo Enfoque en Video
## Visión por Computadora I - CEIA

### 🧑‍🎓 Alumnos
- **Santiago Ignacio Bartolini Rizzo** → C2402
- **Luis Ali** → C2401

---

## 📋 Descripción

Implementación de un detector automático de máximo enfoque en video mediante análisis en el dominio de la frecuencia y el espacio. Se compararon dos métricas principales (image quality measure (FM) y Laplacian Variance) aplicadas sobre diferentes estrategias de análisis (frame completo, ROI central, y matrices de enfoque).

---

## 📂 Archivos del Proyecto

```
TP2/
├── 📓 TP2.ipynb          # Notebook principal con todos los experimentos
├── 🐍 focus_metrics.py            # Módulo con métricas de enfoque implementadas
├── 🎥 focus_video.mov             # Video a procesar (171 frames, 640×360)
└── 📚 README.md                   # Este archivo
```

**✅ Archivos esenciales para ejecutar el TP:**
- `TP2.ipynb` - Notebook completo con código, resultados y conclusiones
- `focus_metrics.py` - Funciones de métricas de enfoque
- `focus_video.mov` - Video de entrada
- `README.md` - Este archivo con instrucciones

---

## 🎯 Experimentos Implementados

### **PARTE 1: Métrica Image quality measure (FM)**

1. **Experimento 1** - Frame Completo  
   Análisis de enfoque sobre la imagen completa (640×360 pixels)

2. **Experimento 2** - ROI Central 5%  
   Análisis sobre región de interés central (107×107 pixels)

3. **Experimento 3** - Matrices de Enfoque N×M  
   Análisis con grids de diferentes tamaños: 3×3, 7×5, 6×8, 20×20  
   Incluye visualización con mapa de calor superpuesto

### **PARTE 2: Métrica Laplacian Variance**

4. **Experimento 4.1** - Frame Completo  
5. **Experimento 4.2** - ROI Central 5%  
6. **Experimento 4.3** - Matrices de Enfoque N×M  
   Incluye visualización con mapa de calor superpuesto

### **BONUS**

7. **Experimento 5** - Unsharp Masking  
   Aplicación de técnica de realce de bordes con diferentes intensidades

---

## 🚀 Instalación y Ejecución

### Requisitos

- Python 3.11 o 3.12
- Poetry (recomendado) o pip
- Jupyter Notebook

### Opción 1: Poetry (Recomendada)

```bash
# 1. Instalar dependencias
poetry install

# 2. Registrar kernel de Jupyter
poetry run python -m ipykernel install --user --name=tp2-vision --display-name="Python (Vision TP2 - Poetry)"

# 3. Iniciar Jupyter
poetry run jupyter notebook TP2.ipynb

# 4. Seleccionar el kernel "Python (Vision TP2 - Poetry)" en el notebook
```

### Opción 2: pip con requirements.txt

Si tienes un `requirements.txt`:

```bash
# 1. Crear entorno virtual (opcional pero recomendado)
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar Jupyter
jupyter notebook TP2.ipynb
```

### Dependencias Principales

```
opencv-python >= 4.5.0
numpy >= 1.21.0
matplotlib >= 3.7.0
scipy >= 1.6.1
jupyter >= 1.1.1
ipykernel >= 6.0.0
```

---

## 📊 Resultados Principales

### Hallazgo Principal

**Frame 111** fue detectado consistentemente como el frame de máximo enfoque por:
- ✅ Image quality measure (FM) sobre ROI 5%
- ✅ Laplacian Variance sobre frame completo
- ✅ Laplacian Variance sobre ROI 5%
- ✅ Laplacian Variance sobre TODOS los grids (3×3, 7×5, 6×8, 20×20)

### Comparación de Métricas

| Aspecto | FM (Frequency Domain) | Laplacian Variance |
|---------|----------------------|-------------------|
| **Complejidad** | O(n² log n) | **O(n²)** ✅ |
| **Consistencia** | Variable según tamaño de matriz de enfoque | **Altísima** ✅ |
| **Velocidad** | aproximadamente 3 veces más lento | **Muy rápido** ✅ |
| **Frames detectados (grids)** | 78, 99, 105, 111 | **111 (todos)** ✅ |

### Visualizaciones

El notebook incluye:
- 📈 Gráficas de evolución temporal del enfoque
- 🗺️ Mapas de calor de enfoque superpuestos sobre frames
- 📊 Comparaciones visuales entre estrategias
- 🎨 Colormap `plasma_r` invertido para interpretación intuitiva
---

## 📖 Uso del Notebook

1. **Abrir el notebook**: `TP2.ipynb`

2. **Ejecutar celdas secuencialmente**:
   - Importación de bibliotecas
   - Carga del video
   - PARTE 1: Experimentos con image quality measure (FM)
   - PARTE 2: Experimentos con Laplacian
   - Visualizaciones con matrices superpuestas
   - Experimento Bonus (Unsharp Masking)
   - Conclusiones finales

3. **Visualizar resultados**:
   - Las gráficas se generan inline en el notebook
   - Los mapas de calor muestran distribución espacial del enfoque
   - Las conclusiones resumen todos los hallazgos
---

## 🔬 Módulo `focus_metrics.py`

Contiene las funciones implementadas:

### Métricas de Enfoque
```python
image_quality_measure_fm(image)           # FM (Frequency Domain)
laplacian_variance(image)                  # Laplacian Variance
```

### Funciones Auxiliares
```python
extract_roi_center(image, percentage)      # Extrae ROI central
create_focus_grid(image, grid_size, metric)# Crea matriz de enfoque
detect_focus_peaks(focus_values)           # Detecta picos
apply_unsharp_mask(image, amount)          # Unsharp masking
visualize_focus_grid_overlay(frame, grid_size, metric, colormap)  # Visualización
```

---

## 📚 Referencias

### Papers Implementados

1. **"Image Sharpness Measure for Blurred Images in Frequency Domain"**
   - Métrica image auqlity measure (FM) basada en FFT
   - Análisis de contenido de alta frecuencia

2. **"Analysis of Focus Measure Operators for Shape-from-Focus"** (Pertuz et al., 2013)
   - Laplacian Variance (LAP4)
   - Comparación de operadores de enfoque
---

## 🐛 Solución de Problemas

### El kernel no aparece en Jupyter

```bash
# Poetry:
poetry run python -m ipykernel install --user --name=tp2-vision --display-name="Python (Vision TP2 - Poetry)"

# Verificar:
jupyter kernelspec list
```

### Error: ModuleNotFoundError

```bash
# Asegurarse de que el entorno está activado y las dependencias instaladas
poetry install  # o pip install -r requirements.txt
```

### El video no se encuentra

Asegúrate de que `focus_video.mov` está en el mismo directorio que el notebook.

---

## 📧 Contacto

**Materia:** Visión por Computadora I  
**Programa:** CEIA (Carrera de Especialización en Inteligencia Artificial)  
**Institución:** FIUBA (Facultad de Ingeniería - Universidad de Buenos Aires)

---

## 🎓 Conclusión

Este trabajo demostró que:
- **Laplacian Variance es superior** para aplicaciones de tiempo real por su velocidad y consistencia
- **El ROI central** mejora significativamente la sensibilidad (hasta 16× en FM)
- **El Frame 111** es objetivamente el frame más enfocado del video
- Las **visualizaciones con mapas de calor** permiten entender la distribución espacial del enfoque

Para detalles completos, ver las **Conclusiones Finales** en el notebook.
---
