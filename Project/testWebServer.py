import http.server
import socketserver
import json
import time
import multiprocessing
from Shifter import shifter
from Motor_Code_Project import Stepper
import Json_Reader

# Preload angle data
XY = Json_Reader.goanglexy
Z = Json_Reader.goanglez
numturrets = len(Json_Reader.TurretData)
numball = len(Json_Reader.BallData)


# -------------------------
#  MOTOR + GPIO SIMULATION
# -------------------------
class GPIOSimulator:
    def __init__(self):
        self.pin_state = False
        self.radius = 0
        self.theta = 0
        self.z = 0

        self.s = shifter(16, 21, 20)
        self.lock = multiprocessing.Lock()
        self.m1 = Stepper(self.s, self.lock, 0)
        self.m2 = Stepper(self.s, self.lock, 1)

        self.m1.zero()
        self.m2.zero()

    def toggle_pin(self):
        self.pin_state = not self.pin_state
        return self.pin_state

    def set_origin(self, radius, theta, z):
        self.radius = float(radius)
        self.theta = float(theta)
        self.z = float(z)

        self.m1.zero()
        self.m2.zero()
        return True

    def get_status(self):
        return {
            "pin_state": "ON" if self.pin_state else "OFF",
            "radius": self.radius,
            "theta": self.theta,
            "z": self.z,
            "motor1_angle": float(self.m1.angle),
            "motor2_angle": float(self.m2.angle)
        }

    def initiate_automation(self):
        print("Automation started...")

        # turrets
        for t in range(1, numturrets):
            self.m1.goAngle(XY[f"turret_{t}"])
            self.m2.goAngle(Z[f"turret_{t}"])
            self.m1.both.wait()
            self.m2.both.wait()
            time.sleep(2)

        # balls
        for b in range(1, numball):
            self.m1.goAngle(XY[f"ball_{b}"])
            self.m2.goAngle(Z[f"ball_{b}"])
            self.m1.both.wait()
            self.m2.both.wait()
            time.sleep(2)

        self.m1.goAngle(0)
        self.m2.goAngle(0)
        return True


gpio = GPIOSimulator()



# -------------------------
#  WEB SERVER HANDLER
# -------------------------
class MotorRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        # Serve dashboard directly (like working LED example)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        status = gpio.get_status()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Motor Dashboard</title>
            <style>
                body {{
                    font-family: Arial;
                    background: #f0f0f0;
                    padding: 20px;
                }}
                .card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    width: 400px;
                    margin: auto;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                button {{
                    padding: 10px 20px;
                    margin: 5px;
                    font-size: 16px;
                    border-radius: 6px;
                    border: none;
                    cursor: pointer;
                }}
                .on {{ background:#4CAF50; color:white; }}
                .off {{ background:#F44336; color:white; }}
                .blue {{ background:#2196F3; color:white; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Motor Status</h2>

                <p><b>Pin:</b> {status["pin_state"]}</p>
                <p><b>Radius:</b> {status["radius"]}</p>
                <p><b>Theta:</b> {status["theta"]}</p>
                <p><b>Z:</b> {status["z"]}</p>

                <p><b>Motor 1 Angle:</b> {status["motor1_angle"]:.2f}°</p>
                <p><b>Motor 2 Angle:</b> {status["motor2_angle"]:.2f}°</p>

                <button class="on" onclick="send('toggle')">Toggle Pin</button>
                <button class="blue" onclick="send('automation')">Start Automation</button>

                <h3>Set Origin</h3>
                <input id="r" placeholder="Radius" />
                <input id="t" placeholder="Theta" />
                <input id="z" placeholder="Z" />
                <button onclick="setOrigin()">Apply</button>
            </div>

            <script>
                function send(cmd) {{
                    fetch('/' + cmd, {{ method:'POST' }})
                }}

                function setOrigin() {{
                    const body = {{
                        radius: document.getElementById("r").value,
                        theta:  document.getElementById("t").value,
                        z:      document.getElementById("z").value
                    }};
                    fetch('/set_origin', {{
                        method:'POST',
                        headers:{{'Content-Type':'application/json'}},
                        body:JSON.stringify(body)
                    }});
                }}

                // Auto-refresh every 2 seconds
                setInterval(()=>location.reload(), 2000);
            </script>
        </body>
        </html>
        """

        self.wfile.write(html.encode())


    def do_POST(self):
        response = {}

        if self.path == "/toggle":
            response = {"pin": gpio.toggle_pin()}

        elif self.path == "/automation":
            response = {"success": gpio.initiate_automation()}

        elif self.path == "/set_origin":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length).decode())
            response = {"success": gpio.set_origin(data["radius"], data["theta"], data["z"])}

        # Send JSON back
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())



# -------------------------
#  START SERVER
# -------------------------
def start_server(port=8080):
    with socketserver.TCPServer(("", port), MotorRequestHandler) as httpd:
        print(f"Server running at http://<Pi_IP>:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    start_server()
