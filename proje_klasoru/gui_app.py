# ============================================================
# Bu dosya: gui_app.py
# Tüm export işlemleri ANALİZ BAŞLAT ile OTOMATİK yapılır
# ============================================================

import csv
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import threading
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image
import urllib.request
import io
import math
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

from config import DOWNLOADS_DIR, OUTPUTS_DIR
from core.dem_analyzer import DEMAnalyzer
from core.file_manager import FileManager
from core.kmz_exporter import export_anomaly_to_kmz
from engines.engine3_opentopo import download_dem_opentopo


class DEMApp:
    def __init__(self, master):
        self.master = master
        master.title("DEM Analiz Sistemi - Yeraltı Boşluk Tespiti")
        master.geometry("1400x800")
        master.configure(bg='#1e1e1e')

        self.bg_color = "#1e1e1e"
        self.fg_color = "#d4d4d4"
        self.accent_color = "#007acc"
        self.input_bg = "#2d2d2d"

        self.analyzer = DEMAnalyzer()
        self.dem_data = None
        self.file_manager = FileManager()
        self.current_anomaly_data = None
        self.overlay_alpha = tk.DoubleVar(value=0.7)

        self.setup_ui()

    # ============================================================
    # ARAYÜZ KURULUMU
    # ============================================================
    def setup_ui(self):
        main_frame = tk.Frame(self.master, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # SOL PANEL (kaydırmalı)
        left_panel_container = tk.Frame(main_frame, bg=self.bg_color, width=400)
        left_panel_container.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel_container.pack_propagate(False)

        self.canvas = tk.Canvas(left_panel_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(left_panel_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ARA ÇİZGİ
        separator = ttk.Separator(main_frame, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=5)

        # SAĞ PANEL
        right_panel = tk.Frame(main_frame, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ========== SOL PANEL İÇERİĞİ ==========
        tk.Label(self.scrollable_frame, text="🔍 ANALİZ", 
                 font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=5)

        # KOORDİNATLAR
        coord_frame = tk.LabelFrame(self.scrollable_frame, text="📍 Koordinatlar", bg=self.bg_color, fg=self.fg_color)
        coord_frame.pack(fill=tk.X, pady=5, padx=8)
        
        row1 = tk.Frame(coord_frame, bg=self.bg_color)
        row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text="Enlem:", bg=self.bg_color, fg=self.fg_color, width=7, anchor='w').pack(side=tk.LEFT)
        self.lat_entry = tk.Entry(row1, bg=self.input_bg, fg=self.fg_color, width=22)
        self.lat_entry.pack(side=tk.LEFT, padx=5)
        self.lat_entry.insert(0, "41.05592165753617")
        
        row2 = tk.Frame(coord_frame, bg=self.bg_color)
        row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text="Boylam:", bg=self.bg_color, fg=self.fg_color, width=7, anchor='w').pack(side=tk.LEFT)
        self.lon_entry = tk.Entry(row2, bg=self.input_bg, fg=self.fg_color, width=22)
        self.lon_entry.pack(side=tk.LEFT, padx=5)
        self.lon_entry.insert(0, "29.656312834259097")

        # ALAN
        area_frame = tk.LabelFrame(self.scrollable_frame, text="📐 Alan (metre)", bg=self.bg_color, fg=self.fg_color)
        area_frame.pack(fill=tk.X, pady=5, padx=8)
        
        area_row = tk.Frame(area_frame, bg=self.bg_color)
        area_row.pack(fill=tk.X, pady=2)
        tk.Label(area_row, text="Genişlik:", bg=self.bg_color, fg=self.fg_color, width=9, anchor='w').pack(side=tk.LEFT)
        self.width_entry = tk.Entry(area_row, bg=self.input_bg, fg=self.fg_color, width=10)
        self.width_entry.pack(side=tk.LEFT, padx=5)
        self.width_entry.insert(0, "400")
        tk.Label(area_row, text="Yükseklik:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=(10,0))
        self.height_entry = tk.Entry(area_row, bg=self.input_bg, fg=self.fg_color, width=10)
        self.height_entry.pack(side=tk.LEFT, padx=5)
        self.height_entry.insert(0, "400")

        # PARAMETRELER
        params_frame = tk.LabelFrame(self.scrollable_frame, text="⚙️ Parametreler", bg=self.bg_color, fg=self.fg_color)
        params_frame.pack(fill=tk.X, pady=5, padx=8)
        
        self.sigma_mode = tk.StringVar(value="auto")
        tk.Radiobutton(params_frame, text="🎯 Otomatik Sigma", variable=self.sigma_mode, value="auto",
                      bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color).pack(anchor=tk.W, padx=5, pady=2)
        
        self.threshold_auto_var = tk.BooleanVar(value=True)
        tk.Radiobutton(params_frame, text="🎯 Otomatik Anomali Eşiği", variable=self.threshold_auto_var, value=True,
                      bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color).pack(anchor=tk.W, padx=5, pady=2)
        
        self.threshold_var = tk.DoubleVar(value=5.0)
        self.threshold_slider = tk.Scale(params_frame, from_=0.5, to=20, orient=tk.HORIZONTAL,
                                         variable=self.threshold_var, bg=self.bg_color, length=250, resolution=0.5)
        self.threshold_slider.pack(pady=5, padx=5)
        self.threshold_slider.pack_forget()

        # FİLTRE
        filter_frame = tk.LabelFrame(self.scrollable_frame, text="🎛️ Filtre", bg=self.bg_color, fg=self.fg_color)
        filter_frame.pack(fill=tk.X, pady=5, padx=8)
        
        self.filter_var = tk.StringVar(value="Gaussian")
        filter_row = tk.Frame(filter_frame, bg=self.bg_color)
        filter_row.pack()
        for f in ["Gaussian", "Median", "Low-pass", "High-pass", "Yok"]:
            tk.Radiobutton(filter_row, text=f, variable=self.filter_var, value=f,
                          bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color,
                          command=self.apply_filter_and_update).pack(side=tk.LEFT, padx=3)

        # GÖRÜNÜM
        view_frame = tk.LabelFrame(self.scrollable_frame, text="🎨 Görünüm", bg=self.bg_color, fg=self.fg_color)
        view_frame.pack(fill=tk.X, pady=5, padx=8)
        
        color_row = tk.Frame(view_frame, bg=self.bg_color)
        color_row.pack(fill=tk.X, pady=2)
        tk.Label(color_row, text="Renk:", bg=self.bg_color, fg=self.fg_color, width=5, anchor='w').pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value="RdBu")
        colors = ["RdBu", "viridis", "plasma", "inferno", "magma", "coolwarm", "seismic", "jet"]
        self.color_combo = ttk.Combobox(color_row, textvariable=self.color_var, values=colors, state="readonly", width=12)
        self.color_combo.pack(side=tk.LEFT, padx=5)
        self.color_combo.bind("<<ComboboxSelected>>", lambda e: self.update_overlay())
        
        self.show_basemap_var = tk.BooleanVar(value=False)
        tk.Checkbutton(view_frame, text="🛰️ Uydu Haritası", variable=self.show_basemap_var,
                      bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color,
                      command=self.toggle_basemap).pack(anchor=tk.W, padx=5, pady=2)

        # İŞLEMLER
        btn_frame = tk.LabelFrame(self.scrollable_frame, text="🚀 İşlemler", bg=self.bg_color, fg=self.fg_color)
        btn_frame.pack(fill=tk.X, pady=10, padx=8)
        
        self.analyze_btn = tk.Button(btn_frame, text="🔍 ANALİZ BAŞLAT", bg=self.accent_color, fg="white",
                                     font=("Arial", 10, "bold"), command=self.start_analysis)
        self.analyze_btn.pack(fill=tk.X, pady=3)
        
        btn_row = tk.Frame(btn_frame, bg=self.bg_color)
        btn_row.pack(fill=tk.X, pady=3)
        
        self.harita_btn = tk.Button(btn_row, text="🗺️ HARİTA", bg="#17a2b8", fg="white",
                                    font=("Arial", 9), command=self.show_on_map)
        self.harita_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.surfer_btn = tk.Button(btn_row, text="💾 SURFER", bg="#6c757d", fg="white",
                                    font=("Arial", 9), command=self.export_surfer)
        self.surfer_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.kmz_btn = tk.Button(btn_row, text="🌍 KMZ", bg="#28a745", fg="white",
                                 font=("Arial", 9), command=self.export_kmz)
        self.kmz_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.excel_btn = tk.Button(btn_row, text="📊 EXCEL", bg="#ffc107", fg="black",
                                   font=("Arial", 9), command=self.export_excel)
        self.excel_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # SONUÇLAR
        result_frame = tk.LabelFrame(self.scrollable_frame, text="📊 Sonuçlar", bg=self.bg_color, fg=self.fg_color)
        result_frame.pack(fill=tk.X, pady=10, padx=8)
        
        self.result_text = tk.Text(result_frame, height=6, bg=self.input_bg, fg=self.fg_color, font=("Consolas", 8))
        self.result_text.pack(fill=tk.X, pady=5, padx=5)
        
        self.status_label = tk.Label(self.scrollable_frame, text="Hazır", bg=self.bg_color, fg="#6c757d", font=("Arial", 8))
        self.status_label.pack(pady=5)

        # ========== SAĞ PANEL (HARİTA) ==========
        self.figure = Figure(figsize=(10, 8), facecolor='#1e1e1e')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#2d2d2d')
        
        self.canvas_widget = FigureCanvasTkAgg(self.figure, master=right_panel)
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ax.text(0.5, 0.5, "Henüz analiz yapılmadı\nKoordinatları girip 'Analiz Başlat' butonuna tıklayın",
                    transform=self.ax.transAxes, ha='center', va='center', color='white', fontsize=12)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis('off')
        self.canvas_widget.draw()

    # ============================================================
    # YARDIMCI FONKSİYONLAR
    # ============================================================
    def get_basemap_image(self, lat, lon, zoom=14, size=400):
        try:
            url = f"https://staticmap.openstreetmap.de/staticmap.php?center={lat},{lon}&zoom={zoom}&size={size}x{size}&maptype=mapnik"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                img_data = response.read()
            img = Image.open(io.BytesIO(img_data))
            return img
        except Exception as e:
            print(f"⚠️ Harita yüklenemedi: {e}")
            return Image.new('RGB', (size, size), color='#2d2d2d')

    def toggle_basemap(self):
        if self.current_anomaly_data is not None:
            self.update_overlay()

    def calculate_auto_threshold(self):
        if self.current_anomaly_data is None:
            return 5.0
        data = self.current_anomaly_data.flatten()
        abs_data = np.abs(data)
        std_val = np.std(data)
        threshold_std = max(2.0, std_val * 1.5)
        percentiles = np.percentile(abs_data, [85, 90, 95])
        threshold_percentile = percentiles[1]
        max_val = np.max(abs_data)
        threshold_max = max_val * 0.2
        auto_threshold = np.mean([threshold_std, threshold_percentile, threshold_max])
        auto_threshold = max(1.0, min(15.0, auto_threshold))
        return auto_threshold

    def update_overlay(self):
        """Anomali haritasını güncelle"""
        if self.current_anomaly_data is None:
            return
        
        self.ax.clear()
        
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        width = float(self.width_entry.get())
        height = float(self.height_entry.get())
        
        self.ax.set_facecolor('#1a1a1a')
        extent = [0, width, 0, height]
        
        cmap = self.color_var.get()
        self.ax.imshow(self.current_anomaly_data, cmap=cmap, alpha=0.7,
                       extent=extent, origin='lower', interpolation='bilinear')
        
        threshold = self.calculate_auto_threshold() if self.threshold_auto_var.get() else self.threshold_var.get()
        levels = [-threshold, threshold]
        
        if np.max(np.abs(self.current_anomaly_data)) > threshold:
            contour = self.ax.contour(self.current_anomaly_data, levels=levels,
                                      colors='yellow', linewidths=1.5, alpha=0.9, extent=extent)
            self.ax.clabel(contour, fmt='%.1fm', colors='yellow', fontsize=8)
        
        self.ax.set_xlabel("Doğu-Batı (metre)", color='white')
        self.ax.set_ylabel("Kuzey-Güney (metre)", color='white')
        self.ax.set_title("Anomali Haritası", color='white')
        self.ax.tick_params(colors='white')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        
        self.canvas_widget.draw()

    def apply_filter_and_update(self):
        """Filtre seçildiğinde anında anomali haritasını güncelle"""
        if self.current_anomaly_data is None:
            return
        
        filter_type = self.filter_var.get()
        
        if filter_type == "Gaussian":
            from scipy.ndimage import gaussian_filter
            filtered = gaussian_filter(self.analyzer.residual, sigma=1)
        elif filter_type == "Median":
            from scipy.ndimage import median_filter
            filtered = median_filter(self.analyzer.residual, size=3)
        elif filter_type == "Low-pass":
            from scipy.ndimage import uniform_filter
            filtered = uniform_filter(self.analyzer.residual, size=3)
        elif filter_type == "High-pass":
            from scipy.ndimage import gaussian_filter
            lowpass = gaussian_filter(self.analyzer.residual, sigma=2)
            filtered = self.analyzer.residual - lowpass
        else:
            filtered = self.analyzer.residual
        
        self.analyzer.filtered = filtered
        self.current_anomaly_data = filtered
        self.update_overlay()
        
        threshold = self.calculate_auto_threshold() if self.threshold_auto_var.get() else self.threshold_var.get()
        stats = self.analyzer.get_statistics(threshold=threshold)
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Çöküntü: %{stats['neg_ratio']:.1f}  |  Yükselti: %{stats['pos_ratio']:.1f}\n")
        self.result_text.insert(tk.END, f"Min: {stats['min']:.1f}m  |  Max: {stats['max']:.1f}m\n")
        self.result_text.insert(tk.END, f"Std: {stats['std']:.1f}m  |  Filtre: {filter_type}")
        self.status_label.config(text=f"✅ Filtre: {filter_type}", fg="#28a745")

    # ============================================================
    # ANALİZ BAŞLAT
    # ============================================================
    def start_analysis(self):
        self.analyze_btn.config(state=tk.DISABLED, text="⏳ ANALİZ YAPILIYOR...")
        self.status_label.config(text="DEM indiriliyor...", fg="#ffc107")
        thread = threading.Thread(target=self._do_analysis)
        thread.start()

    def _do_analysis(self):
        try:
            lat = float(self.lat_entry.get())
            lon = float(self.lon_entry.get())
            width = float(self.width_entry.get())
            height = float(self.height_entry.get())

            sigma_mode = self.sigma_mode.get()
            filter_type = self.filter_var.get()

            self.master.after(0, lambda: self.status_label.config(text="DEM indiriliyor...", fg="#ffc107"))
            success, dem = download_dem_opentopo(lat, lon, width, height,
                                                 os.path.join(DOWNLOADS_DIR, "temp_gui.tif"))

            if not success or dem is None:
                self.master.after(0, lambda: messagebox.showerror("Hata", "DEM indirilemedi!"))
                self.master.after(0, self._reset_ui)
                return

            self.dem_data = dem
            self.analyzer.load_dem(dem)

            if sigma_mode == "auto":
                self.master.after(0, lambda: self.status_label.config(text="Otomatik sigma hesaplanıyor...", fg="#ffc107"))
                sigma = None
            else:
                sigma = 50

            trend = self.analyzer.calculate_trend(sigma=sigma)
            residual = self.analyzer.calculate_residual()

            self.master.after(0, lambda: self.status_label.config(text="Filtre uygulanıyor...", fg="#ffc107"))
            if filter_type != "Yok":
                self.analyzer.apply_filter(filter_type, sigma=2, size=3)
            else:
                self.analyzer.filtered = residual

            stats = self.analyzer.get_statistics(threshold=self.threshold_var.get())
            self.current_anomaly_data = self.analyzer.filtered

            self._save_and_export(stats, filter_type)

        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Hata", str(e)))
            self.master.after(0, self._reset_ui)

    def _save_and_export(self, stats, filter_type):
        """Verileri kaydet ve export işlemlerini yap"""
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        width = float(self.width_entry.get())
        height = float(self.height_entry.get())
        sigma = self.analyzer.last_sigma if hasattr(self.analyzer, 'last_sigma') else 50
        threshold = self.threshold_var.get()

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"ANALIZ SONUCLARI\n")
        self.result_text.insert(tk.END, f"{'=' * 30}\n")
        self.result_text.insert(tk.END, f"Koordinat: {lat:.6f}, {lon:.6f}\n")
        self.result_text.insert(tk.END, f"Alan: {width:.0f}m x {height:.0f}m\n")
        self.result_text.insert(tk.END, f"Sigma: {sigma:.0f}\n")
        self.result_text.insert(tk.END, f"Cokuntu anomalisi: %{stats['neg_ratio']:.2f}\n")
        self.result_text.insert(tk.END, f"Yukselti anomalisi: %{stats['pos_ratio']:.2f}\n")
        self.result_text.insert(tk.END, f"Maks cokuntu: {stats['min']:.2f} m\n")
        self.result_text.insert(tk.END, f"Maks yukselti: {stats['max']:.2f} m\n")
        self.result_text.insert(tk.END, f"Standart sapma: {stats['std']:.2f} m\n")
        self.result_text.insert(tk.END, f"Filtre: {filter_type}\n")
        self.result_text.insert(tk.END, f"Eşik: {threshold:.1f}m\n")

        params = {
            "width": width,
            "height": height,
            "sigma": sigma,
            "filter": filter_type,
            "threshold": threshold,
            "colormap": self.color_var.get()
        }

        output_paths = {
            "anomaly_map": os.path.join(OUTPUTS_DIR, f"anomali_{lat}_{lon}.png"),
            "surfer_xyz": os.path.join(OUTPUTS_DIR, f"anomali_{lat}_{lon}.xyz"),
            "surfer_grd": os.path.join(OUTPUTS_DIR, f"anomali_{lat}_{lon}.grd")
        }

        session_dir, session_name = self.file_manager.save_analysis(
            lat, lon, params, stats,
            self.analyzer.dem_data,
            self.analyzer.filtered,
            output_paths
        )

        self.status_label.config(text="Surfer dosyaları oluşturuluyor...", fg="#ffc107")
        self._auto_export_surfer(session_dir)

        self.status_label.config(text="KMZ dosyası oluşturuluyor...", fg="#ffc107")
        self._auto_export_kmz(session_dir)

        self.status_label.config(text="Excel dosyası oluşturuluyor...", fg="#ffc107")
        self._auto_export_excel(session_dir)

        self.status_label.config(text="WhiteboxTools analizleri yapılıyor...", fg="#ffc107")
        dem_file_path = os.path.join(DOWNLOADS_DIR, "temp_gui.tif")
        self._auto_export_whitebox(session_dir, dem_file_path)

        self.result_text.insert(tk.END, f"\n{'=' * 30}\n")
        self.result_text.insert(tk.END, f"💾 TUM DOSYALAR KAYDEDILDI\n")
        self.result_text.insert(tk.END, f"Klasor: {session_dir}\n")

        self.update_overlay()
        self.status_label.config(text=f"✅ Analiz tamamlandi! Tum dosyalar: {session_dir}", fg="#28a745")
        self._reset_ui()

    # ============================================================
    # OTOMATİK EXPORT FONKSİYONLARI
    # ============================================================
    def _auto_export_surfer(self, session_dir):
        if self.analyzer.filtered is None:
            return
        
        filtered = self.analyzer.filtered
        rows, cols = filtered.shape
        
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        width = float(self.width_entry.get())
        height = float(self.height_entry.get())
        
        lat_per_meter = 1 / 111320
        lon_per_meter = 1 / (111320 * np.cos(np.radians(lat)))
        
        min_lat = lat - (height / 2) * lat_per_meter
        max_lat = lat + (height / 2) * lat_per_meter
        min_lon = lon - (width / 2) * lon_per_meter
        max_lon = lon + (width / 2) * lon_per_meter
        
        xyz_path = os.path.join(session_dir, "anomali.xyz")
        with open(xyz_path, 'w', encoding='utf-8') as f:
            f.write("X,Y,Z\n")
            for i in range(rows):
                for j in range(cols):
                    x_deg = min_lon + (j + 0.5) * (width / cols) * lon_per_meter
                    y_deg = max_lat - (i + 0.5) * (height / rows) * lat_per_meter
                    z_val = filtered[i, j]
                    f.write(f"{x_deg:.8f},{y_deg:.8f},{z_val:.4f}\n")
        
        grd_path = os.path.join(session_dir, "anomali.grd")
        with open(grd_path, 'w') as f:
            f.write("DSAA\n")
            f.write(f"{cols} {rows}\n")
            f.write(f"{min_lon:.8f} {max_lon:.8f}\n")
            f.write(f"{min_lat:.8f} {max_lat:.8f}\n")
            f.write(f"{filtered.min():.4f} {filtered.max():.4f}\n")
            for i in range(rows):
                for j in range(cols):
                    f.write(f"{filtered[i, j]:.4f} ")
                f.write("\n")
        
        print(f"✅ Surfer dosyalari: {session_dir}")

    def _auto_export_kmz(self, session_dir):
        if self.analyzer.filtered is None:
            return
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        width = float(self.width_entry.get())
        height = float(self.height_entry.get())
        threshold = self.threshold_var.get()

        try:
            export_anomaly_to_kmz(self.analyzer.filtered, lat, lon, width, height, session_dir, threshold)
            print(f"✅ KMZ olusturuldu: {session_dir}")
        except Exception as e:
            print(f"❌ KMZ hatasi: {e}")

    def _auto_export_excel(self, session_dir):
        if self.analyzer.filtered is None:
            return
        
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        width = float(self.width_entry.get())
        height = float(self.height_entry.get())
        threshold = self.threshold_var.get()
        
        filtered = self.analyzer.filtered
        rows, cols = filtered.shape
        
        lat_per_meter = 1 / 111320
        lon_per_meter = 1 / (111320 * np.cos(np.radians(lat)))
        
        min_lat = lat - (height / 2) * lat_per_meter
        max_lat = lat + (height / 2) * lat_per_meter
        min_lon = lon - (width / 2) * lon_per_meter
        max_lon = lon + (width / 2) * lon_per_meter
        
        csv_path = os.path.join(session_dir, "anomali_verileri.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Enlem', 'Boylam', 'Z_Anomali(m)'])
            for i in range(rows):
                for j in range(cols):
                    anomaly_value = filtered[i, j]
                    point_lat = max_lat - (i + 0.5) * lat_per_meter * 30
                    point_lon = min_lon + (j + 0.5) * lon_per_meter * 30
                    writer.writerow([f"{point_lat:.8f}", f"{point_lon:.8f}", f'="{anomaly_value:.2f}"'])
        
        detay_path = os.path.join(session_dir, "detayli_veriler.csv")
        with open(detay_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Enlem', 'Boylam', 'Z_Anomali(m)', 'X_metre', 'Y_metre', 'Tip', 'Potansiyel'])
            for i in range(rows):
                for j in range(cols):
                    anomaly_value = filtered[i, j]
                    point_lat = max_lat - (i + 0.5) * lat_per_meter * 30
                    point_lon = min_lon + (j + 0.5) * lon_per_meter * 30
                    x_m = j * 30
                    y_m = i * 30
                    
                    tip = "COKUNTU" if anomaly_value < -threshold else ("YUKSELTI" if anomaly_value > threshold else "NORMAL")
                    abs_val = abs(anomaly_value)
                    potansiyel = "YUKSEK" if abs_val >= 20 else ("ORTA" if abs_val >= 10 else ("DUSUK" if abs_val >= 5 else "ONEMSIZ"))
                    
                    writer.writerow([f"{point_lat:.8f}", f"{point_lon:.8f}", f'="{anomaly_value:.2f}"',
                                     f"{x_m:.1f}", f"{y_m:.1f}", tip, potansiyel])
        
        summary_path = os.path.join(session_dir, "ozet_istatistik.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\nANOMALİ ANALİZ ÖZETİ\n" + "="*60 + "\n\n")
            f.write(f"Koordinat: {lat:.6f}, {lon:.6f}\n")
            f.write(f"Alan: {width:.0f}m x {height:.0f}m\n")
            f.write(f"Toplam nokta: {rows * cols}\n\n")
            
            neg_count = np.sum(filtered < -threshold)
            pos_count = np.sum(filtered > threshold)
            normal_count = rows * cols - neg_count - pos_count
            
            f.write("--- ANOMALİ DAĞILIMI ---\n")
            f.write(f"Cokuntu: {neg_count} nokta (%{neg_count/(rows*cols)*100:.1f})\n")
            f.write(f"Yukselti: {pos_count} nokta (%{pos_count/(rows*cols)*100:.1f})\n")
            f.write(f"Normal: {normal_count} nokta (%{normal_count/(rows*cols)*100:.1f})\n\n")
            
            f.write("--- EN BUYUK ANOMALİLER ---\n")
            sorted_neg = np.sort(filtered.flatten())
            f.write("En buyuk cokuntuler:\n")
            for val in sorted_neg[:10]:
                if val < -threshold:
                    f.write(f"  {val:.2f} m\n")
            
            sorted_pos = np.sort(filtered.flatten())[::-1]
            f.write("\nEn buyuk yukseltiler:\n")
            for val in sorted_pos[:10]:
                if val > threshold:
                    f.write(f"  {val:.2f} m\n")
        
        print(f"✅ Excel dosyalari: {session_dir}")

    def _auto_export_whitebox(self, session_dir, dem_path):
        try:
            import whitebox
            wbt = whitebox.WhiteboxTools()
            wbt.set_verbose_mode(False)
            
            print("📊 WhiteboxTools analizleri başlıyor...")
            
            if not os.path.exists(dem_path):
                print(f"⚠️ DEM dosyası bulunamadı: {dem_path}")
                return False
            
            slope_path = os.path.join(session_dir, "egim.tif")
            wbt.slope(dem_path, slope_path)
            print(f"  ✅ Eğim analizi: {slope_path}")
            
            hillshade_path = os.path.join(session_dir, "hillshade.tif")
            wbt.hillshade(dem_path, hillshade_path, azimuth=315, altitude=45)
            print(f"  ✅ Gölgelendirme: {hillshade_path}")
            
            aspect_path = os.path.join(session_dir, "baki.tif")
            wbt.aspect(dem_path, aspect_path)
            print(f"  ✅ Bakı analizi: {aspect_path}")
            
            print("✅ WhiteboxTools analizleri tamamlandı!")
            return True
            
        except ImportError:
            print("❌ WhiteboxTools kurulu değil! 'pip install whitebox' ile kurun.")
            return False
        except Exception as e:
            print(f"❌ WhiteboxTools hatası: {e}")
            return False

    # ============================================================
    # MANUEL EXPORT FONKSİYONLARI
    # ============================================================
    def export_surfer(self):
        if self.analyzer.filtered is None:
            messagebox.showwarning("Uyarı", "Önce analiz yapmalısınız!")
            return
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        session_name = self.file_manager.create_session_name(lat, lon)
        session_dir = os.path.join(OUTPUTS_DIR, "sessions", session_name)
        os.makedirs(session_dir, exist_ok=True)
        self._auto_export_surfer(session_dir)
        messagebox.showinfo("Başarılı", f"Surfer dosyaları kaydedildi:\n📁 {session_dir}")

    def export_kmz(self):
        if self.analyzer.filtered is None:
            messagebox.showwarning("Uyarı", "Önce analiz yapmalısınız!")
            return
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        width = float(self.width_entry.get())
        height = float(self.height_entry.get())
        threshold = self.threshold_var.get()
        session_name = self.file_manager.create_session_name(lat, lon)
        session_dir = os.path.join(OUTPUTS_DIR, "sessions", session_name)
        os.makedirs(session_dir, exist_ok=True)
        try:
            export_anomaly_to_kmz(self.analyzer.filtered, lat, lon, width, height, session_dir, threshold)
            messagebox.showinfo("Başarılı", f"KMZ dosyası oluşturuldu!\n📁 {session_dir}")
        except Exception as e:
            messagebox.showerror("Hata", f"KMZ hatasi: {e}")

    def export_excel(self):
        if self.analyzer.filtered is None:
            messagebox.showwarning("Uyarı", "Önce analiz yapmalısınız!")
            return
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        session_name = self.file_manager.create_session_name(lat, lon)
        session_dir = os.path.join(OUTPUTS_DIR, "sessions", session_name)
        os.makedirs(session_dir, exist_ok=True)
        self._auto_export_excel(session_dir)
        messagebox.showinfo("Başarılı", f"Excel dosyası oluşturuldu!\n📁 {session_dir}")

    def _reset_ui(self):
        self.analyze_btn.config(state=tk.NORMAL, text="🔍 ANALİZ BAŞLAT")

    def show_on_map(self):
        if self.current_anomaly_data is None:
            messagebox.showwarning("Uyarı", "Önce analiz yapmalısınız!")
            return
        
        import json
        from scipy.ndimage import label
        from skimage.measure import find_contours
        
        lat = float(self.lat_entry.get())
        lon = float(self.lon_entry.get())
        width = float(self.width_entry.get())
        height = float(self.height_entry.get())
        threshold = self.threshold_var.get()
        
        lat_per_meter = 1 / 111320
        lon_per_meter = 1 / (111320 * np.cos(np.radians(lat)))
        
        min_lat = lat - (height / 2) * lat_per_meter
        max_lat = lat + (height / 2) * lat_per_meter
        min_lon = lon - (width / 2) * lon_per_meter
        max_lon = lon + (width / 2) * lon_per_meter
        
        rows, cols = self.current_anomaly_data.shape
        
        neg_mask = self.current_anomaly_data < -threshold
        pos_mask = self.current_anomaly_data > threshold
        
        neg_labels, neg_count = label(neg_mask)
        pos_labels, pos_count = label(pos_mask)
        
        heat_points = []
        step = max(1, min(rows, cols) // 15)
        for i in range(0, rows, step):
            for j in range(0, cols, step):
                anomaly = self.current_anomaly_data[i, j]
                point_lat = max_lat - (i + 0.5) * lat_per_meter * (width / cols)
                point_lon = min_lon + (j + 0.5) * lon_per_meter * (height / rows)
                intensity = min(1.0, float(abs(anomaly)) / 50.0)
                heat_points.append([float(point_lat), float(point_lon), intensity])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Anomali Bölgeleri</title>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js"></script>
            <style>
                #map {{ height: 100vh; width: 100%; }}
                .info {{ background: rgba(0,0,0,0.8); padding: 10px; border-radius: 8px; color: white; position: absolute; top: 10px; right: 10px; z-index: 1000; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <div class="info">
                <b>🔍 ANOMALİ ANALİZİ</b><br>
                Çöküntü: {neg_count} bölge | Yükselti: {pos_count} bölge<br>
                Eşik: ±{threshold}m
            </div>
            <script>
                var map = L.map('map').setView([{lat}, {lon}], 14);
                L.tileLayer('http://{{s}}.google.com/vt/lyrs=s&x={{x}}&y={{y}}&z={{z}}', {{
                    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
                    attribution: '&copy; Google Earth'
                }}).addTo(map);
                
                var heatData = {json.dumps(heat_points)};
                L.heatLayer(heatData, {{radius: 20, blur: 15, minOpacity: 0.3}}).addTo(map);
                
                var bounds = [[{min_lat}, {min_lon}], [{max_lat}, {max_lon}]];
                L.rectangle(bounds, {{color: "#ffffff", weight: 2, fill: false, dashArray: '5, 5'}}).addTo(map);
            </script>
        </body>
        </html>
        """
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
        
        webbrowser.open(temp_path)
        self.status_label.config(text=f"🗺️ Harita açıldı ({neg_count} çöküntü, {pos_count} yükselti)", fg="#28a745")


def main():
    root = tk.Tk()
    app = DEMApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()