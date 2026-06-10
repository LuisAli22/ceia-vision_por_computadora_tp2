"""
Módulo de métricas de enfoque para detección de máximo enfoque en video.

Este módulo implementa diferentes métricas de enfoque para analizar
imágenes y videos, incluyendo:
- Image Quality Measure (FM)
- Laplacian Variance
- Procesamiento por ROI (Region of Interest)
- Procesamiento por grids (matrices N×M)
- Unsharp masking para realce de detalles
- Visualización de matrices de enfoque
"""

import numpy as np
from matplotlib import cm
import cv2  # pylint: disable=no-member
from scipy.fft import fft2, fftshift
from scipy.signal import find_peaks


def get_centered_fourier_transform_magnitude(image):
    """
    Calcula AF (magnitud del espectro de Fourier centrado).
    
    Args:
        image: Imagen en escala de grises (numpy array)

    Returns:
        AF: Absolute value (magnitude) of centered Fourier transform
            AF = |Fc| donde Fc es la FFT centrada
            
    Implementación:
        1. F = fft2(I)        - Transformada de Fourier 2D
        2. Fc = fftshift(F)   - Centrar frecuencias (DC en el centro)
        3. AF = |Fc|          - Magnitud del espectro
    """
    image_as_float = image.astype(np.float64)
    fourier_transform = fft2(image_as_float)
    centered_fourier_transform = fftshift(fourier_transform)
    return  np.abs(centered_fourier_transform)


def image_quality_measure_fm(image):
    """
    Calcula FM (Image Quality Measure) en dominio frecuencial.
    Paper: "Image Sharpness Measure for Blurred Images in Frequency Domain"
    
    Implementa el algoritmo exacto del paper:
        1. F = fft2(I)                    - Transformada de Fourier
        2. Fc = fftshift(F)               - Centrar el espectro
        3. AF = abs(Fc)                   - Magnitud del espectro
        4. M = max(AF)                    - Valor máximo de frecuencia
        5. TH = count(AF > M/1000)        - Pixels sobre threshold
        6. FM = TH / (M × N)              - Image Quality Measure
    
    Args:
        image: Imagen en escala de grises (numpy array, tamaño M×N)

    Returns:
        FM: Image Quality Measure FM (Frequency Domain Image Blur Measure)
            Mayor FM → imagen más nítida (sharp) → mejor enfocada
            Menor FM → imagen más borrosa (blurred) → desenfocada
    """
    magnitude_spectrum = get_centered_fourier_transform_magnitude(image)
    maximum_frequency_value = np.max(magnitude_spectrum)
    threshold_value = maximum_frequency_value / 1000.0
    total_pixels_above_threshold = np.sum(magnitude_spectrum > threshold_value)
    image_height_rows, image_width_columns = image.shape
    total_pixels_in_image = image_height_rows * image_width_columns
    return total_pixels_above_threshold / total_pixels_in_image




def laplacian_variance(image):
    """
    Métrica de varianza del Laplaciano.
    A mayor varianza, mayor enfoque.
    Args:
        image: Imagen en escala de grises
    Returns:
        laplacian_variance_value: Varianza del Laplaciano
    """
    laplacian_filtered_image = cv2.Laplacian(image, cv2.CV_64F)
    laplacian_variance_value = laplacian_filtered_image.var()
    return laplacian_variance_value




def calculate_roi_side_length(image, roi_percentage):
    """
    Calcula el lado del cuadrado ROI basado en el porcentaje del área total.
    
    Args:
        image: Imagen completa (grayscale o color)
        roi_percentage: Porcentaje del área (0.05 = 5%, 0.10 = 10%)
    
    Returns:
        roi_side_length: Longitud del lado del cuadrado ROI (en pixels)
    """
    image_rows, image_columns = image.shape[:2]
    total_image_area = image_rows * image_columns
    roi_area = total_image_area * roi_percentage
    roi_side_length = int(np.sqrt(roi_area))
    return roi_side_length


def calculate_centered_roi_bounds(image, roi_side_length):
    """
    Calcula los límites de una ROI cuadrada centrada en la imagen.
    Args:
        image: Imagen completa (grayscale o color)
        roi_side_length: Longitud del lado del cuadrado ROI
    
    Returns:
        Tupla (start_row, end_row, start_col, end_col) con los límites de la ROI
    """
    image_rows, image_columns = image.shape[:2]
    # Encontrar el centro de la imagen
    center_row = image_rows // 2
    center_column = image_columns // 2
    # Calcular mitad del lado ROI
    half_side = roi_side_length // 2
    # Calcular límites con protección de bordes
    roi_start_row = max(0, center_row - half_side)
    roi_end_row = min(image_rows, center_row + half_side)
    roi_start_column = max(0, center_column - half_side)
    roi_end_column = min(image_columns, center_column + half_side)
    return roi_start_row, roi_end_row, roi_start_column, roi_end_column


def extract_roi_center(image, roi_percentage=0.05):
    """
    Extrae una región de interés (ROI) cuadrada del centro de la imagen.
    Args:
        image: Imagen completa (grayscale o color)
        roi_percentage: Porcentaje del área total (0.05 = 5%, 0.10 = 10%)
    
    Returns:
        region_of_interest: Región cuadrada extraída del centro de la imagen
    """
    roi_side_length = calculate_roi_side_length(
        image,
        roi_percentage
    )
    roi_start_row, roi_end_row, roi_start_column, roi_end_column = (
        calculate_centered_roi_bounds(
            image,
            roi_side_length
        )
    )
    region_of_interest = image[
        roi_start_row:roi_end_row,
        roi_start_column:roi_end_column
    ]
    return region_of_interest

def get_cell_bounds(component_index, cell_dimension, 
                           number_of_grid_components, image_dimension):
    """
    Calcula el inicio y fin de una celda del grid en una dimensión.
    
    Args:
        component_index: Índice de la celda (fila o columna)
        cell_dimension: Tamaño de cada celda (alto o ancho)
        number_of_grid_components: Total de celdas en esa dimensión
        image_dimension: Tamaño total de la imagen en esa dimensión
    
    Returns:
        Tupla (cell_start, cell_end) con inicio y fin de la celda
    """
    cell_start = component_index * cell_dimension
    if component_index < number_of_grid_components - 1:
        cell_end = (component_index + 1) * cell_dimension
    else:
        cell_end = image_dimension
    return (cell_start, cell_end)

def create_focus_grid(image, grid_size=(7, 7),
                     focus_metric=image_quality_measure_fm):
    """
    Crea una matriz de enfoque dividiendo la imagen en una cuadrícula N×M.
    
    Divide la imagen en celdas rectangulares equiespaciadas y calcula
    el enfoque de cada celda usando la métrica especificada.
    
    Args:
        image: Imagen en escala de grises (numpy array)
        grid_size: Tupla (N, M) con el tamaño de la cuadrícula
                   N = número de filas, M = número de columnas
        focus_metric: Función de métrica de enfoque
                      Por defecto se usa image_quality_measure_fm
    Returns:
        focus_grid_matrix: Matriz N×M con valores de enfoque para cada celda
    """
    img_h, img_w = image.shape
    grid_rows, grid_cols = grid_size
    focus_grid = np.zeros(grid_size)
    for row_idx in range(grid_rows):
        for col_idx in range(grid_cols):
            r_start, r_end = get_cell_bounds(
                row_idx, img_h // grid_rows, grid_rows, img_h
            )
            c_start, c_end = get_cell_bounds(
                col_idx, img_w // grid_cols, grid_cols, img_w
            )
            focus_grid[row_idx, col_idx] = focus_metric(
                image[r_start:r_end, c_start:c_end]
            )
    return focus_grid

def apply_unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.5):
    """
    Aplica unsharp masking para realzar detalles.
    
    Implementa la ecuación:
        g_sharp = f + γ(f - h_blur * f)
    
    Donde:
        - f: imagen original
        - h_blur * f: imagen desenfocada (Gaussian blur)
        - γ: amount (intensidad del realce)
        - g_sharp: imagen realzada

    Args:
        image: Imagen de entrada (escala de grises)
        kernel_size: Tamaño del kernel gaussiano (debe ser impar)
        sigma: Desviación estándar del filtro gaussiano
        amount: Intensidad del realce (γ).
    Returns:
        sharpened_image: Imagen con unsharp masking aplicado
    """
    blurred_image = cv2.GaussianBlur(image, kernel_size, sigma)
    unsharp_mask = image.astype(np.float64) - blurred_image.astype(np.float64)
    sharpened_image = image.astype(np.float64) + amount * unsharp_mask
    return  np.clip(sharpened_image, 0, 255).astype(np.uint8)

def visualize_focus_grid_overlay(frame, grid_size, focus_metric,  # pylint: disable=too-many-locals
                                      colormap='hot',alpha=0.5):
    """
    Dibuja la matriz de enfoque superpuesta sobre un frame del video.
    
    Args:
        frame: Frame del video (BGR o escala de grises)
        grid_size: Tupla (filas, columnas) del grid
        focus_metric: Función de métrica de enfoque a usar
        colormap: Mapa de colores de matplotlib ('viridis', 'hot', 'jet')
        alpha: Transparencia de la superposición (0.0-1.0)
        show_grid_lines: Si True, dibuja las líneas del grid en verde
    
    Returns:
        frame_with_overlay: Frame con la matriz de enfoque superpuesta
    """
    # Convertir a escala de grises para calcular enfoque
    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_color = frame.copy()
    else:
        gray = frame
        frame_color = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    
    # Calcular la matriz de enfoque
    focus_matrix = create_focus_grid(gray, grid_size, focus_metric)
    
    # Normalizar valores de enfoque al rango [0, 1]
    focus_min = np.min(focus_matrix)
    focus_max = np.max(focus_matrix)
    focus_normalized = (focus_matrix - focus_min) / (focus_max - focus_min + 1e-10)
    
    # Crear mapa de calor con el colormap elegido
    cmap = cm.get_cmap(colormap)
    heatmap = cmap(focus_normalized)[:, :, :3]  # RGB sin canal alpha
    heatmap = (heatmap * 255).astype(np.uint8)
    
    # Redimensionar el heatmap al tamaño del frame
    frame_height, frame_width = frame_color.shape[:2]
    heatmap_resized = cv2.resize(heatmap, (frame_width, frame_height), 
                                 interpolation=cv2.INTER_NEAREST)
    
    # Superponer el heatmap sobre el frame con transparencia
    frame_with_overlay = cv2.addWeighted(frame_color, 1 - alpha, 
                                        heatmap_resized, alpha, 0)
    
    # Dibujar líneas del grid si se solicita
    grid_rows, grid_cols = grid_size
    cell_height = frame_height // grid_rows
    cell_width = frame_width // grid_cols
    
    # Líneas horizontales
    for i in range(1, grid_rows):
        y = i * cell_height
        cv2.line(frame_with_overlay, (0, y), (frame_width, y), 
                (0, 255, 0), 2)
    
    # Líneas verticales
    for j in range(1, grid_cols):
        x = j * cell_width
        cv2.line(frame_with_overlay, (x, 0), (x, frame_height), 
                (0, 255, 0), 2)
    
    return frame_with_overlay, focus_matrix


def detect_focus_peaks(focus_curve, prominence=None, distance=None):
    """
    Detecta picos (máximos) en la curva de enfoque.

    Args:
        focus_curve: Array con valores de la métrica de enfoque
        prominence: Prominencia mínima del pico
        distance: Distancia mínima entre picos (en frames)

    Returns:
        peak_frame_indices: Índices de los frames con máximo enfoque
        peak_properties: Propiedades de los picos detectados
    """
    # Si no se especifica prominencia, usar un porcentaje del rango
    if prominence is None:
        focus_curve_range = np.max(focus_curve) - np.min(focus_curve)
        prominence = focus_curve_range * 0.1

    peak_frame_indices, peak_properties = find_peaks(
        focus_curve,
        prominence=prominence,
        distance=distance
    )

    return peak_frame_indices, peak_properties
