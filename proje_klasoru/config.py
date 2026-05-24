# config.py
import os

# Klasör yapısı
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Klasörleri oluştur
for dir_path in [DOWNLOADS_DIR, OUTPUTS_DIR, LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Analiz parametreleri
DEFAULT_SIGMA = 15  # Gaussian filtre sigma değeri
DEFAULT_MEDIAN_SIZE = 3  # Medyan filtre boyutu

# Hata loglama
LOG_FILE = os.path.join(LOGS_DIR, "hata_logu.txt")