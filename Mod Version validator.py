import json
import os
import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
WORKSHOP_URL_TEMPLATE = "https://reforger.armaplatform.com/workshop/{}"

def get_latest_version_from_workshop(mod_id):
    url = WORKSHOP_URL_TEMPLATE.format(mod_id)
    try:
        print(f" - Fetching workshop page: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Save raw HTML for debugging
        debug_path = os.path.join(SCRIPT_DIR, f"{mod_id}_debug.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f" - [DEBUG] Saved HTML to: {debug_path}")

        soup = BeautifulSoup(response.text, "html.parser")

        # Look for <dt> with 'Version' and its next <dd>
        dt_tags = soup.find_all("dt", string="Version")
        if not dt_tags:
            print(f" - [DEBUG] No <dt> tags with text 'Version' found")

        for dt in dt_tags:
            dd = dt.find_next_sibling("dd")
            if dd:
                version = dd.text.strip()
                print(f" - [DEBUG] Found workshop version: {version}")
                return version

        print(" - [DEBUG] Could not extract version from HTML.")
    except Exception as e:
        print(f"[ERROR] Failed to fetch mod page for {mod_id}: {e}")
    return None

def update_config_versions():
    if not os.path.isfile(CONFIG_PATH):
        print(f"[ERROR] Config file not found at {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    # 🛠️ Fixed path to nested 'mods' section
    mods = data.get("game", {}).get("mods", [])
    if not mods:
        print("[ERROR] No mods found under game.mods!")
        return

    changed = False

    for mod in mods:
        mod_id = mod.get("modId")
        current_version = mod.get("version")
        mod_name = mod.get("name", mod_id)
        if not mod_id:
            continue

        print(f"Checking mod '{mod_name}' (current version: {current_version})")
        latest_version = get_latest_version_from_workshop(mod_id)

        if latest_version and latest_version != current_version:
            print(f" - [UPDATE] Version mismatch: {current_version} -> {latest_version}")
            mod["version"] = latest_version
            changed = True
        elif latest_version == current_version:
            print(f" - [OK] Up to date.")
        else:
            print(f" - [WARN] Could not determine workshop version.")

    if changed:
        with open(CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print(f"[INFO] Config updated and saved to: {CONFIG_PATH}")
    else:
        print("[INFO] No updates were needed.")

if __name__ == "__main__":
    update_config_versions()
