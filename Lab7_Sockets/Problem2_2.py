from http.server import BaseHTTPRequestHandler, HTTPServer
import RPi.GPIO as GPIO
import json

# GPIO setup
led_pins = [17, 27, 22]
GPIO.setmode(GPIO.BCM)

pwms = []
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 500)
    pwm.start(0)
    pwms.append(pwm)

brightness_levels = [0, 0, 0]  # Store current brightness % for each LED

# --- HTTP Request Handler ---
class LEDHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LED Brightness Control</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #f7f8fa;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 25px 40px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    width: 300px;
                }}
                .slider-group {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                label {{
                    width: 60px;
                    font-weight: bold;
                }}
                input[type=range] {{
                    flex: 1;
                    height: 6px;
                    border-radius: 5px;
                    background: #ddd;
                    outline: none;
                    -webkit-appearance: none;
                }}
                input[type=range]::-webkit-slider-thumb {{
                    -webkit-appearance: none;
                    appearance: none;
                    width: 18px;
                    height: 18px;
                    border-radius: 50%;
                    background: #3b82f6; /* Blue handle */
                    cursor: pointer;
                }}
                input[type=range]::-webkit-slider-runnable-track {{
                    background: #3b82f6;
                    height: 6px;
                    border-radius: 5px;
                }}
                span {{
                    width: 40px;
                    text-align: right;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                {"".join([
                    f'''
                    <div class="slider-group">
                        <label>LED{i+1}</label>
                        <input type="range" id="led{i}" min="0" max="100" value="{brightness_levels[i]}"
                            oninput="updateLED({i}, this.value)">
                        <span id="val{i}">{brightness_levels[i]}</span>
                    </div>
                    ''' for i in range(3)
                ])}
            </div>

            <script>
                async function updateLED(led, value) {{
                    document.getElementById("val" + led).innerText = value;
                    const data = {{ led: led, brightness: value }};
                    await fetch('/', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(data)
                    }});
                }}
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        led = int(data['led'])
        brightness = int(data['brightness'])
        brightness_levels[led] = brightness
        pwms[led].ChangeDutyCycle(brightness)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))

# --- Run Server ---
if __name__ == "__main__":
    try:
        server = HTTPServer(('0.0.0.0', 8080), LEDHandler)
        print("Server running on http://<Pi_IP>:8080")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for pwm in pwms:
            pwm.stop()
        GPIO.cleanup()
