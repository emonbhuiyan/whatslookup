import os
import re
import base64
import requests
import json
import time
from dotenv import load_dotenv
from colorama import init, Fore, Style
init()  # Initialize colorama (needed for Windows)

# Load variables from .env
load_dotenv()

# API URLs
API_URL = "https://whatsapp-osint.p.rapidapi.com/wspic/b64"
API_HOST = "whatsapp-osint.p.rapidapi.com"

# Available endpoints
ENDPOINTS = {
    "1": {"name": "Profile picture", "url": "/wspic/b64", "method": "GET"},
    "2": {"name": "User status", "url": "/about", "method": "GET"},
    "3": {"name": "Business verification", "url": "/bizos", "method": "POST"},
    "4": {"name": "Device information", "url": "/devices", "method": "GET"},
    "5": {"name": "Full OSINT information", "url": "/wspic/dck", "method": "GET"},
    "6": {"name": "Privacy settings", "url": "/privacy", "method": "GET"}
}

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
    print(Fore.GREEN + "🔍" * 15 + Style.RESET_ALL)
    print("\n" + Style.BRIGHT + Fore.GREEN + "WhatsApp OSINT Tool" + Style.RESET_ALL + "\n")

def sanitize_phone(raw: str) -> str:
    return re.sub(r"[^\d]", "", raw)

def is_valid_phone(p: str) -> bool:
    return p.isdigit() and 8 <= len(p) <= 15

def show_menu():
    print(Fore.CYAN + "🔍 Select the type of query:" + Style.RESET_ALL)
    print()
    for key, endpoint in ENDPOINTS.items():
        print(f"  {Fore.YELLOW}{key}.{Style.RESET_ALL} {endpoint['name']}")
    print()

def fetch_endpoint(phone: str, api_key: str, endpoint: str, method: str = "GET"):
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": API_HOST}
    url = "https://whatsapp-osint.p.rapidapi.com" + endpoint
    
    try:
        if method == "GET":
            return requests.get(url, headers=headers, params={"phone": phone}, timeout=30)
        elif method == "POST":
            return requests.post(url, headers=headers, data=phone, timeout=30)
    except requests.RequestException as e:
        raise e

def fetch(phone: str, api_key: str):
    """Original repository function"""
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": API_HOST}
    url = API_URL + "?phone=" + phone
    try:
        return requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        raise e

def save_b64(b64_str: str, path: str) -> bool:
    try:
        img = base64.b64decode(b64_str, validate=True)
        with open(path, "wb") as f:
            f.write(img)
        return True
    except Exception:
        return False

def process_profile_picture(phone: str, api_key: str):
    """Process profile picture (original endpoint)"""
    try:
        resp = fetch_endpoint(phone, api_key, "/wspic/b64", "GET")
    except requests.RequestException as e:
        print("❌ Network error:", e)
        return

    print("HTTP:", resp.status_code)
    ctype = resp.headers.get("Content-Type", "")

    if resp.status_code != 200:
        print("❌ Server error:", resp.text.strip())
        return

    body = resp.text.strip()

    if "application/json" in ctype.lower():
        try:
            data = resp.json()
        except Exception:
            print("❌ Could not read JSON. Body:\n", body)
            return
        b64 = data.get("data") or data.get("image") or data.get("base64")
        if not b64:
            print("ℹ️ No base64 field in response:", data)
            return
        fname = f"whatsapp_{phone}.jpg"
        if save_b64(b64, fname):
            print(f"✅ Image saved as {fname}")
        else:
            print("❌ Invalid Base64.")
    else:
        lo = body.lower()
        if "no profile picture" in lo or "does not have a profile picture" in lo:
            print("ℹ️ That user has no profile picture (or it's hidden).")
        else:
            fname = f"whatsapp_{phone}.jpg"
            if save_b64(body, fname):
                print(f"✅ Image saved as {fname}")
            else:
                print(f"ℹ️ Text response:\n{body}")

def process_user_status(phone: str, api_key: str):
    """Process user status"""
    try:
        resp = fetch_endpoint(phone, api_key, "/about", "GET")
    except requests.RequestException as e:
        print("❌ Network error:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Server error:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n📊 {Fore.CYAN}User status:{Style.RESET_ALL}")
        print(f"   📱 Number: {phone}")
        
        if "about" in data:
            if data['about'] and data['about'].strip():
                print(f"   📝 Status: {data['about']}")
            else:
                print(f"   📝 Status: No custom status")
        elif "status" in data:
            print(f"   📝 Status: {data['status']}")
        if "last_seen" in data:
            print(f"   🕒 Last seen: {data['last_seen']}")
        if "is_online" in data:
            status = "🟢 Online" if data['is_online'] else "🔴 Offline"
            print(f"   {status}")
            
    except Exception:
        print("ℹ️ Text response:", resp.text.strip())

def process_business_verification(phone: str, api_key: str):
    """Process business verification"""
    try:
        # The /bizos endpoint requires JSON in the body
        headers = {
            "x-rapidapi-key": api_key, 
            "x-rapidapi-host": API_HOST,
            "Content-Type": "application/json"
        }
        url = "https://whatsapp-osint.p.rapidapi.com/bizos"
        data = {"phone": phone}
        resp = requests.post(url, headers=headers, json=data, timeout=30)
    except requests.RequestException as e:
        print("❌ Network error:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Server error:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n🏢 {Fore.CYAN}WhatsApp Business Verification:{Style.RESET_ALL}")
        print(f"   📱 Number: {phone}")
        
        # The response is an array with one object
        if isinstance(data, list) and len(data) > 0:
            business_data = data[0]
            
            if "isBusiness" in business_data:
                is_biz = business_data['isBusiness']
                if is_biz and is_biz != "false" and "Not a Business Account" not in str(is_biz) and "Not Registered" not in str(is_biz):
                    print(f"   ✅ Is a WhatsApp Business account: {is_biz}")
                elif "Not a Business Account" in str(is_biz):
                    print(f"   ❌ Not a WhatsApp Business account (it's a personal account)")
                elif "Not Registered" in str(is_biz):
                    print(f"   ❌ Not registered on WhatsApp")
                else:
                    print(f"   ❌ Not a WhatsApp Business account")
                    
            if "verifiedName" in business_data and business_data['verifiedName']:
                print(f"   🏪 Verified Name: {business_data['verifiedName']}")
                
            if "query" in business_data:
                print(f"   🔍 Query: {business_data['query']}")
        else:
            print("   ℹ️ No business information found")
            
    except Exception:
        print("ℹ️ Text response:", resp.text.strip())

def process_device_info(phone: str, api_key: str):
    """Process device information"""
    try:
        resp = fetch_endpoint(phone, api_key, "/devices", "GET")
    except requests.RequestException as e:
        print("❌ Network error:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Server error:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n📱 {Fore.CYAN}Device Information:{Style.RESET_ALL}")
        print(f"   📞 Number: {phone}")
        
        if "devices" in data:
            if isinstance(data['devices'], list) and data['devices']:
                print(f"   🔢 Total devices: {len(data['devices'])}")
                for i, device in enumerate(data['devices'], 1):
                    print(f"\n   📱 Device {i}:")
                    if "device_type" in device:
                        print(f"     🖥️  Type: {device['device_type']}")
                    if "os" in device:
                        print(f"     💻 OS: {device['os']}")
                    if "last_seen" in device:
                        print(f"     🕒 Last seen: {device['last_seen']}")
                    if "status" in device:
                        status = "🟢 Online" if device['status'] == "online" else "🔴 Offline"
                        print(f"     {status}")
            elif isinstance(data['devices'], int):
                print(f"   🔢 Total devices: {data['devices']}")
            else:
                print("   ℹ️ No device information found")
        if "message" in data:
            print(f"   ℹ️ {data['message']}")
        if "devices" not in data and "message" not in data:
            print("   ℹ️ No device information found")
            
    except Exception:
        print("ℹ️ Text response:", resp.text.strip())

def process_osint_info(phone: str, api_key: str):
    """Process full OSINT information"""
    try:
        resp = fetch_endpoint(phone, api_key, "/wspic/dck", "GET")
    except requests.RequestException as e:
        print("❌ Network error:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Server error:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n🔍 {Fore.CYAN}Full OSINT Information:{Style.RESET_ALL}")
        print(f"   📱 Number: {phone}")
        
        if "verification_status" in data:
            print(f"   ✅ Verification: {data['verification_status']}")
        if "last_seen" in data:
            print(f"   🕒 Last seen: {data['last_seen']}")
        if "profile_info" in data:
            print(f"   👤 Profile information available")
        if "osint_data" in data:
            print(f"   📊 Additional OSINT data available")
            
        print(f"\n📄 {Fore.YELLOW}Full data:{Style.RESET_ALL}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
            
    except Exception:
        print("ℹ️ Text response:", resp.text.strip())

def process_privacy_settings(phone: str, api_key: str):
    """Process privacy settings"""
    try:
        resp = fetch_endpoint(phone, api_key, "/privacy", "GET")
    except requests.RequestException as e:
        print("❌ Network error:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Server error:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n🔒 {Fore.CYAN}Privacy Settings:{Style.RESET_ALL}")
        print(f"   📱 Number: {phone}")
        
        if "privacy" in data:
            print(f"   🔒 Privacy settings: {data['privacy']}")
        elif "profile_visibility" in data:
            print(f"   👤 Profile visibility: {data['profile_visibility']}")
        if "last_seen" in data:
            print(f"   🕒 Last seen: {data['last_seen']}")
        if "read_receipts" in data:
            receipts = "✅ Enabled" if data['read_receipts'] else "❌ Disabled"
            print(f"   📨 Read receipts: {receipts}")
        if "status_visibility" in data:
            print(f"   📝 Status visibility: {data['status_visibility']}")
        if "profile_picture" in data:
            print(f"   🖼️  Photo visibility: {data['profile_picture']}")
            
    except Exception:
        print("ℹ️ Text response:", resp.text.strip())


def main():
    show_banner()
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("❌ RAPIDAPI_KEY not found in .env")
        return

    # Show menu
    show_menu()
    
    # Select option
    while True:
        choice = input(f"{Fore.CYAN}Select an option (1-6): {Style.RESET_ALL}").strip()
        if choice in ENDPOINTS:
            break
        print("❌ Invalid option. Select a number from 1 to 6.")

    # Get phone number
    phone = input("Enter the number (with country code, without '+', e.g. 51916574069): ").strip()
    phone = sanitize_phone(phone)

    if not is_valid_phone(phone):
        print("❌ Invalid format. Example: 51916574069")
        return

    print(f"\n🔍 {Fore.GREEN}Processing query...{Style.RESET_ALL}")
    print(f"📱 Number: {phone}")
    print(f"🎯 Query: {ENDPOINTS[choice]['name']}")
    print()

    # Process according to selected option
    if choice == "1":
        process_profile_picture(phone, api_key)
    elif choice == "2":
        process_user_status(phone, api_key)
    elif choice == "3":
        process_business_verification(phone, api_key)
    elif choice == "4":
        process_device_info(phone, api_key)
    elif choice == "5":
        process_osint_info(phone, api_key)
    elif choice == "6":
        process_privacy_settings(phone, api_key)

    print(f"\n✅ {Fore.GREEN}Query completed.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
