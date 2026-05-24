# main.py - TAM GÜNCEL VERSİYON (Gerçekçi anomali tespiti ile)
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from config import DOWNLOADS_DIR, OUTPUTS_DIR

# ============================================
# MOTORLARI İÇE AKTAR
# ============================================

# 1. MOTOR: OpenTopography (GERÇEK DEM - API ile)
try:
    from engine3_opentopo import download_dem_opentopo
    OPENTOPO_VAR = True
    print("✓ OpenTopography motoru hazır (GERÇEK DEM)")
except ImportError:
    OPENTOPO_VAR = False
    print("✗ OpenTopography motoru bulunamadı")

# 2. MOTOR: Copernicus (YEREL DEM - manuel indirilen dosya)
try:
    from engine3_copernicus import download_dem_copernicus
    COPERNICUS_VAR = True
    print("✓ Copernicus motoru hazır (YEREL DEM)")
except ImportError:
    COPERNICUS_VAR = False
    print("✗ Copernicus motoru bulunamadı")

# 3. MOTOR: SRTM (SENTETİK TEST - yedek)
try:
    from engine1_srtm import download_dem_srtm
    SRTM_VAR = True
    print("✓ SRTM test motoru hazır")
except ImportError:
    SRTM_VAR = False
    print("✗ SRTM motoru bulunamadı")

# 4. MOTOR: ALOS (SENTETİK TEST - yedek)
try:
    from engine2_alos import download_dem_alos
    ALOS_VAR = True
    print("✓ ALOS test motoru hazır")
except ImportError:
    ALOS_VAR = False
    print("✗ ALOS motoru bulunamadı")

# ============================================
# DEM İŞLEME FONKSİYONLARI
# ============================================

def calculate_trend_surface(dem, sigma=50):
    """Doğal topoğrafya trend yüzeyi - sigma=50 önerilir"""
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(dem, sigma=sigma)

def calculate_residual(dem, trend):
    """Anomali haritası = DEM - Trend"""
    return dem - trend

def apply_filters(residual, median_size=3):
    """Gürültü azaltma"""
    from scipy.ndimage import median_filter
    return median_filter(residual, size=median_size)

def plot_and_save(residual, output_path):
    """Anomali haritasını kaydet"""
    plt.figure(figsize=(10, 8))
    im = plt.imshow(residual, cmap='RdBu', interpolation='bilinear')
    plt.colorbar(im, label="Anomali (m)")
    plt.title("Yeraltı Boşluk Anomalisi (Mavi=Çöküntü/Potansiyel Boşluk)")
    plt.savefig(output_path, dpi=150)
    plt.close()

def log_error(engine_name, error_msg):
    """Hataları log dosyasına yaz"""
    log_path = os.path.join("logs", "hata_logu.txt")
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {engine_name}: {error_msg}\n")

# ============================================
# ANA ANALİZ FONKSİYONU
# ============================================

def analiz_yap(lat, lon, width_m, height_m, sigma=50, anomali_esik=5.0):
    """
    Ana analiz fonksiyonu
    
    Parametreler:
    - lat, lon: koordinatlar
    - width_m, height_m: alan büyüklüğü (metre)
    - sigma: trend yüzeyi yumuşaklığı (15=detaylı, 50=genel, 100=çok genel)
    - anomali_esik: anomali sayma eşiği (metre, 5.0 önerilir)
    """
    print("\n" + "="*60)
    print(f"ANALİZ BAŞLATILIYOR")
    print(f"Koordinat: {lat}, {lon}")
    print(f"Alan: {width_m}m x {height_m}m")
    print(f"Sigma (trend yumuşaklık): {sigma}")
    print(f"Anomali eşiği: ±{anomali_esik} metre")
    print("="*60 + "\n")
    
    # ========================================
    # MOTOR SIRALAMASI (ÖNCE GERÇEK, SONRA YEDEK)
    # ========================================
    engines = []
    
    # 1. Öncelik: OpenTopography (API ile otomatik gerçek DEM)
    if OPENTOPO_VAR:
        engines.append(("🌍 OpenTopography (GERÇEK DEM - API ile)", download_dem_opentopo))
    
    # 2. İkincil: Copernicus (yerel DEM dosyası)
    if COPERNICUS_VAR:
        engines.append(("📁 Copernicus (YEREL DEM Dosyası)", download_dem_copernicus))
    
    # 3. Yedek: SRTM sentetik test
    if SRTM_VAR:
        engines.append(("🧪 SRTM (SENTETİK TEST - Yedek)", download_dem_srtm))
    
    # 4. Son yedek: ALOS sentetik test
    if ALOS_VAR:
        engines.append(("🧪 ALOS (SENTETİK TEST - Son Yedek)", download_dem_alos))
    
    if not engines:
        print("\n❌ HİÇBİR MOTOR BULUNAMADI!")
        return False
    
    # ========================================
    # MOTORLARI SIRAYLA DENE
    # ========================================
    dem_data = None
    successful_engine = None
    
    for engine_name, engine_func in engines:
        print(f"\n>>> {engine_name} motoru deneniyor...")
        
        temp_name = f"temp_{engine_name.replace(' ', '_').replace('(', '').replace(')', '').replace('🌍', '').replace('📁', '').replace('🧪', '')}.tif"
        temp_dem_path = os.path.join(DOWNLOADS_DIR, temp_name)
        
        try:
            success, dem = engine_func(lat, lon, width_m, height_m, temp_dem_path)
            
            if success and dem is not None:
                dem_data = dem
                successful_engine = engine_name
                print(f"\n✅ {engine_name} başarıyla veri çekti!")
                break
            else:
                print(f"❌ {engine_name} başarısız oldu, diğer motor deneniyor...")
                log_error(engine_name, "DEM indirme başarısız")
        except Exception as e:
            print(f"❌ {engine_name} hata verdi: {e}")
            log_error(engine_name, str(e))
    
    if dem_data is None:
        print("\n❌ TÜM MOTORLAR BAŞARISIZ!")
        return False
    
    # ========================================
    # DEM BAŞARIYLA İNDİRİLDİ, ANALİZ BAŞLIYOR
    # ========================================
    print(f"\n>>> DEM başarıyla yüklendi ({successful_engine})")
    print(f">>> Analiz işleniyor...")
    
    # 1. Trend surface hesapla (kullanıcının verdiği sigma ile)
    trend = calculate_trend_surface(dem_data, sigma=sigma)
    print(f"  Trend surface hesaplandı (sigma={sigma})")
    
    # 2. Residual (anomali) hesapla
    residual = calculate_residual(dem_data, trend)
    
    # 3. Filtre uygula (gürültü azaltma)
    filtered = apply_filters(residual, median_size=3)
    
    # 4. Görselleştir ve kaydet
    output_image = os.path.join(OUTPUTS_DIR, f"anomali_{lat}_{lon}.png")
    plot_and_save(filtered, output_image)
    
    # 5. Surfer XYZ formatında dışa aktar
    surfer_xyz = os.path.join(OUTPUTS_DIR, f"anomali_{lat}_{lon}.xyz")
    with open(surfer_xyz, 'w') as f:
        f.write("X Y Z\n")
        for i in range(filtered.shape[0]):
            for j in range(filtered.shape[1]):
                f.write(f"{j*30} {i*30} {filtered[i,j]:.4f}\n")
    
    # 6. Surfer GRD formatında dışa aktar
    surfer_grd = os.path.join(OUTPUTS_DIR, f"anomali_{lat}_{lon}.grd")
    with open(surfer_grd, 'w') as f:
        f.write("DSAA\n")
        f.write(f"{filtered.shape[1]} {filtered.shape[0]}\n")
        f.write(f"0 {filtered.shape[1]*30} 0 {filtered.shape[0]*30}\n")
        f.write(f"{filtered.min():.4f} {filtered.max():.4f}\n")
        for i in range(filtered.shape[0]):
            for j in range(filtered.shape[1]):
                f.write(f"{filtered[i,j]:.4f} ")
            f.write("\n")
    
    # ========================================
    # İSTATİSTİKLER (GERÇEKÇİ EŞİKLERLE)
    # ========================================
    
    # Gerçek anomali tespiti (eşik değerinin üzerindekiler)
    gercek_cokuntu = filtered[filtered < -anomali_esik].size
    gercek_yukselti = filtered[filtered > anomali_esik].size
    toplam_piksel = filtered.size
    
    cokuntu_orani = (gercek_cokuntu / toplam_piksel) * 100
    yukselti_orani = (gercek_yukselti / toplam_piksel) * 100
    anomali_std = np.std(filtered)
    
    print(f"\n✅ ANALİZ TAMAMLANDI!")
    print(f"   Kullanılan motor: {successful_engine}")
    print(f"   Anomali haritası: {output_image}")
    print(f"   Surfer XYZ: {surfer_xyz}")
    print(f"   Surfer GRD: {surfer_grd}")
    
    print(f"\n📊 ANOMALİ ANALİZİ (eşik: ±{anomali_esik}m):")
    print(f"   Gerçek çöküntü alanı (olası boşluk): %{cokuntu_orani:.2f}")
    print(f"   Gerçek yükselti alanı (olası dolgu): %{yukselti_orani:.2f}")
    print(f"   Anomalilerin standart sapması: ±{anomali_std:.2f} metre")
    print(f"   Maksimum çöküntü: {filtered.min():.2f} metre")
    print(f"   Maksimum yükselti: {filtered.max():.2f} metre")
    
    # Yorum
    if cokuntu_orani < 10:
        print(f"\n✅ Sonuç: %{cokuntu_orani:.1f} oranında gerçek anomali tespit edildi (makul)")
    elif cokuntu_orani < 25:
        print(f"\n⚠️ Sonuç: %{cokuntu_orani:.1f} oranında anomali - sigma değerini artırmayı deneyin")
    else:
        print(f"\n⚠️ Sonuç: %{cokuntu_orani:.1f} oranında anomali - sigma değerini büyütün (örnek: sigma=100)")
    
    if "GERÇEK" in successful_engine:
        print(f"\n🎯 BU GERÇEK DEM VERİSİDİR!")
        print(f"   Analiz sonuçları saha ile karşılaştırılabilir.")
    else:
        print(f"\n⚠️ NOT: Sentetik test verisi kullanıldı.")
        print(f"   Gerçek analiz için OpenTopography API key'inizi kontrol edin.")
    
    return True

# ============================================
# PROGRAM BAŞLANGICI
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("   DEM ANALİZ SİSTEMİ - YERALTI BOŞLUK TESPİTİ")
    print("   Yeraltındaki yapıları yüzey izlerinden tespit eder")
    print("="*60)
    
    print("\n" + "="*60)
    print("   AYARLAR HAKKINDA:")
    print("   - Sigma (15=detaylı, 50=genel, 100=çok genel)")
    print("   - Anomali eşiği (metre cinsinden, 5.0 önerilir)")
    print("="*60)
    
    # Kullanıcıdan koordinat ve ayarları iste
    print("\nAnaliz yapmak istediğiniz değerleri girin:")
    print("(Boş bırakırsanız varsayılan değerler kullanılır)\n")
    
    try:
        lat_input = input("Enlem (örn: 41.0559): ").strip()
        lon_input = input("Boylam (örn: 29.6563): ").strip()
        width_input = input("Genişlik (metre, örn: 300): ").strip()
        height_input = input("Yükseklik (metre, örn: 300): ").strip()
        sigma_input = input("Sigma değeri (15/50/100 - öneri: 50): ").strip()
        esik_input = input("Anomali eşiği (metre - öneri: 5.0): ").strip()
        
        lat = float(lat_input) if lat_input else 41.05592165753617
        lon = float(lon_input) if lon_input else 29.656312834259097
        width = float(width_input) if width_input else 300
        height = float(height_input) if height_input else 300
        sigma = float(sigma_input) if sigma_input else 50
        esik = float(esik_input) if esik_input else 5.0
        
    except:
        print("Hatalı giriş, varsayılan değerler kullanılıyor...")
        lat, lon, width, height = 41.05592165753617, 29.656312834259097, 300, 300
        sigma, esik = 50, 5.0
    
    # Analizi başlat
    basarili_mu = analiz_yap(lat, lon, width, height, sigma, esik)
    
    if basarili_mu:
        print("\n" + "="*60)
        print("🎉 PROGRAM BAŞARIYLA TAMAMLANDI!")
        print("   outputs/ klasöründeki dosyaları inceleyebilirsiniz:")
        print(f"   - Anomali haritası: outputs/anomali_{lat}_{lon}.png")
        print(f"   - Surfer dosyaları: outputs/anomali_{lat}_{lon}.xyz ve .grd")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("⚠️ PROGRAM HATA İLE KARŞILAŞTI!")
        print("   logs/hata_logu.txt dosyasını kontrol edin")
        print("="*60)