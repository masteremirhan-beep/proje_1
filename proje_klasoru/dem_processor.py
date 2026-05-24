# dem_processor.py
import numpy as np
from scipy.ndimage import gaussian_filter, median_filter
import matplotlib.pyplot as plt
from datetime import datetime
import os

def calculate_trend_surface(dem, sigma=15):
    """Doğal topoğrafya trend yüzeyi"""
    return gaussian_filter(dem, sigma=sigma)

def calculate_residual(dem, trend):
    """Anomali haritası = DEM - Trend"""
    return dem - trend

def apply_filters(residual, median_size=3):
    """Gürültü azaltma"""
    return median_filter(residual, size=median_size)

def plot_and_save(residual, output_path):
    """Anomali haritasını kaydet"""
    plt.figure(figsize=(10, 8))
    im = plt.imshow(residual, cmap='RdBu', interpolation='bilinear')
    plt.colorbar(im, label="Anomali (m)")
    plt.title("Yeraltı Boşluk Anomalisi (Mavi=Çöküntü)")
    plt.savefig(output_path, dpi=150)
    plt.close()
    
def log_error(engine_name, error_msg):
    """Hataları log dosyasına yaz"""
    with open(os.path.join(os.path.dirname(__file__), "logs", "hata_logu.txt"), "a") as f:
        f.write(f"{datetime.now()} - {engine_name}: {error_msg}\n")