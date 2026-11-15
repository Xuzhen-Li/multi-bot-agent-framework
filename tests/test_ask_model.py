import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "scripts", "ask_model.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import ask_model  # noqa: E402


class AskModelTest(unittest.TestCase):
    def test_deepseek_request_shape(self):
        r = ask_model.build_request("deepseek", "deepseek-v4-pro", "hi", effort="high")
        self.assertEqual(r["url"], "https://api.deepseek.com/chat/completions")
        self.assertEqual(r["body"]["reasoning_effort"], "high")
        self.assertEqual(r["body"]["thinking"], {"type": "enabled"})

    def test_gemini_request_shape(self):
        r = ask_model.build_request("gemini", "gemini-4-hydrogen", "hi", system="be brief")
        self.assertTrue(r["url"].startswith("https://generativelanguage.googleapis.com/v1beta/openai/"))
        self.assertEqual(r["body"]["messages"][0]["role"], "system")
        self.assertNotIn("thinking", r["body"])

    def test_dry_run_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            prompt = os.path.join(d, "p.md")
            with open(prompt, "x") as f:
                f.write("Review this.")
            out = os.path.join(d, "a.md")
            res = subprocess.run([sys.executable, SCRIPT, "--provider", "gemini",
                                  "--model", "gemini-4-hydrogen", "--prompt", prompt,
                                  "--out", out, "--dry-run"], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual(json.loads(res.stdout)["body"]["model"], "gemini-4-hydrogen")
            with open(out, "x") as f:
                f.write("old")
            res = subprocess.run([sys.executable, SCRIPT, "--provider", "gemini",
                                  "--model", "m", "--prompt", prompt, "--out", out,
                                  "--dry-run"], capture_output=True, text=True)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("exists", res.stderr)


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self, *args):
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class WritePathTest(unittest.TestCase):
    """Run main() with a fake urlopen, so no network and no API key are used."""

    def run_main(self, d, payload):
        prompt = os.path.join(d, "p.md")
        if not os.path.exists(prompt):
            with open(prompt, "x") as f:
                f.write("Review this.")
        calls = []

        def fake_urlopen(req, timeout=None):
            calls.append(req)
            return FakeResponse(payload)

        old_open, old_key = ask_model.urllib.request.urlopen, os.environ.get("GEMINI_API_KEY")
        ask_model.urllib.request.urlopen = fake_urlopen
        os.environ["GEMINI_API_KEY"] = "test-key"
        try:
            rc = ask_model.main(["--provider", "gemini", "--model", "m", "--prompt", prompt,
                                 "--out", os.path.join(d, "a.md")])
        finally:
            ask_model.urllib.request.urlopen = old_open
            if old_key is None:
                os.environ.pop("GEMINI_API_KEY", None)
            else:
                os.environ["GEMINI_API_KEY"] = old_key
        return rc, calls

    def test_answer_and_meta_written(self):
        with tempfile.TemporaryDirectory() as d:
            rc, calls = self.run_main(d, {"model": "m", "choices": [{"message": {"content": "ok"}}]})
            self.assertEqual(rc, 0)
            self.assertEqual(len(calls), 1)
            with open(os.path.join(d, "a.md")) as f:
                self.assertEqual(f.read(), "ok")
            with open(os.path.join(d, "a.md.meta.json")) as f:
                self.assertEqual(json.load(f)["model"], "m")

    def test_existing_meta_stops_before_the_call(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "a.md.meta.json"), "x") as f:
                f.write("{}")
            with self.assertRaises(SystemExit):
                self.run_main(d, {"choices": [{"message": {"content": "ok"}}]})
            self.assertFalse(os.path.exists(os.path.join(d, "a.md")))

    def test_empty_answer_is_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            rc, calls = self.run_main(d, {"choices": [{"message": {"content": None}}]})
            self.assertEqual(rc, 3)
            self.assertFalse(os.path.exists(os.path.join(d, "a.md")))
            self.assertTrue(os.path.exists(os.path.join(d, "a.md.empty-response.json")))


if __name__ == "__main__":
    unittest.main()
