import os
import requests
from colorama import Fore, Style, init
import traceback

init(autoreset=True)

ascii_art = r"""
 __    __     ______     _____     ______     __            ______     ______     ______   ______   ______     ______    
/\ "-./  \   /\  __ \   /\  __-.  /\  ___\   /\ \          /\  == \   /\  __ \   /\__  _\ /\__  _\ /\  ___\   /\  == \   
\ \ \-./\ \  \ \ \/\ \  \ \ \/\ \ \ \  __\   \ \ \____     \ \  __<   \ \ \/\ \  \/_/\ \/ \/_/\ \/ \ \  __\   \ \  __<   
 \ \_\ \ \_\  \ \_____\  \ \____-  \ \_____\  \ \_____\     \ \_____\  \ \_____\    \ \_\    \ \_\  \ \_____\  \ \_\ \_\ 
  \/_/  \/_/   \/_____/   \/____/   \/_____/   \/_____/      \/_____/   \/_____/     \/_/     \/_/   \/_____/   \/_/ /_/ 
"""
print(Fore.LIGHTYELLOW_EX + ascii_art + "\n> Created by breadbars on youtube")

token = "https://auth.roproxy.com/v2/logout"
auth = "https://users.roproxy.com/v1/users/authenticated"
buy = "https://apis.roproxy.com/marketplace-fiat-service/v1/product/purchase"
like = "https://apis.roproxy.com/voting-api/vote/asset/{asset_id}?vote=true"

script_dir = os.path.dirname(os.path.abspath(__file__))
cookies_file_path = os.path.join(script_dir, "cookies.txt")

asset_id = input(Fore.LIGHTBLUE_EX + "[+] Enter Model ID: ")
use_cookies_file = input(Fore.LIGHTBLUE_EX + "[+] Use cookies.txt? (yes/no): ").strip().lower()

if use_cookies_file == "yes":
    if not os.path.exists(cookies_file_path):
        print(f"{cookies_file_path} not found!")
        input(Fore.RED + "Press Enter to exit...")
        exit()
    with open(cookies_file_path, "r") as file:
        cookies = file.read().splitlines()
else:
    manual_cookie = input(Fore.LIGHTBLUE_EX + "[+] Enter Roblox Cookie: ").strip()
    if not manual_cookie:
        print("No cookie provided!")
        input(Fore.RED + "Press Enter to exit...")
        exit()
    cookies = [manual_cookie]

for i, roblosecurity_cookie in enumerate(cookies):
    if not roblosecurity_cookie.strip():
        continue

    print(f"\n----------\nProcessing cookie {i + 1}...")

    try:
        headers = {
            "Content-Type": "application/json",
            "Cookie": ".ROBLOSECURITY=" + roblosecurity_cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.0 (Edition Campaign 34)",
        }

        response = requests.post(token, headers=headers, timeout=30)

        if response.status_code == 403 and "X-CSRF-TOKEN" in response.headers:
            csrf_token = response.headers["X-CSRF-TOKEN"]
            print(Fore.BLUE + f"[+] {response.status_code} | X-CSRF-TOKEN: {csrf_token}")
        else:
            print(Fore.RED + f"[-] {response.status_code} | Failed to fetch X-CSRF-TOKEN.")
            print(response.text)
            continue

        headers["X-CSRF-TOKEN"] = csrf_token

        response = requests.get(auth, headers=headers, timeout=30)

        if response.status_code == 200:
            user_info = response.json()
            user_id = user_info.get("id")
            username = user_info.get("name")
        else:
            print(Fore.RED + f"[-] {response.status_code} | Failed to fetch user information.")
            print(response.text)
            continue

        # Purchase the model
        data = {
            "expectedPrice": {
                "currencyCode": "USD",
                "quantity": {
                    "significand": 0,
                    "exponent": 0
                }
            },
            "productKey": {
                "productNamespace": "PRODUCT_NAMESPACE_CREATOR_MARKETPLACE_ASSET",
                "productType": "PRODUCT_TYPE_MODEL",
                "productTargetId": asset_id
            }
        }

        response = requests.post(buy, json=data, headers=headers, timeout=30)

        if response.status_code == 200:
            print(Fore.GREEN + f"[+] {username} | Purchase Success. | {response.status_code}")
        else:
            print(Fore.RED + f"[-] {response.status_code} | Purchase failed.")
            print(response.text)
            continue

        response = requests.post(like.format(asset_id=asset_id), headers=headers, timeout=30)

        if response.status_code == 200:
            print(Fore.GREEN + f"[+] {username} | Voting Success. | {response.status_code}")
        else:
            print(Fore.RED + f"[-] {response.status_code} | Voting failed.")
            print(response.text)
            continue

    except Exception as e:
        print(Fore.RED + "An error occurred:")
        print(Fore.YELLOW + traceback.format_exc())

print("----------\nFinished processing all cookies.")
input(Fore.LIGHTCYAN_EX + "\nPress Enter to exit...")
