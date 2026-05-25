import os
import glob
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

def show_3d_topography():
    # 1. En son indirilen tif dosyasını bul
    tif_folder = "07_Output_Forge"
    list_of_files = glob.glob(os.path.join(tif_folder, "*.tif"))
    
    if not list_of_files:
        print("HATA: Gösterilecek .tif dosyası bulunamadı!")
        return

    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Görselleştiriliyor: {latest_file}")

    # 2. Veriyi Oku
    with rasterio.open(latest_file) as src:
        elevation = src.read(1)
        # Hatalı verileri (negatifleri) temizle
        elevation = np.where(elevation < -100, 0, elevation)

    # 3. 3D Görselleştirme Ayarları
    x = np.linspace(0, elevation.shape[1], elevation.shape[1])
    y = np.linspace(0, elevation.shape[0], elevation.shape[0])
    X, Y = np.meshgrid(x, y)

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(12, 8))
    
    # Işıklandırma efekti (Daha gerçekçi görünüm için)
    ls = LightSource(azdeg=315, altdeg=45)
    rgb = ls.shade(elevation, cmap=plt.cm.terrain, vert_exag=0.1, blend_mode='soft')

    surf = ax.plot_surface(X, Y, elevation, facecolors=rgb,
                           linewidth=0, antialiased=True, shade=False)

    ax.set_title(f"3D Arazi Analizi: {os.path.basename(latest_file)}")
    plt.show(block=False) 
    plt.pause(0.1)