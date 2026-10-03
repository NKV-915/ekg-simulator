import asyncio
import http.server
import json
import socketserver
import threading
import websockets

# Speicher für aktive Räume: {"RAUM1": {websocket1, websocket2}}
ROOMS = {}
CLIENT_ROOMS = {}  # Zuordnung: websocket -> room_id

async def ws_handler(websocket):
    client_ip = websocket.remote_address[0]
    print(f"[WebSocket] Neuer Client verbunden: {client_ip}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            # 1. Raum beitreten
            if data.get("type") == "join_room":
                room_id = data.get("room", "DEFAULT").strip().upper()
                
                # Alten Raum verlassen, falls vorhanden
                old_room = CLIENT_ROOMS.get(websocket)
                if old_room and old_room in ROOMS:
                    ROOMS[old_room].discard(websocket)

                # Dem neuen Raum zuweisen
                CLIENT_ROOMS[websocket] = room_id
                if room_id not in ROOMS:
                    ROOMS[room_id] = set()
                ROOMS[room_id].add(websocket)
                
                print(f"[WebSocket] Client {client_ip} ist Raum '{room_id}' beigetreten.")
                continue

            # 2. Nachricht nur an Clients im SELBEN Raum weiterleiten
            current_room = CLIENT_ROOMS.get(websocket)
            if current_room and current_room in ROOMS:
                for client in ROOMS[current_room]:
                    if client != websocket:
                        await client.send(message)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Client beim Trennen aus dem Raum entfernen
        room_id = CLIENT_ROOMS.pop(websocket, None)
        if room_id and room_id in ROOMS:
            ROOMS[room_id].discard(websocket)
            if not ROOMS[room_id]:
                del ROOMS[room_id]
        print(f"[WebSocket] Client getrennt: {client_ip}")

def run_http_server(port=8000):
    Handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"[HTTP] Webserver gestartet unter: http://localhost:{port}/")
        httpd.serve_forever()

async def main():
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        print("[WebSocket] Server läuft auf ws://0.0.0.0:8765 (Raum-Support aktiv)")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Server] Beendet durch Benutzer.")