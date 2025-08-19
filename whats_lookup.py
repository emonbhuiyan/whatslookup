import os
import re
import base64
import requests
from dotenv import load_dotenv
from colorama import init, Fore, Style
init()  # Inicializa colorama (necesario para Windows)

# Cargar variables desde .env
load_dotenv()

API_URL = "https://whatsapp-osint.p.rapidapi.com/wspic/b64"
API_HOST = "whatsapp-osint.p.rapidapi.com"

def show_banner():
    print(Fore.GREEN + """
⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣤⣶⣶⣶⣶⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀
⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀
⠀⢀⣾⣿⣿⣿⣿⡿⠟⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀
⠀⣾⣿⣿⣿⣿⡟⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀
⢠⣿⣿⣿⣿⣿⣧⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄
⢸⣿⣿⣿⣿⣿⣿⣦⠀⠀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⠘⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠈⠻⢿⣿⠟⠉⠛⠿⣿⣿⣿⣿⣿⣿⠃
⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⡀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⡿⠀
⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣤⣤⣴⣾⣿⣿⣿⣿⡿⠁⠀
⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠀⠀⠀
⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠁⠀⠀⠀⠀
⠠⠛⠛⠛⠉⠁⠀⠈⠙⠛⠛⠿⠿⠿⠿⠛⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀
""" + Style.RESET_ALL)
    print(Fore.GREEN + "📸" * 15 + Style.RESET_ALL)
    print("\n" + Style.BRIGHT + Fore.GREEN + "WhatsApp Profile Picture Tool" + Style.RESET_ALL + "\n")

def sanitize_phone(raw: str) -> str:
    return re.sub(r"[^\d]", "", raw)

def is_valid_phone(p: str) -> bool:
    return p.isdigit() and 8 <= len(p) <= 15

def fetch(phone: str, api_key: str):
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": API_HOST}
    return requests.get(API_URL, headers=headers, params={"phone": phone}, timeout=30)

def save_b64(b64_str: str, path: str) -> bool:
    try:
        img = base64.b64decode(b64_str, validate=True)
        with open(path, "wb") as f:
            f.write(img)
        return True
    except Exception:
        return False

def main():
    show_banner()
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("❌ No se encontró RAPIDAPI_KEY en .env")
        return

    phone = input("Introduce el número (con código de país, sin '+', p.ej. 51916574069): ").strip()
    phone = sanitize_phone(phone)

    if not is_valid_phone(phone):
        print("❌ Formato no válido. Ejemplo: 51916574069")
        return

    try:
        resp = fetch(phone, api_key)
    except requests.RequestException as e:
        print("❌ Error de red:", e)
        return

    print("HTTP:", resp.status_code)
    ctype = resp.headers.get("Content-Type", "")

    if resp.status_code != 200:
        print("❌ Error del servidor:", resp.text.strip())
        return

    body = resp.text.strip()

    if "application/json" in ctype.lower():
        try:
            data = resp.json()
        except Exception:
            print("❌ No se pudo leer JSON. Cuerpo:\n", body)
            return
        b64 = data.get("data") or data.get("image") or data.get("base64")
        if not b64:
            print("ℹ️ Sin campo base64 en la respuesta:", data)
            return
        fname = f"whatsapp_{phone}.jpg"
        if save_b64(b64, fname):
            print(f"✅ Imagen guardada como {fname}")
        else:
            print("❌ Base64 inválido.")
    else:
        lo = body.lower()
        if "no profile picture" in lo or "does not have a profile picture" in lo:
            print("ℹ️ Ese usuario no tiene foto de perfil (o está oculta).")
        else:
            fname = f"whatsapp_{phone}.jpg"
            if save_b64(body, fname):
                print(f"✅ Imagen guardada como {fname}")
            else:
                print(f"ℹ️ Respuesta en texto:\n{body}")

if __name__ == "__main__":
    main()
