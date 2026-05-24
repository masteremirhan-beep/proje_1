# engine1_srtm.py
import urllib.request
import rasterio
import numpy as np
from rasterio.transform import from_origin
import os

def download_dem_srtm(lat, lon, width_m, height_m, output_path):
    """
    SRTM'den DEM indir (30m çözünürlük)
    Not: Bu basit bir simülasyondur. Gerçek SRTM indirme için 
    OpenTopography veya NASA Earthdata API gerekir.
    """
    try:
        print(f"[Motor 1 - SRTM] Veri indiriliyor: {lat}, {lon}")
        
        # Burada gerçek DEM indirme kodu olacak
        # Şimdilik test için sentetik veri üretiyoruz
        rows = int(height_m / 30)  # 30m çözünürlük
        cols = int(width_m / 30)
        
        # Gerçekçi test verisi (normal dağılımlı arazi)
        x = np.linspace(0, width_m, cols)
        y = np.linspace(0, height_m, rows)
        xx, yy = np.meshgrid(x, y)
        dem = 100 + 0.01*xx + 0.02*yy + np.sin(xx/50)*np.cos(yy/50)*5
        
        # Yapay boşluk ekle (test için)
        dem[rows//3:2*rows//3, cols//4:3*cols//4] -= 2
        
        # GeoTIFF olarak kaydet
        transform = from_origin(lon, lat, 30, 30)
        with rasterio.open(
            output_path, 'w',
            driver='GTiff',
            height=rows, width=cols,
            count=1, dtype='float32',
            crs='EPSG:4326',
            transform=transform
        ) as dst:
            dst.write(dem.astype(np.float32), 1)
        
        print(f"[Motor 1 - SRTM] ✓ Başarılı: {output_path}")
        return True, dem
        
    except Exception as e:
        print(f"[Motor 1 - SRTM] ✗ Hata: {e}")
        return False, None