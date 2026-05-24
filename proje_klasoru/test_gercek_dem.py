# test_gercek_dem.py - OpenTopography'yi bağımsız test et
import urllib.request
import rasterio
import numpy as np
import os

API_KEY = "a92da5448c6a4a5f1dc6a857e8e9f2f7"  # test_api.py'de çalışan key

lat = 41.05592165753617
lon = 29.656312834259097

# Daha büyük alan dene (0.02 derece ≈ 2.2km)
min_lat = lat - 0.01
max_lat = lat + 0.01
min_lon = lon - 0.01
max_lon = lon + 0.01

url = f"https://portal.opentopography.org/API/globaldem?demtype=SRTMGL1&south={min_lat}&north={max_lat}&west={min_lon}&east={max_lon}&outputFormat=GTiff&API_Key={API_KEY}"

print(f"URL: {url[:100]}...")
print("İndiriliyor...")

try:
    # İndir
    urllib.request.urlretrieve(url, "test_gercek_output.tif")
    
    # Dosyayı kontrol et
    if os.path.exists("test_gercek_output.tif"):
        dosya_boyutu = os.path.getsize("test_gercek_output.tif")
        print(f"Dosya boyutu: {dosya_boyutu} byte")
        
        # İlk 100 byte'ı oku (hata mesajı mı yoksa GeoTIFF mi görmek için)
        with open("test_gercek_output.tif", "rb") as f:
            baslangic = f.read(100)
            print(f"Dosya başlangıcı: {baslangic[:50]}")
            
            # "error" kelimesi varsa hata mesajıdır
            if b"error" in baslangic.lower() or b"<html" in baslangic.lower():
                print("✗ Bu bir hata mesajı, GeoTIFF değil!")
                # Hata içeriğini oku
                with open("test_gercek_output.tif", "r", encoding="utf-8", errors="ignore") as f2:
                    print(f"Hata içeriği: {f2.read(500)}")
            else:
                print("✓ Dosya GeoTIFF gibi görünüyor")
                # Rasterio ile dene
                try:
                    with rasterio.open("test_gercek_output.tif") as src:
                        dem = src.read(1)
                        print(f"✓ BAŞARILI! DEM boyutu: {dem.shape}")
                except Exception as e:
                    print(f"Rasterio hatası: {e}")
    else:
        print("✗ Dosya oluşturulamadı")
        
except Exception as e:
    print(f"Hata: {e}")