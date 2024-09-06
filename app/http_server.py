"""Servidor HTTP mínimo: GET /, GET /api/health y POST /api/login."""
import json
import logging
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import __version__

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

log = logging.getLogger("Server")
access_log = logging.getLogger("HTTP")


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        server_version = "Plataforma/" + __version__

        def log_message(self, format, *args):  # noqa: A002 - firma de la clase base
            pass  # usamos nuestro propio log de accesos (HTTP)

        def _send(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status, data):
            self._send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8")

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                with open(os.path.join(STATIC_DIR, "index.html"), "rb") as fh:
                    self._send(200, fh.read(), "text/html; charset=utf-8")
            elif self.path == "/api/health":
                data = {"status": "ok", "version": __version__}
                data.update(app.health())
                self._json(200, data)
            else:
                self._json(404, {"ok": False, "mensaje": "No encontrado"})

        def do_POST(self):
            start = time.monotonic()
            status = 500
            try:
                if self.path != "/api/login":
                    status = 404
                    self._json(status, {"ok": False, "mensaje": "No encontrado"})
                    return
                length = int(self.headers.get("Content-Length") or 0)
                try:
                    payload = json.loads(self.rfile.read(length) or b"{}")
                except ValueError:
                    status = 400
                    self._json(status, {"ok": False, "mensaje": "Petición inválida"})
                    return
                status, body = app.controller.login(payload)
                self._json(status, body)
            except Exception:
                status = 500
                log.exception("Unhandled exception on POST %s", self.path)
                self._json(500, {"ok": False, "mensaje": "Internal Server Error"})
            finally:
                access_log.info("POST %s -> %d (%.0f ms)", self.path, status,
                                (time.monotonic() - start) * 1000)

    return Handler


def serve(app, host, port):
    httpd = ThreadingHTTPServer((host, port), make_handler(app))
    httpd.daemon_threads = True
    log.info("Platform v%s listening on http://%s:%d", __version__, host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log.info("Server stopped")
    finally:
        httpd.server_close()
