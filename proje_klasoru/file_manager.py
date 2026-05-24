# file_manager.py - KESİN ÇÖZÜM (tüm numpy tiplerini dönüştürür)
import os
from datetime import datetime
import json
import numpy as np
from config import OUTPUTS_DIR

class FileManager:
    def __init__(self):
        self.sessions_dir = os.path.join(OUTPUTS_DIR, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def create_session_name(self, lat, lon):
        """Oturum adı oluştur (tarih saat + koordinat)"""
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        lat_short = f"{lat:.4f}".replace(".", "_")
        lon_short = f"{lon:.4f}".replace(".", "_")
        session_name = f"{timestamp}_L{lat_short}_L{lon_short}"
        return session_name
    
    def _convert_value(self, val):
        """Herhangi bir değeri JSON uyumlu hale getir"""
        if isinstance(val, (np.float32, np.float64)):
            return float(val)
        elif isinstance(val, (np.int32, np.int64)):
            return int(val)
        elif isinstance(val, np.ndarray):
            return val.tolist()
        elif isinstance(val, dict):
            return {k: self._convert_value(v) for k, v in val.items()}
        elif isinstance(val, (list, tuple)):
            return [self._convert_value(item) for item in val]
        elif isinstance(val, (np.bool_)):
            return bool(val)
        else:
            return val
    
    def save_analysis(self, lat, lon, params, stats, dem_data, filtered_data, output_paths):
        """Tüm analiz verilerini kaydet"""
        session_name = self.create_session_name(lat, lon)
        session_dir = os.path.join(self.sessions_dir, session_name)
        os.makedirs(session_dir, exist_ok=True)
        
        # Tüm verileri JSON uyumlu hale getir
        lat_clean = float(lat)
        lon_clean = float(lon)
        params_clean = self._convert_value(params)
        stats_clean = self._convert_value(stats)
        
        # 1. Parametreleri JSON olarak kaydet
        params_file = os.path.join(session_dir, "params.json")
        with open(params_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "coordinates": {"lat": lat_clean, "lon": lon_clean},
                "parameters": params_clean,
                "statistics": stats_clean,
                "output_files": output_paths
            }, f, indent=2, ensure_ascii=False)
        
        # 2. İstatistikleri TXT olarak kaydet
        report_file = os.path.join(session_dir, "rapor.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("DEM ANALİZ RAPORU\n")
            f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            f.write(f"Koordinat: {lat}, {lon}\n")
            f.write(f"Alan: {params.get('width', '?')}m x {params.get('height', '?')}m\n\n")
            f.write("--- ANALİZ PARAMETRELERİ ---\n")
            for key, value in params.items():
                f.write(f"{key}: {value}\n")
            f.write("\n--- İSTATİSTİKLER ---\n")
            for key, value in stats.items():
                f.write(f"{key}: {value}\n")
            f.write("\n--- ÇIKTI DOSYALARI ---\n")
            for key, value in output_paths.items():
                f.write(f"{key}: {value}\n")
        
        # 3. NumPy verilerini kaydet (ham veri)
        if dem_data is not None:
            np_file = os.path.join(session_dir, "dem_data.npy")
            np.save(np_file, dem_data)
        
        if filtered_data is not None:
            np_filtered = os.path.join(session_dir, "anomaly_data.npy")
            np.save(np_filtered, filtered_data)
        
        print(f"✅ Kayıt tamamlandı: {session_dir}")
        return session_dir, session_name
    
    def list_sessions(self):
        """Tüm kayıtlı oturumları listele"""
        if not os.path.exists(self.sessions_dir):
            return []
        
        sessions = []
        for item in os.listdir(self.sessions_dir):
            item_path = os.path.join(self.sessions_dir, item)
            if os.path.isdir(item_path):
                params_file = os.path.join(item_path, "params.json")
                if os.path.exists(params_file):
                    with open(params_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    sessions.append({
                        "name": item,
                        "path": item_path,
                        "timestamp": data.get("timestamp", ""),
                        "coordinates": data.get("coordinates", {})
                    })
        return sorted(sessions, key=lambda x: x["name"], reverse=True)
    
    def load_session(self, session_name):
        """Kayıtlı bir oturumu yükle"""
        session_dir = os.path.join(self.sessions_dir, session_name)
        if not os.path.exists(session_dir):
            return None
        
        params_file = os.path.join(session_dir, "params.json")
        with open(params_file, 'r', encoding='utf-8') as f:
            params = json.load(f)
        
        # Verileri yükle
        dem_data = None
        anomaly_data = None
        
        np_file = os.path.join(session_dir, "dem_data.npy")
        if os.path.exists(np_file):
            dem_data = np.load(np_file)
        
        np_filtered = os.path.join(session_dir, "anomaly_data.npy")
        if os.path.exists(np_filtered):
            anomaly_data = np.load(np_filtered)
        
        return {
            "params": params,
            "dem_data": dem_data,
            "anomaly_data": anomaly_data,
            "session_dir": session_dir
        }