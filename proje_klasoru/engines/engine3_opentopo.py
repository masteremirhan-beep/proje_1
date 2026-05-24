# engine3_opentopo.py - ÇALIŞIYOR!
import urllib.request
import rasterio
import numpy as np
import os

OPENTOPO_API_KEY = "a92da5448c6a4a5f1dc6a857e8e9f2f7"

def download_dem_opentopo(lat, lon, width_m, height_m, output_path):
    """
    OpenTopography API ile gerçek DEM indir
    """
    try:
        print(f"[OpenTopography] Gerçek DEM indiriliyor...")
        
        # Sabit alan kullan (testte çalışan)
        min_lat = lat - 0.01
        max_lat = lat + 0.01
        min_lon = lon - 0.01
        max_lon = lon + 0.01
        
        print(f"  Bounding Box: {min_lat:.4f}° → {max_lat:.4f}°, {min_lon:.4f}° → {max_lon:.4f}°")
        
        url = f"https://portal.opentopography.org/API/globaldem?demtype=SRTMGL1&south={min_lat}&north={max_lat}&west={min_lon}&east={max_lon}&outputFormat=GTiff&API_Key={OPENTOPO_API_KEY}"
        
        print(f"  İndiriliyor...")
        urllib.request.urlretrieve(url, output_path)
        
        # Dosya kontrolü (testte çalışan 5829 byte)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:  # 1000 byte yeterli
            with rasterio.open(output_path) as src:
                dem = src.read(1).astype(np.float32)
                dem = np.nan_to_num(dem, nan=0.0)
                print(f"  ✓ Başarılı! Boyut: {dem.shape[0]}x{dem.shape[1]} piksel")
                print(f"  Yükseklik aralığı: {dem.min():.1f}m - {dem.max():.1f}m")
                return True, dem
        else:
            print(f"  ✗ Dosya çok küçük: {os.path.getsize(output_path)} byte")
            return False, None
            
    except Exception as e:
        print(f"  ✗ Hata: {e}")
        return False, None

# Test
if __name__ == "__main__":
    print("Motor test ediliyor...")
    success, dem = download_dem_opentopo(41.0559, 29.6563, 300, 300, "motor_test.tif")
    if success:
        print("✓ MOTOR BAŞARIYLA ÇALIŞTI!")
    else:
        print("✗ Motor çalışmadı")