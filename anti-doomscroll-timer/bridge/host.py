import sys
import json
import struct
import socket

# Port, auf dem die Python GUI-App auf eingehende Verbindungen wartet
GUI_PORT = 9005
GUI_HOST = "127.0.0.1"

def read_message():
    """
    Liest eine Nachricht aus dem Standard-Input im Native Messaging Format.
    Native Messaging verwendet ein 4-Byte Längenpräfix vor jeder JSON-Nachricht.
    """
    try:
        # Lese die ersten 4 Bytes (Längenpräfix)
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length:
            sys.exit(0)
        # Entpacke die Länge als unsigned 32-bit Integer
        message_length = struct.unpack('@I', raw_length)[0]
        # Lese die eigentliche Nachricht
        message = sys.stdin.buffer.read(message_length).decode('utf-8')
        return json.loads(message)
    except Exception:
        sys.exit(1)

def send_to_gui(message_data):
    """
    Sendet die empfangene Nachricht als JSON per TCP-Socket an die GUI-App.
    """
    try:
        # Erstelle einen TCP-Socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)  # Timeout von 2 Sekunden
            s.connect((GUI_HOST, GUI_PORT))
            # Sende die Nachricht als UTF-8 codierten String
            serialized = json.dumps(message_data) + "\n"
            s.sendall(serialized.encode('utf-8'))
    except ConnectionRefusedError:
        # GUI-App läuft vermutlich gerade nicht, ignoriere den Fehler
        pass
    except Exception as e:
        # Andere Fehler protokollieren (optional in Datei)
        pass

def main():
    while True:
        # Warte auf Nachrichten von der Chrome/Edge Extension
        msg = read_message()
        if msg:
            # Leite die Nachricht (z. B. {"url": "..."}) an die GUI weiter
            send_to_gui(msg)

if __name__ == "__main__":
    main()
