import asyncio
import json
import os
import websockets

# Speicher für aktive Räume
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

            # 1. Raum beitreten
            if data.get("type") == "join_room":
                room_id = data.get("room", "DEFAULT").strip().upper()
                
                # Alten Raum verlassen
                old_room = CLIENT_ROOMS.get(websocket)
                if old_room and old_room in ROOMS:
                    ROOMS[old_room].discard(websocket)

                # Dem neuen Raum zuweisen
                CLIENT_ROOMS[websocket] = room_id
                if room_id not in ROOMS:
                    ROOMS[room_id] = set()
                ROOMS[room_id].add(websocket)
                
                print(f"[WebSocket] Client ist Raum '{room_id}' beigetreten.")
                continue

            # 2. Nachricht an Clients im SELBEN Raum weiterleiten
            current_room = CLIENT_ROOMS.get(websocket)
            if current_room and current_room in ROOMS:
                for client in ROOMS[current_room]:
                    if client != websocket:
                        await client.send(message)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        room_id = CLIENT_ROOMS.pop(websocket, None)
        if room_id and room_id in ROOMS:
            ROOMS[room_id].discard(websocket)
            if not ROOMS[room_id]:
                del ROOMS[room_id]
        print(f"[WebSocket] Client getrennt.")

async def main():
    # Render weist automatisch einen Port über os.environ zu
    port = int(os.environ.get("PORT", 8765))
    
    async with websockets.serve(ws_handler, "0.0.0.0", port):
        print(f"[WebSocket] Server gestartet auf Port {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())