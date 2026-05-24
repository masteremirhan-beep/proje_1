# test_api.py
import urllib.request
import urllib.parse

API_KEY = "a92da5448c6a4a5f1dc6a857e8e9f2f7"  # Buraya yazın

url = "https://portal.opentopography.org/API/globaldem?demtype=SRTMGL1&south=40&north=41&west=29&east=30&outputFormat=GTiff&API_Key=" + API_KEY

try:
    print("API test ediliyor...")
    response = urllib.request.urlopen(url)
    print(f"✓ Başarılı! HTTP Kodu: {response.getcode()}")
except Exception as e:
    print(f"✗ Hata: {e}")