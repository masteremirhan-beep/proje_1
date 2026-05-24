import sys
import os
import importlib.util

# --- 1. PROJE YOLU AYARI (Kritik) ---
# main_gui.py dosyası 01_Ana_Menu içinde olduğu için bir üst klasörü (proje kökünü) ekliyoruz.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLabel)
from PyQt6.QtCore import Qt

# --- 2. MODÜL IMPORTLARI (Hata Kontrollü) ---
try:
    # Rakamla başlayan klasörleri import ederken bazen sorun çıkabilir, 
    # bu yüzden dinamik yükleme en garanti yoldur.
    def show_3d_topography():
        spec = importlib.util.spec_from_file_location("visualizer", os.path.join(project_root, "04_Analiz_Merkezi", "visualizer.py"))
        viz_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(viz_module)
        viz_module.show_3d_topography()
except Exception as e:
    def show_3d_topography(): print(f"Görselleştirme hatası: {e}")

def get_map_class():
    module_path = os.path.join(project_root, '02_Otomatik_Izlek', 'izlek_engine.py')
    spec = importlib.util.spec_from_file_location("izlek_engine", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.MapStation

# --- 3. ANA UYGULAMA ---
class OtoSurferApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oto Surfer Analiz")
        self.setFixedSize(550, 450)
        self.setStyleSheet("background-color: #f5f5f5;")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Başlık
        title = QLabel("OTO SURFER SİSTEMİ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 18px; color: #333;")
        main_layout.addWidget(title)

        # Otomatik İzlek Butonu
        self.btn_oto_izlek = QPushButton("Otomatik İzlek Oluştur")
        self.btn_oto_izlek.setFixedHeight(60)
        self.btn_oto_izlek.setStyleSheet("background-color: #0088cc; color: white; font-weight: bold; font-size: 14px;")
        self.btn_oto_izlek.clicked.connect(self.ac_harita)
        main_layout.addWidget(self.btn_oto_izlek)

        # 3D Contour Butonu
        mid_layout = QHBoxLayout()
        self.btn_3d_contour = QPushButton("3D-Contour Gösterme")
        self.btn_3d_contour.setFixedHeight(50)
        self.btn_3d_contour.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        self.btn_3d_contour.clicked.connect(show_3d_topography)
        
        mid_layout.addWidget(self.btn_3d_contour)
        main_layout.addLayout(mid_layout)

        self.status_label = QLabel("Sistem Hazır...")
        self.status_label.setStyleSheet("color: green;")
        main_layout.addWidget(self.status_label)

    def ac_harita(self):
        try:
            MapClass = get_map_class()
            self.h_pencere = MapClass()
            self.h_pencere.show()
        except Exception as e:
            self.status_label.setText(f"Hata: {e}")
            self.status_label.setStyleSheet("color: red;")

if __name__ == "__main__":
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    win = OtoSurferApp()
    win.show()
    sys.exit(app.exec())