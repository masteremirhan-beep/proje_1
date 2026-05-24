# kmz_exporter.py - METAL/MİNERAL POTANSİYEL ANALİZİ EKLENDİ
import numpy as np
import zipfile
import os
from xml.etree.ElementTree import Element, SubElement, ElementTree
from datetime import datetime

class KMZExporter:
    def __init__(self):
        pass
    
    def analyze_mineral_potential(self, anomaly_value):
        """
        Anomali değerine göre mineral/met potansiyelini hesapla
        """
        abs_val = abs(anomaly_value)
        
        if abs_val >= 30:
            potential = "🔥 ÇOK YÜKSEK"
            color = "#ff0000"
        elif abs_val >= 20:
            potential = "⚠️ YÜKSEK"
            color = "#ff6600"
        elif abs_val >= 10:
            potential = "📈 ORTA"
            color = "#ffcc00"
        elif abs_val >= 5:
            potential = "🔍 DÜŞÜK"
            color = "#88ff88"
        else:
            potential = "⚪ ÖNEMSİZ"
            color = "#888888"
        
        return potential, color
    
    def create_kml_from_anomaly(self, anomaly_data, lat, lon, width_m, height_m, threshold=5.0, output_path="anomaly.kml"):
        """Anomali verisinden KML dosyası oluştur (METAL/MİNERAL POTANSİYEL İLE)"""
        
        rows, cols = anomaly_data.shape
        
        # Derece dönüşümleri
        lat_per_meter = 1 / 111320
        lon_per_meter = 1 / (111320 * np.cos(np.radians(lat)))
        
        pixel_width_deg = (width_m / cols) * lon_per_meter
        pixel_height_deg = (height_m / rows) * lat_per_meter
        
        min_lat = lat - (height_m / 2) * lat_per_meter
        max_lat = lat + (height_m / 2) * lat_per_meter
        min_lon = lon - (width_m / 2) * lon_per_meter
        max_lon = lon + (width_m / 2) * lon_per_meter
        
        # KML dokümanı
        kml = Element("kml", xmlns="http://www.opengis.net/kml/2.2")
        document = SubElement(kml, "Document")
        
        name = SubElement(document, "name")
        name.text = f"Metal/Mineral Potansiyel Analizi - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        self._add_styles(document)
        
        # ========== METAL/MİNERAL POTANSİYEL KLASÖRLERİ ==========
        
        high_folder = SubElement(document, "Folder")
        high_name = SubElement(high_folder, "name")
        high_name.text = "🔥 YÜKSEK POTANSİYEL BÖLGELER (> ±20m)"
        
        medium_folder = SubElement(document, "Folder")
        medium_name = SubElement(medium_folder, "name")
        medium_name.text = "📈 ORTA POTANSİYEL BÖLGELER (±10-20m)"
        
        low_folder = SubElement(document, "Folder")
        low_name = SubElement(low_folder, "name")
        low_name.text = "🔍 DÜŞÜK POTANSİYEL BÖLGELER (±5-10m)"
        
        # Grid üzerinde dolaş (her 2. piksel - optimize)
        step = max(1, min(rows, cols) // 25)
        
        for i in range(0, rows, step):
            for j in range(0, cols, step):
                anomaly_value = anomaly_data[i, j]
                
                if abs(anomaly_value) >= threshold:
                    point_lat = max_lat - (i + 0.5) * pixel_height_deg
                    point_lon = min_lon + (j + 0.5) * pixel_width_deg
                    
                    # Metal/mineral potansiyelini hesapla
                    potential, color = self.analyze_mineral_potential(anomaly_value)
                    
                    # Hangi klasöre gideceğini belirle
                    if abs(anomaly_value) >= 20:
                        folder = high_folder
                    elif abs(anomaly_value) >= 10:
                        folder = medium_folder
                    else:
                        folder = low_folder
                    
                    # Placemark oluştur
                    pm = SubElement(folder, "Placemark")
                    pm_name = SubElement(pm, "name")
                    
                    # Anomali tipine göre isimlendirme
                    if anomaly_value < 0:
                        pm_name.text = f"🔵 BOŞLUK/ÇÖKÜNTÜ: {anomaly_value:.1f}m | Potansiyel: {potential}"
                    else:
                        pm_name.text = f"🔴 DOLGU/YAPI: +{anomaly_value:.1f}m | Potansiyel: {potential}"
                    
                    # Detaylı açıklama
                    pm_desc = SubElement(pm, "description")
                    
                    anomaly_type = "ÇÖKÜNTÜ (Olası Boşluk)" if anomaly_value < 0 else "YÜKSELTİ (Olası Yapı/Dolgu)"
                    
                    # Metal/mineral yorumu
                    mineral_comment = ""
                    if abs(anomaly_value) >= 30:
                        mineral_comment = """
                        <b><font color="#ff0000">🔥 METAL/MİNERAL POTANSİYELİ ÇOK YÜKSEK!</font></b><br/>
                        Bu bölgede:
                        <ul>
                        <li>Yoğun mineral birikimi olabilir</li>
                        <li>Metal içeren kayaçlar bulunabilir</li>
                        <li>Detaylı jeofizik survey önerilir</li>
                        </ul>
                        """
                    elif abs(anomaly_value) >= 20:
                        mineral_comment = """
                        <b><font color="#ff6600">⚠️ METAL/MİNERAL POTANSİYELİ YÜKSEK</font></b><br/>
                        Bu bölgede ikincil mineral zon olabilir.
                        """
                    elif abs(anomaly_value) >= 10:
                        mineral_comment = """
                        <b>📈 ORTA DERECEDE POTANSİYEL</b><br/>
                        Saha araştırması önerilir.
                        """
                    
                    pm_desc.text = f"""
                    <![CDATA[
                    <b>ANOMALİ ANALİZİ</b><br/>
                    <hr/>
                    <b>Anomali Değeri:</b> {anomaly_value:.2f} metre<br/>
                    <b>Tip:</b> {anomaly_type}<br/>
                    <b>Metal/Mineral Potansiyeli:</b> {potential}<br/>
                    <b>Koordinat:</b> {point_lat:.6f}, {point_lon:.6f}<br/>
                    {mineral_comment}
                    <hr/>
                    <b>Öneri:</b><br/>
                    - Manyetik alan ölçümü yapılmalı<br/>
                    - Jeokimyasal örnekleme gerekli<br/>
                    - GPR (Yeraltı Radarı) ile doğrulama
                    ]]>
                    """
                    
                    # Stil
                    style = SubElement(pm, "styleUrl")
                    if anomaly_value < 0:
                        intensity = min(9, int(abs(anomaly_value) / 5))
                        style.text = f"#neg_{min(intensity, 9)}"
                    else:
                        intensity = min(9, int(abs(anomaly_value) / 5))
                        style.text = f"#pos_{min(intensity, 9)}"
                    
                    # Nokta
                    point = SubElement(pm, "Point")
                    coords = SubElement(point, "coordinates")
                    coords.text = f"{point_lon},{point_lat},0"
        
        # İstatistik ve özet
        stats = SubElement(document, "Folder")
        stats_name = SubElement(stats, "name")
        stats_name.text = "📊 METAL/MİNERAL POTANSİYEL ÖZETİ"
        
        high_count = np.sum(np.abs(anomaly_data) >= 20)
        medium_count = np.sum((np.abs(anomaly_data) >= 10) & (np.abs(anomaly_data) < 20))
        low_count = np.sum((np.abs(anomaly_data) >= threshold) & (np.abs(anomaly_data) < 10))
        
        stats_desc = SubElement(stats, "description")
        stats_desc.text = f"""
        <![CDATA[
        <b>🔍 METAL/MİNERAL POTANSİYEL RAPORU</b><br/>
        <hr/>
        <b>Tarih:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Koordinat:</b> {lat:.6f}, {lon:.6f}<br/>
        <b>Analiz Alanı:</b> {width_m:.0f}m x {height_m:.0f}m<br/>
        <hr/>
        <b><font color="#ff0000">🔥 YÜKSEK POTANSİYEL (>±20m):</font></b> {high_count} nokta<br/>
        <b><font color="#ff6600">📈 ORTA POTANSİYEL (±10-20m):</font></b> {medium_count} nokta<br/>
        <b><font color="#88ff88">🔍 DÜŞÜK POTANSİYEL (±5-10m):</font></b> {low_count} nokta<br/>
        <hr/>
        <b>ÖNERİLEN ARAŞTIRMA YÖNTEMLERİ:</b><br/>
        1. Manyetik alan haritalaması<br/>
        2. Jeokimyasal yüzey örneklemesi<br/>
        3. Yeraltı Radarı (GPR) surveyi<br/>
        4. Hedefli sondaj programı
        ]]>
        """
        
        return kml
    
    def _add_styles(self, document):
        """KML stillerini ekle"""
        # Çöküntü (negatif) stilleri - 10 farklı şiddet
        neg_colors = ["#b3d4ff", "#88bbff", "#66a3ff", "#4488ff", "#2266cc", 
                      "#0044aa", "#003388", "#002266", "#001144", "#000022"]
        for i, color in enumerate(neg_colors):
            style = SubElement(document, "Style", id=f"neg_{i}")
            icon_style = SubElement(style, "IconStyle")
            color_elem = SubElement(icon_style, "color")
            color_elem.text = self._hex_to_kml_color(color)
            scale = SubElement(icon_style, "scale")
            scale.text = str(0.5 + i * 0.1)
        
        # Yükselti (pozitif) stilleri
        pos_colors = ["#ffcccc", "#ff9999", "#ff6666", "#ff3333", "#ff0000",
                      "#cc0000", "#990000", "#660000", "#330000", "#1a0000"]
        for i, color in enumerate(pos_colors):
            style = SubElement(document, "Style", id=f"pos_{i}")
            icon_style = SubElement(style, "IconStyle")
            color_elem = SubElement(icon_style, "color")
            color_elem.text = self._hex_to_kml_color(color)
            scale = SubElement(icon_style, "scale")
            scale.text = str(0.5 + i * 0.1)
    
    def _hex_to_kml_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return f"ff{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"
    
    def export_to_kmz(self, anomaly_data, lat, lon, width_m, height_m, output_path, threshold=5.0):
        temp_kml = "temp_anomaly.kml"
        kml = self.create_kml_from_anomaly(anomaly_data, lat, lon, width_m, height_m, threshold, temp_kml)
        
        tree = ElementTree(kml)
        tree.write(temp_kml, encoding='utf-8', xml_declaration=True)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
            kmz.write(temp_kml, "doc.kml")
            
            readme = f"""
            METAL/MİNERAL POTANSİYEL ANALİZİ - RAPOR
            =========================================
            
            Koordinat: {lat:.6f}, {lon:.6f}
            
            Renk Kodları:
            - 🔴 Koyu Kırmızı: Çok yüksek pozitif anomali (dolgu/yapı)
            - 🔵 Koyu Mavi: Çok yüksek negatif anomali (boşluk)
            
            Potansiyel Değerlendirmesi:
            - > ±20m: YÜKSEK metal/mineral potansiyeli
            - ±10-20m: ORTA potansiyel
            - ±5-10m: Düşük potansiyel
            
            Google Earth'te açmak için:
            1. Dosyayı çift tıklayın
            2. Katmanları kontrol edin
            """
            
            kmz.writestr("README.txt", readme)
        
        os.remove(temp_kml)
        return output_path

def export_anomaly_to_kmz(anomaly_data, lat, lon, width_m, height_m, output_dir, threshold=5.0):
    exporter = KMZExporter()
    # Daha basit ve anlaşılır dosya adı
    output_path = os.path.join(output_dir, f"anomali.kmz")
    return exporter.export_to_kmz(anomaly_data, lat, lon, width_m, height_m, output_path, threshold)