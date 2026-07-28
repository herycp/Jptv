import random
import string
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

def generate_credentials(length=8):
    """
    Menghasilkan credential yang benar-benar acak tanpa pola khusus.
    Kombinasi campuran huruf kecil, huruf besar, dan angka secara acak.
    """
    characters = string.ascii_letters + string.digits
    credential = ''.join(random.choices(characters, k=length))
    return credential

def check_xtreme_expired(server_host, username, password):
    api_url = f"{server_host.rstrip('/')}/player_api.php"
    params = {"username": username, "password": password}
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            user_info = data.get("user_info", {})
            exp_date_raw = user_info.get("exp_date")
            status = user_info.get("status", "Unknown")
            
            if exp_date_raw:
                try:
                    exp_timestamp = int(exp_date_raw)
                    formatted_date = datetime.fromtimestamp(exp_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    iso_date = datetime.fromtimestamp(exp_timestamp).isoformat()
                except (ValueError, TypeError):
                    formatted_date = str(exp_date_raw)
                    iso_date = str(exp_date_raw)
            else:
                formatted_date = "Unlimited"
                iso_date = "2099-12-31T23:59:59"
                
            return formatted_date, iso_date, status
        else:
            return f"Gagal API (HTTP {response.status_code})", "2099-12-31T23:59:59", "Unknown"
            
    except Exception as e:
        return f"Error: {e}", "2099-12-31T23:59:59", "Error"

def update_json_file(username, password, exp_date_str, exp_date_iso, status, filename="accounts.json"):
    data = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
            
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    new_entry = {
        "username": username,
        "password": password,
        "created_at": now,
        "exp_date": exp_date_str,
        "exp_date_iso": exp_date_iso,
        "status": status
    }
    
    # Masukkan data terbaru di urutan paling atas
    data.insert(0, new_entry)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Data berhasil ditambahkan dan disimpan ke {filename}")

def register_account():
    # Menghasilkan username & password yang identik tanpa pola tertebak
    credential = generate_credentials(length=8)
    username = credential
    password = credential

    session = requests.Session()
    register_url = "https://webtv.jpanttv.com/register.php" 
    xtreme_server = "http://184.174.96.206:8080"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Origin": "https://webtv.jpanttv.com",
        "Referer": register_url
    }

    try:
        response = session.get(register_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        payload = {
            "username": username,
            "password": password,
            "confirm_password": password
        }
        
        csrf_token = soup.find('input', {'name': 'csrf_token'}) or soup.find('input', {'name': 'token'})
        if csrf_token:
            payload[csrf_token['name']] = csrf_token['value']

        post_response = session.post(register_url, data=payload, headers=headers)
        
        if post_response.status_code == 200:
            exp_date_str, exp_date_iso, status = check_xtreme_expired(xtreme_server, username, password)
            
            print("========================================")
            print("Sukses mendaftar dengan:")
            print(f"Username : {username}")
            print(f"Password : {password}")
            print(f"Status   : {status}")
            print(f"Expired  : {exp_date_str}")
            print("========================================")
            
            update_json_file(username, password, exp_date_str, exp_date_iso, status)
        else:
            print(f"Gagal mengirim data pendaftaran. Status Code: {post_response.status_code}")

    except Exception as e:
        print(f"Terjadi kesalahan saat koneksi: {e}")

if __name__ == "__main__":
    register_account()
