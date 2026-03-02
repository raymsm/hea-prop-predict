import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPOSITION = "Fe:0.2,Co:0.2,Ni:0.2,Cr:0.2,Mn:0.2"


class CliEntrypointTests(unittest.TestCase):
    def run_cli(self, *cmd):
        return subprocess.run(
            [sys.executable, *cmd, COMPOSITION],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_successful_prediction(self, result):
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("--- HEA Property Prediction Results ---", result.stdout)
        self.assertIn("Density (RoM):", result.stdout)

    def test_direct_script_execution(self):
        result = self.run_cli("src/hea_predictor/cli.py")
        self.assert_successful_prediction(result)

    def test_module_execution(self):
        result = self.run_cli("-m", "src.hea_predictor.cli")
        self.assert_successful_prediction(result)


if __name__ == "__main__":
    unittest.main()
