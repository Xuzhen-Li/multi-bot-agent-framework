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


if __name__ == "__main__":
    unittest.main()
