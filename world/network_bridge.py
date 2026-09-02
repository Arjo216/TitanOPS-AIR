import os
import urllib.request
import cv2
import requests
import time
import base64
import networkx as nx
import matplotlib.pyplot as plt
from dataclasses import dataclass
import asyncio
import websockets
import json
import io

COLAB_API_URL = "https://614c-34-74-89-39.ngrok-free.app/process_vision" # <-- PASTE URL HERE
connected_clients = set()

class SwarmWorldEngine:
    def __init__(self, grid_size=20):
        self.step_count = 0
        self.grid_size = grid_size
        self.G = nx.grid_2d_graph(grid_size, grid_size)
        self.ugv_pos = (0, 0)
        
        # 🚀 TACTICAL STATES
        self.autopilot_engaged = False
        self.current_threats = []
        self.strike_authorized = False
        self.blast_zones = []

        self.video_path = "world/tactical_feed.mp4"
        if not os.path.exists(self.video_path):
            print("[SYSTEM] Downloading surveillance footage...")
            urllib.request.urlretrieve("https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4", self.video_path)
        self.cap = cv2.VideoCapture(self.video_path)

    def acquire_sensor_data(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 360))
            # If strike authorized, draw a massive red overlay on the video feed
            if self.strike_authorized:
                overlay = frame.copy()
                cv2.rectangle(overlay, (0,0), (640, 360), (0, 0, 255), -1)
                cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
                cv2.putText(frame, "ORDNANCE DEPLOYED", (150, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)

            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            return base64.b64encode(buffer).decode('utf-8')

    def generate_map_base64(self):
        plt.figure(figsize=(5, 5))
        pos = {(x, y): (y, -x) for x, y in self.G.nodes()}
        
        # Draw base map
        nx.draw_networkx_nodes(self.G, pos, node_size=50, node_color="#222222")
        nx.draw_networkx_edges(self.G, pos, alpha=0.3, edge_color="#444444")
        
        # Draw Threats / Blast Zones
        for threat in self.current_threats:
            cx, cy = threat['center_pixel']
            grid_x = min(int((cx / 1000) * self.grid_size), self.grid_size - 1)
            grid_y = min(int((cy / 1000) * self.grid_size), self.grid_size - 1)
            
            if self.strike_authorized:
                # Draw Explosion Radius
                nx.draw_networkx_nodes(self.G, pos, nodelist=[(grid_x, grid_y)], node_size=800, node_color="#ff0000", alpha=0.5)
            else:
                # Draw Locked Target
                nx.draw_networkx_nodes(self.G, pos, nodelist=[(grid_x, grid_y)], node_size=150, node_color="#ffcc00")

        nx.draw_networkx_nodes(self.G, pos, nodelist=[self.ugv_pos], node_size=100, node_color="#00ff00")
        
        plt.axis("off")
        plt.gcf().set_facecolor('black')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor='black', pad_inches=0)
        buf.seek(0)
        map_b64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return map_b64

    async def step(self):
        try:
            image_b64 = self.acquire_sensor_data()
            payload = {"agent_id": "UAV_01", "timestamp": time.time(), "image_b64": image_b64}
            
            response = await asyncio.to_thread(requests.post, COLAB_API_URL, json=payload, timeout=5.0)
            
            if response.status_code == 200:
                intel = response.json()
                self.current_threats = intel['threat_data']
                threat_count = intel['threats_detected']
                
                # --- COMMAND & CONTROL LOGIC ---
                log_msg = f"[RADAR] Scanning... Sector Clear."
                status = "PATROL"

                if threat_count > 0:
                    status = "TARGET_LOCK"
                    log_msg = f"[WARNING] {threat_count} Targets acquired. Calculating threat geometry."
                    
                    if self.autopilot_engaged:
                        # Autopilot automatically fires on any target
                        self.strike_authorized = True
                        status = "STRIKE_EXECUTED"
                        log_msg = f"[AUTOPILOT] LETHAL FORCE AUTHORIZED. Interceptor Swarm deployed."
                    else:
                        if self.strike_authorized:
                            status = "STRIKE_EXECUTED"
                            log_msg = f"[MANUAL OVERRIDE] COMMAND CONFIRMED. Targets Neutralized."
                        else:
                            log_msg = f"[HOLD] Target locked. Awaiting manual commander authorization."

                map_b64 = self.generate_map_base64()

                ui_payload = {
                    "type": "TELEMETRY",
                    "status": status,
                    "threats": threat_count,
                    "video_frame": intel.get('processed_image_b64', image_b64),
                    "map_frame": map_b64,
                    "log_msg": log_msg
                }
                
                for client in list(connected_clients):
                    await client.send(json.dumps(ui_payload))

                # Reset strike after 1 frame so it flashes on screen
                if self.strike_authorized:
                    self.strike_authorized = False

        except Exception as e:
            pass

world = SwarmWorldEngine()

async def ws_handler(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            cmd = data.get("command")
            if cmd == "ENGAGE_AUTOPILOT":
                world.autopilot_engaged = True
                print("[C2] Autopilot ENGAGED.")
            elif cmd == "MANUAL_OVERRIDE":
                world.autopilot_engaged = False
                print("[C2] Manual Override ACTIVE. Awaiting fire commands.")
            elif cmd == "FIRE_SWARM":
                world.strike_authorized = True
                print("[C2] MANUAL STRIKE EXECUTED.")
    finally:
        connected_clients.remove(websocket)

async def main():
    print("TITAN_OPS AIR: WEAPONS HOT.")
    server = await websockets.serve(ws_handler, "0.0.0.0", 8765)
    while True:
        await world.step()
        await asyncio.sleep(2.0)

if __name__ == "__main__":
    asyncio.run(main())