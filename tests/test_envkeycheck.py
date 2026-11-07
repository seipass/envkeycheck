import pathlib
import subprocess
import sys
import tempfile
import unittest

from envkeycheck import compare_key_sets, parse_env_keys


class ParseEnvKeysTests(unittest.TestCase):
    def test_parses_assignments_without_returning_values(self):
        keys, invalid_lines = parse_env_keys(
            """# sample

API_URL=https://private.example
export API_TOKEN='private-token'
EMPTY=
"""
        )

        self.assertEqual(keys, {"API_URL", "API_TOKEN", "EMPTY"})
        self.assertEqual(invalid_lines, [])

    def test_returns_line_numbers_for_non_assignment_lines(self):
        keys, invalid_lines = parse_env_keys(
            """GOOD=hidden-value
not an assignment: leaked-value
"""
        )

        self.assertEqual(keys, {"GOOD"})
        self.assertEqual(invalid_lines, [2])

    def test_compare_reports_missing_and_extra_keys(self):
        missing, extra = compare_key_sets({"A", "B"}, {"B", "C"})

        self.assertEqual(missing, {"A"})
        self.assertEqual(extra, {"C"})


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "envkeycheck", *map(str, args)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_cli_returns_zero_for_matching_key_sets(self):
        with tempfile.TemporaryDirectory() as directory:
            first = pathlib.Path(directory, ".env.example")
            second = pathlib.Path(directory, ".env.production")
            first.write_text(
                """API_KEY=example-secret
PORT=3000
""",
                encoding="utf-8",
            )
            second.write_text(
                """PORT=9000
API_KEY=production-secret
""",
                encoding="utf-8",
            )

            result = self.run_cli(first, second)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("match", result.stdout.lower())
        self.assertNotIn("secret", result.stdout + result.stderr)

    def test_cli_returns_one_for_key_mismatch_without_printing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            first = pathlib.Path(directory, ".env.example")
            second = pathlib.Path(directory, ".env.production")
            first.write_text(
                """KEEP=example-secret
NEEDED=sample-secret
""",
                encoding="utf-8",
            )
            second.write_text(
                """KEEP=prod-secret
EXTRA=private-secret
""",
                encoding="utf-8",
            )

            result = self.run_cli(first, second)

        self.assertEqual(result.returncode, 1)
        self.assertIn("NEEDED", result.stdout)
        self.assertIn("EXTRA", result.stdout)
        self.assertNotIn("secret", result.stdout + result.stderr)

    def test_cli_returns_two_for_malformed_line_without_echoing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            first = pathlib.Path(directory, ".env.example")
            second = pathlib.Path(directory, ".env.production")
            first.write_text("GOOD=ok\n", encoding="utf-8")
            second.write_text("BAD PRIVATE_VALUE\n", encoding="utf-8")

            result = self.run_cli(first, second)

        self.assertEqual(result.returncode, 2)
        self.assertIn(":1:", result.stderr)
        self.assertNotIn("PRIVATE_VALUE", result.stdout + result.stderr)

    def test_cli_returns_two_for_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            reference = pathlib.Path(directory, ".env.example")
            missing = pathlib.Path(directory, "not-a-real-env-file")
            reference.write_text("GOOD=ok\\n", encoding="utf-8")

            result = self.run_cli(reference, missing)

        self.assertEqual(result.returncode, 2)
        self.assertIn("not-a-real-env-file", result.stderr)


if __name__ == "__main__":
    unittest.main()
