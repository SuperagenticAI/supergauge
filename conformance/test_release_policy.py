"""Run shared release-policy cases against the protocol checker."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check


class ReleasePolicyTests(unittest.TestCase):
    def test_shared_cases(self):
        cases = json.loads(
            (Path(__file__).parent / "fixtures/release-policy.json").read_text()
        )
        for case in cases:
            with self.subTest(case=case["name"]):
                record = case["record"]
                result = check.Result()
                for validate in (
                    check.check_l1,
                    check.check_l2,
                    check.check_l3,
                    check.check_l4,
                ):
                    validate(record, result)
                self.assertEqual(result.level, case["level"], result.failures)
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "record.json"
                    path.write_text(json.dumps(record))
                    process = subprocess.run(
                        [
                            sys.executable,
                            str(Path(check.__file__)),
                            str(path),
                            "--level",
                            "L1",
                            "--require-ship",
                            "--quiet",
                        ],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(
                        process.returncode,
                        0 if case["release_permitted"] else 1,
                        process.stdout + process.stderr,
                    )


if __name__ == "__main__":
    unittest.main()
