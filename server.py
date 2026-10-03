import asyncio
import json
import os
import websockets

ROOMS = {}
CLIENT_ROOMS = {}

async def ws_handler(websocket):
    client_ip = websocket.remote_address[0] if websocket.remote_address else "Unknown"
    print(f"[WebSocket] Verbindung aufgebaut: {client_ip}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type")

            # Heartbeat ping/pong zur Aufrechterhaltung der Verbindung auf Render
            if msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
                continue

            # 1. Raum beitreten
            if msg_type == "join_room":
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
                
                print(f"[WebSocket] Client {client_ip} ist Raum '{room_id}' beigetreten. (Aktive Geräte in '{room_id}': {len(ROOMS[room_id])})")
                continue

            # 2. Nachricht an alle ANDEREN Clients im SELBEN Raum weiterleiten
            current_room = CLIENT_ROOMS.get(websocket)
            if current_room and current_room in ROOMS:
                for client in ROOMS[current_room]:
                    if client != websocket:
                        try:
                            await client.send(message)
                        except websockets.exceptions.ConnectionClosed:
                            pass

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        room_id = CLIENT_ROOMS.pop(websocket, None)
        if room_id and room_id in ROOMS:
            ROOMS[room_id].discard(websocket)
            if not ROOMS[room_id]:
                del ROOMS[room_id]
        print(f"[WebSocket] Client getrennt: {client_ip}")

async def main():
    port = int(os.environ.get("PORT", 8765))
    async with websockets.serve(ws_handler, "0.0.0.0", port):
        print(f"[WebSocket] Server läuft auf Port {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())