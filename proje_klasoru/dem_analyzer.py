# dem_analyzer.py - OTOMATİK SİGMA SEÇİCİLİ
import numpy as np
from scipy.ndimage import gaussian_filter, median_filter, uniform_filter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DEMAnalyzer:
    def __init__(self):
        self.dem_data = None
        self.trend = None
        self.residual = None
        self.filtered = None
        self.auto_sigma = None
    
    def load_dem(self, dem):
        """DEM verisini yükle"""
        self.dem_data = dem
    
    def auto_select_sigma(self, dem=None):
        """
        DEM verisine göre en uygun sigma değerini otomatik seçer
        """
        if dem is None:
            dem = self.dem_data
        
        if dem is None:
            return 50  # varsayılan
        
        # 1. Arazinin pürüzlülüğünü hesapla (standart sapma)
        roughness = np.std(dem)
        
        # 2. Eğim analizi
        gy, gx = np.gradient(dem)
        slope = np.sqrt(gx**2 + gy**2)
        avg_slope = np.mean(slope)
        
        # 3. Arazi tipine göre sigma seçimi
        if roughness < 10:  # Çok düz arazi (ova, plato)
            auto_sigma = 30
            terrain_type = "Düz arazi"
        elif roughness < 30:  # Orta dalgalı (tepeler)
            auto_sigma = 50
            terrain_type = "Dalgalı arazi"
        elif roughness < 60:  # Engebeli (dağlık)
            auto_sigma = 70
            terrain_type = "Engebeli arazi"
        else:  # Çok engebeli (yüksek dağlar)
            auto_sigma = 90
            terrain_type = "Çok engebeli arazi"
        
        # Eğime göre fine-tuning
        if avg_slope > 20:  # Dik eğimler
            auto_sigma += 10
        elif avg_slope < 5:  # Çok düz
            auto_sigma -= 10
        
        # Sigma sınırları (15-100 arası)
        auto_sigma = max(15, min(100, auto_sigma))
        self.auto_sigma = auto_sigma
        
        print(f"  📊 Otomatik sigma seçimi:")
        print(f"     Arazi tipi: {terrain_type}")
        print(f"     Pürüzlülük: {roughness:.1f}m")
        print(f"     Ortalama eğim: {avg_slope:.1f}°")
        print(f"     ✅ Seçilen sigma: {auto_sigma}")
        
        return auto_sigma
    
    def calculate_trend(self, sigma=None):
        """
        Trend surface hesapla
        sigma=None ise otomatik seç
        """
        if sigma is None:
            sigma = self.auto_select_sigma()
        
        self.trend = gaussian_filter(self.dem_data, sigma=sigma)
        self.last_sigma = sigma
        return self.trend
    
    def calculate_residual(self):
        """Residual (anomali) hesapla"""
        self.residual = self.dem_data - self.trend
        return self.residual
    
    def apply_filter(self, filter_type, **params):
        """Filtre uygula"""
        if self.residual is None:
            self.calculate_residual()
        
        if filter_type == "Gaussian":
            sigma = params.get('sigma', 1)
            self.filtered = gaussian_filter(self.residual, sigma=sigma)
        elif filter_type == "Median":
            size = params.get('size', 3)
            self.filtered = median_filter(self.residual, size=size)
        elif filter_type == "Low-pass":
            size = params.get('size', 5)
            self.filtered = uniform_filter(self.residual, size=size)
        elif filter_type == "High-pass":
            sigma = params.get('sigma', 5)
            lowpass = gaussian_filter(self.residual, sigma=sigma)
            self.filtered = self.residual - lowpass
        else:
            self.filtered = self.residual
        
        return self.filtered
    
    def get_statistics(self, threshold=5.0):
        """İstatistik hesapla"""
        if self.filtered is None:
            return None
        
        neg_anomaly = self.filtered[self.filtered < -threshold].size
        pos_anomaly = self.filtered[self.filtered > threshold].size
        total = self.filtered.size
        
        return {
            'neg_ratio': (neg_anomaly / total) * 100,
            'pos_ratio': (pos_anomaly / total) * 100,
            'std': np.std(self.filtered),
            'min': self.filtered.min(),
            'max': self.filtered.max(),
            'mean': np.mean(self.filtered),
            'auto_sigma': self.last_sigma if hasattr(self, 'last_sigma') else None
        }
    
    def plot_anomaly(self, parent_frame, cmap='RdBu'):
        """Anomali haritasını göster"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        valid_cmaps = ['RdBu', 'viridis', 'plasma', 'inferno', 'magma', 'coolwarm', 'jet', 'seismic']
        if cmap.lower() not in [c.lower() for c in valid_cmaps] and cmap not in valid_cmaps:
            cmap = 'RdBu'
        
        im = ax.imshow(self.filtered, cmap=cmap, interpolation='nearest')
        plt.colorbar(im, ax=ax, label="Anomali (m)")
        
        # Sigma bilgisini başlığa ekle
        sigma_text = f" (Otomatik Sigma={self.last_sigma})" if hasattr(self, 'last_sigma') else ""
        ax.set_title(f"Anomali Haritası{sigma_text}\n(Mavi=Çöküntü, Kırmızı=Yükselti)")
        ax.set_xlabel("Piksel X")
        ax.set_ylabel("Piksel Y")
        ax.grid(True, linestyle='--', alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        return canvas