# engine3_copernicus.py
import rasterio
import numpy as np
import os
from rasterio.warp import calculate_default_transform, reproject, Resampling
from config import DOWNLOADS_DIR

def download_dem_copernicus(lat, lon, width_m, height_m, output_path):
    """
    Copernicus DEM Motoru - Önce lokal dosya arar, yoksa uyarı verir
    
    Bu motor:
    1. Önce download/ klasöründe copernicus_dem.tif dosyası arar
    2. Bulursa, o dosyayı kullanır
    3. Bulamazsa, kullanıcıya manuel indirme talimatı verir
    
    Copernicus DEM indirmek için:
    https://panda.copernicus.eu/ (kayıt gerekir)
    """
    try:
        print(f"[Motor 3 - Copernicus DEM] Yerel DEM taranıyor...")
        
        # Aranacak dosya isimleri (kullanıcı hangi isimle kaydettiyseniz)
        possible_files = [
            os.path.join(DOWNLOADS_DIR, "copernicus_dem.tif"),
            os.path.join(DOWNLOADS_DIR, "copernicus.tif"),
            os.path.join(DOWNLOADS_DIR, "coper_dem.tif"),
            os.path.join(DOWNLOADS_DIR, "dem.tif"),
            "copernicus_dem.tif",  # Ana klasörde de ara
        ]
        
        dem_file = None
        for file_path in possible_files:
            if os.path.exists(file_path):
                dem_file = file_path
                print(f"  ✓ DEM dosyası bulundu: {dem_file}")
                break
        
        if dem_file is None:
            print(f"  ✗ Yerel DEM dosyası bulunamadı!")
            print(f"\n  📥 Copernicus DEM nasıl indirilir:")
            print(f"     1. https://panda.copernicus.eu/ adresine kaydolun")
            print(f"     2. 'Copernicus Global DEM' (30m) seçin")
            print(f"     3. Türkiye bölgesini seçin")
            print(f"     4. İndirdiğiniz .tif dosyasını downloads/ klasörüne koyun")
            print(f"     5. Dosya adını 'copernicus_dem.tif' olarak kaydedin")
            return False, None
        
        # Bulunan DEM dosyasını oku
        with rasterio.open(dem_file) as src:
            # Koordinat kontrolü (basit - dosyanın tamamını alıyoruz)
            dem = src.read(1).astype(np.float32)
            
            # İstenen alanı crop etme (ileri özellik, isteğe bağlı)
            # Şimdilik tüm DEM'i döndürüyoruz
            
            print(f"  ✓ Copernicus DEM başarıyla yüklendi!")
            print(f"  DEM Boyutu: {dem.shape}")
            print(f"  Çözünürlük: {src.res[0]:.2f} metre")
            print(f"  Veri tipi: {dem.dtype}")
            
            # Geçici olarak output_path'e kaydet (kopyala)
            with rasterio.open(
                output_path, 'w',
                driver='GTiff',
                height=dem.shape[0], width=dem.shape[1],
                count=1, dtype=dem.dtype,
                crs=src.crs,
                transform=src.transform
            ) as dst:
                dst.write(dem, 1)
            
            return True, dem
            
    except Exception as e:
        print(f"[Motor 3 - Copernicus DEM] ✗ Hata: {e}")
        return False, None

def check_copernicus_availability():
    """Sistemde Copernicus DEM var mı kontrol et"""
    possible_files = [
        os.path.join(DOWNLOADS_DIR, "copernicus_dem.tif"),
        "copernicus_dem.tif",
    ]
    
    for file_path in possible_files:
        if os.path.exists(file_path):
            print(f"✓ Copernicus DEM hazır: {file_path}")
            return True
    
    print("✗ Copernicus DEM bulunamadı")
    print("  İndirmek için: https://panda.copernicus.eu/")
    return False

# Test için
if __name__ == "__main__":
    # Bu dosyayı direkt çalıştırırsan Copernicus DEM kontrolü yapar
    check_copernicus_availability()