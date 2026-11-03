import json
import threading
import unittest
import urllib.error
import urllib.request

from app.server import create_server


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Port 0 lets the OS choose a free port, so tests never collide.
        cls.server = create_server("127.0.0.1", 0)
        cls.base_url = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def get(self, path):
        return urllib.request.urlopen(self.base_url + path, timeout=5)

    def test_home_page(self):
        with self.get("/") as resp:
            body = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("text/html", resp.headers["Content-Type"])
            self.assertIn("StreamForge", body)

    def test_health_endpoint(self):
        with self.get("/health") as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers["Content-Type"], "application/json")
            self.assertEqual(json.loads(resp.read()), {"status": "ok"})

    def test_health_ignores_query_string(self):
        with self.get("/health?probe=1") as resp:
            self.assertEqual(resp.status, 200)

    def test_unknown_path_returns_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.get("/does-not-exist")
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()