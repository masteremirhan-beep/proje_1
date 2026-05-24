import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QFrame, QGridLayout, QApplication)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QTimer

class MapStation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DefineRota - Otomatik Harita ve Arazi Analizi")
        self.showMaximized()
        self.setStyleSheet("background-color: #12141d;")

        # --- ANA LAYOUT VE WIDGET ---
        ana_widget = QWidget()
        layout = QVBoxLayout(ana_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- ÜST PANEL TASARIMI ---
        self.ust_panel = QFrame()
        self.ust_panel.setFixedHeight(80)
        self.ust_panel.setStyleSheet("background-color: #1b1e29; border-bottom: 1px solid #2d313d;")
        p_layout = QHBoxLayout(self.ust_panel)

        # 1. Koordinat Girişi
        self.coord_input = QLineEdit("37.626651, 37.983352")
        self.coord_input.setFixedWidth(180)
        self.coord_input.setStyleSheet("background-color: #12141d; color: #ffffff; border: 1px solid #2d313d; padding: 5px;")
        
        self.btn_git = QPushButton("GİT")
        self.btn_git.setFixedWidth(50)
        self.btn_git.setStyleSheet("background-color: #0088cc; color: white; font-weight: bold;")
        
        p_layout.addWidget(QLabel("📍 KOORDİNAT"))
        p_layout.addWidget(self.coord_input)
        p_layout.addWidget(self.btn_git)

        # 2. Alan ve Tarama Hassasiyeti
        self.tarama_input = QLineEdit("0.5")
        self.tarama_input.setFixedWidth(40)
        self.tarama_input.setStyleSheet("background-color: #12141d; color: #ffffff; border: 1px solid #2d313d; padding: 5px;")
        
        self.btn_baslat = QPushButton("▶ BAŞLAT")
        self.btn_baslat.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 8px 20px;")
        
        p_layout.addSpacing(20)
        p_layout.addWidget(QLabel("🛰️ TARAMA"))
        p_layout.addWidget(self.tarama_input)
        p_layout.addWidget(QLabel("m"))
        p_layout.addWidget(self.btn_baslat)
        p_layout.addStretch()
        
        # Durum Göstergeleri
        self.lbl_nokta = QLabel("0\nNOKTA")
        self.lbl_nokta.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 14px; text-align: center;")
        self.lbl_ilerleme = QLabel("SİSTEM HAZIRLANIYOR...")
        self.lbl_ilerleme.setStyleSheet("color: #e67e22; font-weight: bold; font-size: 12px;")
        p_layout.addWidget(self.lbl_nokta)
        p_layout.addWidget(self.lbl_ilerleme)

        layout.addWidget(self.ust_panel)

        # --- HARİTA VE SAĞ BUTONLAR ---
        map_container = QWidget()
        map_layout = QGridLayout(map_container)
        map_layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QWebEngineView()
        ayarlar = self.browser.settings()
        ayarlar.setAttribute(ayarlar.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        ayarlar.setAttribute(ayarlar.WebAttribute.LocalContentCanAccessFileUrls, True)
        ayarlar.setAttribute(ayarlar.WebAttribute.JavascriptEnabled, True)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_folder = os.path.join(current_dir, "Map_Engine")
        path = os.path.join(map_folder, "map_view.html")
        baseUrl = QUrl.fromLocalFile(map_folder + os.path.sep)

        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.browser.setHtml(f.read(), baseUrl)
            else:
                print(f"Hata: map_view.html bulunamadı -> {path}")
        except Exception as e:
            print(f"Harita Yükleme Hatası: {e}")

        map_layout.addWidget(self.browser, 0, 0)

        # Sağ Üst DAT/CSV Butonları
        self.btn_dat = QPushButton("📄 DAT")
        self.btn_dat.setFixedSize(60, 40)
        self.btn_dat.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; border-radius: 5px;")
        
        self.btn_csv = QPushButton("📊 CSV")
        self.btn_csv.setFixedSize(60, 40)
        self.btn_csv.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; border-radius: 5px;")
        
        sag_buton_layout = QVBoxLayout()
        sag_buton_layout.addWidget(self.btn_dat)
        sag_buton_layout.addWidget(self.btn_csv)
        sag_buton_layout.addStretch()
        
        map_layout.addLayout(sag_buton_layout, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        layout.addWidget(map_container)
        self.setCentralWidget(ana_widget)

        # --- BAĞLANTILAR ---
        self.btn_git.clicked.connect(self.konuma_git)
        self.btn_baslat.clicked.connect(self.tarama_baslat)
        self.btn_dat.clicked.connect(self.dat_kaydet)
        self.btn_csv.clicked.connect(self.csv_kaydet)
        self.browser.loadFinished.connect(self.harita_hazir)
    
    # --- FONKSİYONLAR (HEPSİ ARTIK CLASS İÇİNDE) ---
    def harita_hazir(self, success):
        if success:
            self.lbl_ilerleme.setText("SİSTEM HAZIR")
            self.lbl_ilerleme.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.lbl_ilerleme.setText("HARİTA HATASI!")

    def konuma_git(self):
        kord_ham = self.coord_input.text().strip()
        try:
            if "," in kord_ham:
                lat, lng = kord_ham.replace(" ", "").split(",")
                js_kodu = f"window.haritayiKaydir('{lat}', '{lng}');"
                self.browser.page().runJavaScript(js_kodu, self.kontrollu_git)
            else:
                self.lbl_ilerleme.setText("VİRGÜL EKSİK!")
        except Exception as e:
            print(f"Hata: {e}")

    def kontrollu_git(self, sonuc):
        if sonuc == "OK":
            self.lbl_ilerleme.setText("HEDEFE GİDİLDİ")
            self.lbl_ilerleme.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            # Harita tam yüklenmemişse 1 saniye sonra tekrar dene
            QTimer.singleShot(1000, self.konuma_git)

    def tarama_baslat(self):
        try:
            aralik_metin = self.tarama_input.text().replace(",", ".")
            aralik = float(aralik_metin)
            self.browser.page().runJavaScript(f"window.manuelAlanTaramasi({aralik});", self.sonuc_goster)
        except Exception as e:
            self.lbl_ilerleme.setText("ARALIK HATALI")
            print(f"Tarama Hatası: {e}")

    def sonuc_goster(self, nokta_sayisi):
        if nokta_sayisi == "ALAN_YOK":
            self.lbl_ilerleme.setText("ÖNCE ALAN ÇİZ!")
            self.lbl_ilerleme.setStyleSheet("color: #e74c3c;")
        else:
            self.lbl_nokta.setText(f"{nokta_sayisi}\nNOKTA")
            self.lbl_ilerleme.setText("TARAMA OK")
            self.lbl_ilerleme.setStyleSheet("color: #2ecc71;")

    def dat_kaydet(self):
        print("Sistem: Koordinatlar .DAT formatında kaydediliyor...")
        self.lbl_ilerleme.setText("DAT OK")

    def csv_kaydet(self):
        print("Sistem: Koordinatlar .CSV formatında kaydediliyor...")
        self.lbl_ilerleme.setText("CSV OK")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = MapStation()
    pencere.show()
    sys.exit(app.exec())