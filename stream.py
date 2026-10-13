import cv2
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CAMERA = "/dev/video6"
HOST = "0.0.0.0"
PORT = 8080

cap = cv2.VideoCapture(CAMERA, cv2.CAP_V4L2)

if not cap.isOpened():
    raise RuntimeError(f"Cannot open camera {CAMERA}")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


class StreamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "multipart/x-mixed-replace; boundary=frame"
        )
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    continue

                success, encoded = cv2.imencode(
                    ".jpg",
                    frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 80]
                )

                if not success:
                    continue

                self.wfile.write(b"--frame\r\n")
                self.send_header("Content-Type", "image/jpeg")
                self.send_header(
                    "Content-Length",
                    str(len(encoded))
                )
                self.end_headers()

                self.wfile.write(encoded.tobytes())
                self.wfile.write(b"\r\n")

        except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected")


server = ThreadingHTTPServer((HOST, PORT), StreamHandler)

print(f"Streaming {CAMERA}")
print(f"Open http://<JETSON-IP>:{PORT}")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping stream...")
finally:
    cap.release()
    server.server_close()