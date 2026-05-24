import requests
import os
from .api_settings import OPENTOPOGRAPHY_KEY

def download_topography_data(min_lat, max_lat, min_lon, max_lon, output_filename="arazi_verisi.tif"):
    """
    OpenTopography API kullanarak SRTM verisi indirir.
    """
    url = f"https://portal.opentopography.org/API/globaldem"
    params = {
        "demtype": "SRTMGL1",
        "south": min_lat,
        "north": max_lat,
        "west": min_lon,
        "east": max_lon,
        "outputFormat": "GTiff",
        "API_Key": "a92da5448c6a4a5f1dc6a857e8e9f2f7"
    }

    print(f"Veri indiriliyor: {min_lat}, {min_lon} bölgesi...")
    
    response = requests.get(url, params=params, stream=True)
    
    if response.status_code == 200:
        # 07_Output_Forge klasörüne kaydet
        output_path = os.path.join("07_Output_Forge", output_filename)
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Başarılı! Veri kaydedildi: {output_path}")
        return output_path
    else:
        print(f"Hata oluştu! Kod: {response.status_code}, Mesaj: {response.text}")
        return None