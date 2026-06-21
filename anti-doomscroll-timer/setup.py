import os
import sys
import json
import base64
import hashlib
import subprocess
import importlib

def _ensure_pip():
    """Bootstrap pip via ensurepip if it is missing (e.g. Python 3.14 on Windows)."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        pass
    print("pip not found – trying ensurepip to bootstrap...")
    try:
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        return True
    except Exception as e:
        print(f"Could not bootstrap pip: {e}")
        return False

def install_dependencies():
    """Install required packages and return True on success."""
    print("Installing python dependencies (customtkinter, pillow, cryptography)...")
    if not _ensure_pip():
        print("ERROR: pip is not available for this Python interpreter.")
        print(f"  Interpreter: {sys.executable}")
        print("  Please run setup.py with a Python that has pip, e.g.:")
        print("    py -3.11 setup.py")
        return False
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "customtkinter", "pillow", "cryptography"],
            check=True
        )
        # Make newly installed packages visible to the current process.
        importlib.invalidate_caches()
        import site
        if hasattr(site, 'addsitepackages'):
            site.addsitepackages(set(sys.path))
        print("Dependencies installed successfully.\n")
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        print("Please run manually: pip install customtkinter pillow cryptography\n")
        return False

def generate_extension_keys_and_manifests():
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa  # type: ignore[import-not-found]
        from cryptography.hazmat.primitives import serialization  # type: ignore[import-not-found]
    except ImportError:
        print("Error: 'cryptography' library is required to generate the extension key.")
        print("Please run: pip install cryptography")
        sys.exit(1)

    print("Generating secure RSA key pair for the extension...")
    # 1. Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 2. Get public key in DER format
    public_key = private_key.public_key()
    der_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # 3. Encode to base64 for manifest.json
    pub_key_base64 = base64.b64encode(der_bytes).decode('utf-8')
    
    # 4. Calculate Extension ID based on the public key
    # Chrome extension ID is calculated from the SHA256 of the public key's DER encoding.
    # The first 32 characters of the hex digest are converted to letters a-p.
    sha256 = hashlib.sha256(der_bytes).hexdigest()
    mapping = {
        '0': 'a', '1': 'b', '2': 'c', '3': 'd', '4': 'e', '5': 'f', '6': 'g', '7': 'h',
        '8': 'i', '9': 'j', 'a': 'k', 'b': 'l', 'c': 'm', 'd': 'n', 'e': 'o', 'f': 'p'
    }
    extension_id = ''.join(mapping[c] for c in sha256[:32])
    
    print(f"Computed Extension ID: {extension_id}")
    
    # 5. Write extension/manifest.json
    extension_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'extension'))
    os.makedirs(extension_dir, exist_ok=True)
    
    manifest_data = {
        "manifest_version": 3,
        "name": "Anti-Doomscroll Timer",
        "version": "1.0",
        "description": "Monitors YouTube Shorts and Instagram Reels to prevent-doomscrolling.",
        "permissions": [
            "tabs",
            "activeTab",
            "webNavigation",
            "nativeMessaging"
        ],
        "background": {
            "service_worker": "background.js"
        },
        "host_permissions": [
            "*://*.youtube.com/*",
            "*://*.instagram.com/*"
        ],
        "key": pub_key_base64,
        "icons": {
            "128": "icon.png"
        }
    }
    
    with open(os.path.join(extension_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=4)
    print(f"Created: {os.path.join(extension_dir, 'manifest.json')}")

    # 6. Write bridge/com.antidoomscroll.timer.json (Host Manifest)
    bridge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'bridge'))
    os.makedirs(bridge_dir, exist_ok=True)
    
    bat_path = os.path.join(bridge_dir, 'host.bat')
    # Write host.bat
    bat_content = f'@echo off\n"{sys.executable}" "{os.path.join(bridge_dir, "host.py")}" %*\n'
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    print(f"Created: {bat_path}")

    host_manifest = {
        "name": "com.antidoomscroll.timer",
        "description": "Anti-Doomscroll and Timer Native Messaging Host",
        "path": bat_path,
        "type": "stdio",
        "allowed_origins": [
            f"chrome-extension://{extension_id}/"
        ]
    }
    
    host_manifest_path = os.path.join(bridge_dir, 'com.antidoomscroll.timer.json')
    with open(host_manifest_path, 'w', encoding='utf-8') as f:
        json.dump(host_manifest, f, indent=4)
    print(f"Created: {host_manifest_path}")

    # 7. Write bridge/register_host.reg
    escaped_manifest_path = host_manifest_path.replace('\\', '\\\\')
    reg_content = f"""Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\\Software\\Google\\Chrome\\NativeMessagingHosts\\com.antidoomscroll.timer]
@="{escaped_manifest_path}"

[HKEY_CURRENT_USER\\Software\\Microsoft\\Edge\\NativeMessagingHosts\\com.antidoomscroll.timer]
@="{escaped_manifest_path}"

[HKEY_CURRENT_USER\\Software\\BraveSoftware\\Brave-Browser\\NativeMessagingHosts\\com.antidoomscroll.timer]
@="{escaped_manifest_path}"
"""
    reg_path = os.path.join(bridge_dir, 'register_host.reg')
    with open(reg_path, 'w', encoding='utf-8') as f:
        f.write(reg_content)
    print(f"Created: {reg_path}")

    # 8. Register in Windows Registry directly (HKCU doesn't need Admin rights)
    print("Registering host in Windows Registry...")
    try:
        import winreg
        for browser in ['Google\\Chrome', 'Microsoft\\Edge', 'BraveSoftware\\Brave-Browser']:
            key_path = f"Software\\{browser}\\NativeMessagingHosts\\com.antidoomscroll.timer"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, host_manifest_path)
            winreg.CloseKey(key)
        print("Success: Registered Native Messaging Host for Chrome, Edge and Brave in Registry.")
    except Exception as e:
        print(f"Could not automatically register to Windows Registry: {e}")
        print("You can register manually by double-clicking 'bridge/register_host.reg'")

    print("\n" + "="*50)
    print(" SETUP COMPLETE ")
    print("="*50)
    print(f"1. Extension ID is: {extension_id}")
    print("2. Open Chrome, Edge or Brave, go to Extensions, enable Developer Mode.")
    print("3. Click 'Load unpacked' and select the 'extension' directory of this project.")
    print("4. Start the Python app by running: python app/main.py")
    print("="*50 + "\n")

if __name__ == "__main__":
    if not install_dependencies():
        print("Aborting setup – dependencies could not be installed.")
        sys.exit(1)
    generate_extension_keys_and_manifests()
