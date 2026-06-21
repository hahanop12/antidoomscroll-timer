# Anti-Doomscroll Timer

**Anti-Doomscroll Timer** is a lightweight, privacy-focused productivity tool designed to help you regain control over your screen time by actively restricting the consumption of short-form videos like YouTube Shorts and Instagram Reels. By combining a browser extension with a native Windows desktop GUI, it counts the videos you watch and tracks your active viewing time, automatically closing your browsers or putting your PC into standby once your limits are reached. It is perfect for anyone struggling with digital distractions who wants a firm, automated barrier to end mindless scrolling.

---

## ⏱️ Features

- **Dual-Limit Monitoring**: Set a strict time limit (e.g., 15 minutes) or a maximum video count (e.g., 10 Reels/Shorts), or both.
- **Smart Window Management**: Automatically terminates popular browser processes (Chrome, Edge, Firefox, Brave, etc.) when your limits are reached.
- **System Standby Option**: Directly puts your Windows PC to sleep to force you to step away from the screen.
- **Grace Period (Last-Video Warning)**: When you reach your video limit, the app enters a warning state ("Last Video!") and changes color. It lets you finish the current video and only triggers the block once you attempt to scroll to the next one.
- **Privacy First & Local**: Runs entirely on your local machine. No external tracking, no cloud telemetry, and no data leaves your computer.
- **Reliable SPA Tracking**: Browser extension utilizes both history state updates and standard tab changes, ensuring accurate tracking even when YouTube/Instagram load new videos dynamically without refreshing the page.

---

## 📋 Prerequisites

To run this tool, your system must meet the following requirements:
- **Operating System**: Windows 10 or Windows 11.
- **Python**: Python >= 3.10 installed on your system.
- **Browser**: Any Chromium-based web browser (such as Google Chrome, Microsoft Edge, Brave, Opera, etc.).

---

## ⚙️ Installation & Setup

Follow these step-by-step instructions to get the tool up and running on your PC:

### Step 1: Clone the Repository
Clone the repository to your local machine and navigate into the project directory:
```bash
git clone https://github.com/Konsti/anti-doomscroll-timer.git
cd anti-doomscroll-timer
```

### Step 2: Install Python Dependencies
Install the required packages using `pip`. These include `customtkinter` (for the GUI), `pillow` (for image processing), and `cryptography` (for secure extension configuration):
```bash
pip install -r app/requirements.txt
```

### Step 3: Run the Setup Script
Run the automated installation script. This script installs any missing packages, generates a secure unique keypair for the browser extension, creates the manifests with absolute system paths, and registers the Native Messaging Host in your Windows Registry:
```bash
python setup.py
```
> [!NOTE]
> The Registry changes are written under `HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts` and `HKEY_CURRENT_USER\Software\Developer\NativeMessagingHosts` so they do not require Administrator privileges.

### Step 4: Install the Browser Extension
1. Open your browser (Chrome or Edge) and navigate to the extensions page:
   - For **Chrome**: Go to `chrome://extensions/`
   - For **Edge**: Go to `edge://extensions/`
2. Enable **Developer mode** using the toggle switch (usually in the top right or top left).
3. Click on the **"Load unpacked"** (Entpackte Erweiterung laden) button.
4. Select the `extension/` folder located inside your cloned `anti-doomscroll-timer` project directory.
5. The extension is now loaded and will communicate automatically with the desktop application.

---

## 🚀 Usage / Quick Start

To start using the tool:

1. Launch the desktop GUI app:
   ```bash
   python app/main.py
   ```
2. Configure your limits:
   - **Time Limit**: The total amount of time you are allowed to browse before actions are triggered (e.g., 15 minutes).
   - **Video Limit**: The maximum number of Shorts or Reels you are allowed to view.
3. Select your desired actions:
   - **Close Browser**: Forcefully closes all active browser windows (Chrome, Edge, Firefox, Brave, etc.) when limits are exceeded.
   - **PC Standby**: Puts your PC into standby mode.
4. Click **Start Timer** (green button).
   - The app will display a live countdown timer and a counter showing the number of videos watched.
   - Each time you watch a YouTube Short or Instagram Reel, the browser extension detects the event and securely communicates it to the GUI, incrementing the counter.
5. To stop the tracking manually at any time, click **Stop** (red button).

---

## 📂 Folder Structure

Here is an overview of the project file tree and where key components reside:

```
anti-doomscroll-timer/
├── app/
│   ├── main.py              # Main CustomTkinter GUI application
│   ├── requirements.txt     # Python application dependencies
│   └── config.json          # Persistent configuration settings
├── bridge/
│   ├── host.py              # Native Messaging Host reading browser messages
│   ├── host.bat             # Windows batch wrapper executed by the browser
│   ├── com.antidoomscroll.timer.json # Manifest linking the browser to the host
│   └── register_host.reg    # Registry file for manual host registration
└── extension/
    ├── manifest.json        # Extension description and permissions
    ├── background.js        # Background script monitoring video changes
    └── icon.png             # Extension logo
```

---

## 🔧 Troubleshooting

- **Registry Key Failures**: If the automatic setup fails to write registry values, run your Command Prompt or PowerShell terminal **as Administrator** and re-run `python setup.py`. Alternatively, you can double-click `bridge/register_host.reg` to manually import the registry settings.
- **Extension Not Counting Videos**:
  - Ensure the desktop GUI is running and the timer is active (`Start Timer` clicked).
  - Verify that the extension is enabled in `chrome://extensions/` or `edge://extensions/`.
  - Check that Python is added to your Windows system `PATH` so `host.bat` can execute `host.py`.
- **Unexpected Browser Closes**: Remember that selecting the **Close Browser** action will close *all* windows of the targeted browsers (not just the tab where you were scrolling). Make sure to save any ongoing work in other browser windows before starting the timer.

---

## 🤝 Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to contribute code:
1. Open an issue on the GitHub repository to discuss your ideas.
2. Fork the repository, create a new branch for your feature, and submit a Pull Request.
3. Make sure to test your changes on Windows with the extension installed before submitting.

---

## ✍️ Credits & Contributors

- **Konsti** — Lead Developer / Original Creator
- **Antigravity** — AI Coding Assistant (by Google DeepMind)
- **Libraries Used**:
  - [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern dark-themed GUI.
  - [Pillow](https://python-pillow.org/) for image formatting.
  - [Cryptography](https://cryptography.io/) for generating browser-compatible secure keys.

---

## 📄 License & Usage

This project is licensed under the GNU General Public License v3.0 (GPLv3) - see the [LICENSE](LICENSE) file for details.

### What this means:
- **Commercial Use:** Permitted, provided any derivative work is also open-sourced under the GPLv3.
- **Modification & Distribution:** You can freely fork, change, and share this software.
- **Source Disclosure:** Anyone distributing a modified version of this tool must make their source code publicly available under the same license.
- **Attribution:** Original credits to **Konsti** must be preserved.

---

### License Agreement

Copyright (c) 2026 Konsti

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to use, copy, modify, and publish the Software, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
2. The original author (Konsti) must be clearly and visibly attributed upon any publication or redistribution of the Software.
3. The Software may NOT be used, sold, or monetized for commercial purposes without prior written consent from the author. For inquiries regarding commercial usage, contact the author via email.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
