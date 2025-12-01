import requests
import threading
from colorama import init, Fore
import time

init(autoreset=True)  # لتفعيل الألوان في الكونسل

API_BASE = "https://discord.com/api/v9"

def get_input(prompt):
    return input(prompt).strip()

def nuke_tool():
    print("\n=== Discord Server Tool (BOT) ===")
    token = get_input("Enter your BOT token: ")
    guild_id = get_input("Enter your server (guild) ID: ")

    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

    def threaded_action(items, func):
        threads = []
        for item in items:
            t = threading.Thread(target=func, args=(item,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    # ------------------ الميزات ------------------

    # 1) Create Channels
    def create_channels():
        try:
            count = int(get_input("How many channels do you want to create?: "))
        except:
            print("Invalid number.")
            return
        name = get_input("Enter channel base name: ")

        def create(_):
            payload = {"name": name, "type": 0}
            r = requests.post(f"{API_BASE}/guilds/{guild_id}/channels", headers=headers, json=payload)
            if r.status_code == 201:
                print(Fore.GREEN + f"[+] Created Text Channel : {payload['name']}")
            else:
                print(Fore.RED + f"Failed: {r.status_code} | {r.text}")

        threaded_action(range(count), create)

    # 2) Delete All Channels
    def delete_channels():
        r = requests.get(f"{API_BASE}/guilds/{guild_id}/channels", headers=headers)
        try:
            channels = r.json()
        except:
            print("⚠️ Failed to get channels")
            return

        def delete(ch):
            r2 = requests.delete(f"{API_BASE}/channels/{ch['id']}", headers=headers)
            if r2.status_code == 204:
                print(Fore.RED + f"[-] Deleting Text Channel : {ch['name']}")
            else:
                print(Fore.RED + f"Failed: {r2.status_code}")

        threaded_action(channels, delete)

    # 3) Rename All Channels
    def rename_channels():
        new_name = get_input("Enter new name for all channels: ")
        r = requests.get(f"{API_BASE}/guilds/{guild_id}/channels", headers=headers)
        try:
            channels = r.json()
        except:
            print("⚠️ Failed to get channels")
            return

        def rename(ch):
            r2 = requests.patch(f"{API_BASE}/channels/{ch['id']}", headers=headers, json={"name": new_name})
            if r2.status_code == 200:
                print(Fore.GREEN + f"[+] Renamed Text Channel : {ch['name']} -> {new_name}")
            else:
                print(Fore.RED + f"Failed: {r2.status_code}")

        threaded_action(channels, rename)

    # 4) Create Roles
    def create_roles():
        try:
            count = int(get_input("How many roles do you want to create?: "))
        except:
            print("Invalid number.")
            return
        name = get_input("Enter role base name: ")

        def create(_):
            payload = {"name": name}
            r = requests.post(f"{API_BASE}/guilds/{guild_id}/roles", headers=headers, json=payload)
            if r.status_code == 200:
                print(Fore.GREEN + f"[+] Created Text Role : {name}")
            else:
                print(Fore.RED + f"Failed: {r.status_code} | {r.text}")

        threaded_action(range(count), create)

    # 5) Delete All Roles
    def delete_roles():
        r = requests.get(f"{API_BASE}/guilds/{guild_id}/roles", headers=headers)
        try:
            roles = r.json()
        except:
            print("⚠️ Failed to get roles")
            return

        # نحصل على رتبة البوت لتجنب حذف الرتب الأعلى
        bot_user = requests.get(f"{API_BASE}/users/@me", headers=headers).json()
        bot_roles = [r for r in roles if r['id'] == bot_user.get('id')]
        bot_position = bot_roles[0]['position'] if bot_roles else 0

        def delete(role):
            if role['position'] < bot_position:
                r2 = requests.delete(f"{API_BASE}/guilds/{guild_id}/roles/{role['id']}", headers=headers)
                if r2.status_code == 204:
                    print(Fore.RED + f"[-] Deleted Text Role : {role['name']}")
                else:
                    print(Fore.RED + f"Failed: {r2.status_code}")

        threaded_action(roles, delete)

    # 6) Delete All Webhooks
    def delete_webhooks():
        r = requests.get(f"{API_BASE}/guilds/{guild_id}/webhooks", headers=headers)
        try:
            hooks = r.json()
        except:
            print("⚠️ Failed to get webhooks")
            return

        def delete(wh):
            r2 = requests.delete(f"{API_BASE}/webhooks/{wh['id']}", headers=headers)
            if r2.status_code == 204:
                print(Fore.RED + f"[-] Webhook Deleted : {wh['name']}")
            else:
                print(Fore.RED + f"Failed: {r2.status_code}")

        threaded_action(hooks, delete)

    # 7) Delete All Emojis
    def delete_emojis():
        r = requests.get(f"{API_BASE}/guilds/{guild_id}/emojis", headers=headers)
        try:
            emojis = r.json()
        except:
            print("⚠️ Failed to get emojis")
            return

        def delete(emoji):
            r2 = requests.delete(f"{API_BASE}/guilds/{guild_id}/emojis/{emoji['id']}", headers=headers)
            if r2.status_code == 204:
                print(Fore.RED + f"[-] Emoji Deleted : {emoji['name']}")
            else:
                print(Fore.RED + f"Failed: {r2.status_code}")

        threaded_action(emojis, delete)

    # 8) Change Server Name
    def change_server_name():
        new_name = get_input("Enter new server name: ")
        r = requests.patch(f"{API_BASE}/guilds/{guild_id}", headers=headers, json={"name": new_name})
        if r.status_code == 200:
            print(Fore.GREEN + f"[+] Server Name Has Been Changed To : {new_name}")
        else:
            print(Fore.RED + f"Failed: {r.status_code} | {r.text}")

    # 9) Spam All Channels
    def spam_channels():
        msg = get_input("Enter spam message: ")
        try:
            count = int(get_input("How many times to send per channel?: "))
        except:
            print("Invalid number.")
            return
        r = requests.get(f"{API_BASE}/guilds/{guild_id}/channels", headers=headers)
        try:
            channels = r.json()
        except:
            print("⚠️ Failed to get channels")
            return

        text_channels = [ch['id'] for ch in channels if ch.get('type') == 0]

        def spam(ch_id):
            for _ in range(count):
                r2 = requests.post(f"{API_BASE}/channels/{ch_id}/messages", headers=headers, json={"content": msg})
                if r2.status_code in [200,201]:
                    print(Fore.GREEN + f"[+] Message Sent in Channel : {ch_id}")
                else:
                    print(Fore.RED + f"Failed: {r2.status_code}")

        threaded_action(text_channels, spam)

    # ------------------ القائمة ------------------
    while True:
        print("\nChoose action:")
        print("(#1) Create Channels")
        print("(#2) Delete All Channels")
        print("(#3) Rename All Channels")
        print("(#4) Create Roles")
        print("(#5) Delete All Roles")
        print("(#6) Delete All Webhooks")
        print("(#7) Delete All Emojis")
        print("(#8) Change Server Name")
        print("(#9) Spam All Channels")
        print("(0) Exit")

        choice = get_input("Enter your choice: ")
        if choice == "1": create_channels()
        elif choice == "2": delete_channels()
        elif choice == "3": rename_channels()
        elif choice == "4": create_roles()
        elif choice == "5": delete_roles()
        elif choice == "6": delete_webhooks()
        elif choice == "7": delete_emojis()
        elif choice == "8": change_server_name()
        elif choice == "9": spam_channels()
        elif choice == "0": break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    nuke_tool()