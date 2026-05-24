# surfer_exporter.py
import numpy as np
import os
from config import OUTPUTS_DIR

def export_to_surfer(data, transform, output_path_xyz, output_path_grd):
    """
    Anomali verisini Surfer uyumlu XYZ ve GRD formatında dışa aktar
    
    Args:
        data: 2D numpy array (anomali verisi)
        transform: rasterio transform objesi (konum bilgisi)
        output_path_xyz: XYZ dosya yolu
        output_path_grd: GRD dosya yolu
    """
    try:
        rows, cols = data.shape
        
        # XYZ export (Surfer'in en sevdiği format)
        with open(output_path_xyz, 'w') as f:
            f.write("X Y Z\n")
            for i in range(rows):
                for j in range(cols):
                    # Basit koordinat sistemi (metre bazlı)
                    x = j * 30  # 30 metre çözünürlük varsayımı
                    y = i * 30
                    z = data[i, j]
                    f.write(f"{x:.2f} {y:.2f} {z:.4f}\n")
        
        # GRD export (Surfer Grid formatı - basit versiyon)
        with open(output_path_grd, 'w') as f:
            f.write("DSAA\n")  # Surfer ASCII Grid formatı
            f.write(f"{cols} {rows}\n")
            f.write(f"0 {cols*30:.2f}\n")
            f.write(f"0 {rows*30:.2f}\n")
            f.write(f"{data.min():.4f} {data.max():.4f}\n")
            
            # Veriyi yaz
            for i in range(rows):
                for j in range(cols):
                    f.write(f"{data[i, j]:.4f} ")
                f.write("\n")
        
        print(f"✓ Surfer dosyaları oluşturuldu:")
        print(f"  - XYZ: {output_path_xyz}")
        print(f"  - GRD: {output_path_grd}")
        return True
        
    except Exception as e:
        print(f"✗ Surfer export hatası: {e}")
        return False

def export_simple_xyz(data, output_path):
    """Sadece XYZ formatında export (minimal)"""
    try:
        rows, cols = data.shape
        with open(output_path, 'w') as f:
            for i in range(rows):
                for j in range(cols):
                    f.write(f"{j*30} {i*30} {data[i,j]:.4f}\n")
        print(f"✓ XYZ dosyası oluşturuldu: {output_path}")
        return True
    except Exception as e:
        print(f"✗ XYZ export hatası: {e}")
        return False