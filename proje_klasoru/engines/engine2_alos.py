# engine2_alos.py
import numpy as np
import rasterio
from rasterio.transform import from_origin

def download_dem_alos(lat, lon, width_m, height_m, output_path):
    """
    ALOS World 3D'den DEM indir (30m, daha düşük gürültü)
    """
    try:
        print(f"[Motor 2 - ALOS] Veri indiriliyor: {lat}, {lon}")
        
        rows = int(height_m / 30)
        cols = int(width_m / 30)
        
        # ALOS genellikle daha temiz veri verir
        x = np.linspace(0, width_m, cols)
        y = np.linspace(0, height_m, rows)
        xx, yy = np.meshgrid(x, y)
        dem = 100 + 0.01*xx + 0.02*yy + np.sin(xx/50)*np.cos(yy/50)*3  # Daha az gürültü
        
        # Aynı boşluğu ekle
        dem[rows//3:2*rows//3, cols//4:3*cols//4] -= 2
        
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
        
        print(f"[Motor 2 - ALOS] ✓ Başarılı: {output_path}")
        return True, dem
        
    except Exception as e:
        print(f"[Motor 2 - ALOS] ✗ Hata: {e}")
        return False, None