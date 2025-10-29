from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import RPi.GPIO as GPIO

# GPIO setup
LED_PINS = [17, 27, 22]
GPIO.setmode(GPIO.BCM)

pwm_leds = []
for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 500)
    pwm.start(0)
    pwm_leds.append(pwm)

# Record brightness level (0–100)
brightness = [0, 0, 0]


class LEDHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_form()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = urllib.parse.parse_qs(post_data.decode('utf-8'))

        led_index = int(data.get('led', [0])[0])
        new_brightness = int(data.get('brightness', [0])[0])

        # Update LED brightness
        brightness[led_index] = new_brightness
        pwm_leds[led_index].ChangeDutyCycle(new_brightness)

        self.send_form()

    def send_form(self):
        html = f"""
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
                    background-color: #f7f7f7;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    padding: 20px 30px;
                    text-align: left;
                }}
                h3 {{
                    margin-bottom: 10px;
                }}
                input[type=range] {{
                    width: 200px;
                }}
                input[type=submit] {{
                    margin-top: 10px;
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: 1px solid #ccc;
                    background-color: #eee;
                    cursor: pointer;
                }}
                input[type=submit]:hover {{
                    background-color: #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <form method="POST">
                    <label><b>Brightness level:</b></label><br>
                    <input type="range" name="brightness" min="0" max="100" value="50"><br><br>
                    
                    <b>Select LED:</b><br>
                    <label><input type="radio" name="led" value="0" checked> LED 1 ({brightness[0]}%)</label><br>
                    <label><input type="radio" name="led" value="1"> LED 2 ({brightness[1]}%)</label><br>
                    <label><input type="radio" name="led" value="2"> LED 3 ({brightness[2]}%)</label><br><br>
                    
                    <input type="submit" value="Change Brightness">
                </form>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=LEDHandler):
    server_address = ('', 8080)
    httpd = server_class(server_address, handler_class)
    
    # Find Pi Zero 2W's IP address with hostname -I, when log into pi zero 2W via ssh
    
    print("WebPage running on http://PiZero2_IPaddress:8080")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for pwm in pwm_leds:
            pwm.stop()
        GPIO.cleanup()
        httpd.server_close()


if __name__ == '__main__':
    run()
