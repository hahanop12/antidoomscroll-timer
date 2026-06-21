# Walkthrough: Anti-Doomscroll & Timer System

Dieses Dokument beschreibt die implementierten Dateien und die Funktionsweise des "Anti-Doomscroll & Timer"-Systems.

## Projektstruktur

Das Projekt wurde erfolgreich unter `C:\Users\Konsti\.gemini\antigravity\scratch\anti-doomscroll-timer` angelegt. Hier ist eine Übersicht über die erstellten Dateien:

1. **`setup.py`**: Das zentrale Skript, das die Python-Abhängigkeiten installiert, die Schlüssel für die Browser-Erweiterung generiert, die Manifeste mit absoluten Pfaden erstellt und den Native Messaging Host in der Windows-Registrierung einträgt.
2. **`app/main.py`**: Die Hauptanwendung. Sie bietet ein modernes Dark-Mode-Interface (mithilfe von `customtkinter`), einen Live-Timer-Countdown, einen Video-Zähler und steuert die Windows-Systemaktionen (Browser schießen und Standby).
3. **`app/requirements.txt`**: Die Abhängigkeiten für die Python-App (`customtkinter`, `pillow` und `cryptography`).
4. **`extension/manifest.json`**: Die Manifestdatei für die Chrome/Edge-Erweiterung (wird von `setup.py` mit dem generierten PublicKey befüllt).
5. **`extension/background.js`**: Das Hintergrundskript der Erweiterung. Es überwacht Web-Aktivitäten auf YouTube und Instagram und leitet Shorts/Reels-URLs an den Native Messaging Host weiter.
6. **`extension/icon.png`**: Ein professionell generiertes Symbolbild für die Erweiterung.
7. **`bridge/host.py`**: Der Native Messaging Host, der die Daten vom Browser liest und über einen lokalen TCP-Socket an die GUI-App weiterleitet.
8. **`bridge/host.bat`**: Der Windows-Wrapper, der vom Browser aufgerufen wird, um `host.py` auszuführen.
9. **`bridge/com.antidoomscroll.timer.json`**: Die Native Messaging Manifest-Konfiguration (wird von `setup.py` mit dem absoluten Pfad zur `host.bat` und der berechneten Extension-ID befüllt).
10. **`bridge/register_host.reg`**: Die Windows-Registry-Datei, um den Host manuell zu registrieren (falls das automatische Setup fehlschlägt).

---

## Funktionsweise der Komponenten

### 1. Die Python-App (CustomTkinter GUI)
Die App nutzt `customtkinter` für eine ansprechende Oberfläche.
- **Benutzeroberfläche**: Ein stylisches dunkelgraues Design mit blauen und grünen Akzenten. Der Benutzer kann die Zeit und die maximale Anzahl an Videos auswählen. Ein großer Button startet den Countdown.
- **Hintergrund-Socket**: Beim Start der App wird im Hintergrund ein TCP-Server auf Port `9005` gestartet. Er empfängt Nachrichten in Echtzeit. Da grafische Benutzeroberflächen nicht threadsicher sind, werden eingehende URLs in eine thread-sichere `queue.Queue` geschrieben und vom Hauptthread alle 100ms abgefragt.
- **Eindeutigkeit**: Um Fehlzählungen bei Seitenaktualisierungen zu vermeiden, werden empfangene Video-URLs in einem `set()` gespeichert und nur einmal gezählt.
- **Verzögertes Limit-Triggering**: Wenn das eingestellte Video-Limit erreicht wird (z. B. 2/2), wird die Aktion (wie das Schließen des Browsers oder Standby) nicht sofort ausgeführt. Der Benutzer kann das letzte erlaubte Video fertig anschauen. Die UI warnt den Benutzer farblich (Orange und "Letztes Video!"). Erst wenn der Benutzer zum nächsten Video weiterscrollt (sobald der Zähler das Limit überschreitet), werden die ausgewählten Aktionen ausgeführt.
- **Systemaktionen**:
  - **Browser beenden**: Schließt Prozesse wie `chrome.exe`, `msedge.exe`, `firefox.exe`, `opera.exe` und `brave.exe` mittels `taskkill`.
  - **Standby-Modus**: Setzt Windows über die .NET API in den Standby-Zustand.

### 2. Die Browser-Erweiterung
- Die Erweiterung lauscht auf `chrome.tabs.onUpdated` und `chrome.webNavigation.onHistoryStateUpdated`.
- Da moderne Web-Apps (wie YouTube und Instagram) oft Seitenübergänge per History-API (SPA) durchführen, sorgt `onHistoryStateUpdated` dafür, dass das Laden eines neuen Shorts oder Reels zuverlässig erkannt wird, selbst wenn die Seite nicht komplett neu geladen wird.
- Ein Filter stellt sicher, dass dieselbe URL nicht mehrfach hintereinander an den Host geschickt wird.

### 3. Die Brücke (Native Messaging)
- **Kommunikationsfluss**: Der Browser startet beim Laden eines Shorts/Reels automatisch die Datei `host.bat`, welche `host.py` ausführt.
- Der Browser sendet die Daten als standardisiertes Datenpaket (4-Byte-Länge + JSON).
- `host.py` liest dieses Paket ein, stellt eine kurze TCP-Verbindung zur GUI-App her, sendet das Paket weiter und schließt die Verbindung wieder.
- Dies entkoppelt die Lebensdauer der GUI-App vollständig vom Browser-Prozess.

---

## Installationsanleitung

Detaillierte Schritte zur Inbetriebnahme findest du in der ebenfalls erstellten [README.md](file:///C:/Users/Konsti/.gemini/antigravity/scratch/anti-doomscroll-timer/README.md).

Zusammenfassend:
1. Python installieren (und den Haken bei **"Add python.exe to PATH"** setzen).
2. `setup.py` im Projektverzeichnis ausführen:
   ```cmd
   python setup.py
   ```
3. Den Ordner `extension` als entpackte Erweiterung im Browser laden (`chrome://extensions/` -> Entwicklermodus -> Entpackte Erweiterung laden).
4. Die App mit `python app/main.py` starten und den Timer aktivieren!
