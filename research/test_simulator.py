import tempfile
import unittest
from pathlib import Path
from simulator import ResearchWorkspace


class SimulatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ws = ResearchWorkspace(self.tmp.name)

    def test_round_trip(self):
        for name, data in [("empty.bin", b""), ("binary.bin", bytes(range(256)) * 200),
                           ("text.txt", b"hello world")]:
            (self.ws.inputs / name).write_bytes(data)
            self.assertTrue(self.ws.simulate(name)["source_preserved"])
            self.assertTrue(self.ws.restore(name + ".sim")["verified"])
            self.assertEqual((self.ws.restored / name).read_bytes(), data)
            self.assertEqual((self.ws.inputs / name).read_bytes(), data)

    def test_no_overwrite(self):
        (self.ws.inputs / "a.txt").write_bytes(b"abc")
        self.ws.simulate("a.txt")
        with self.assertRaises(FileExistsError):
            self.ws.simulate("a.txt")
        self.ws.restore("a.txt.sim")
        with self.assertRaises(FileExistsError):
            self.ws.restore("a.txt.sim")

    def test_corrupt_artifact_preserves_original(self):
        (self.ws.inputs / "a.txt").write_bytes(b"abc")
        self.ws.simulate("a.txt")
        (self.ws.artifacts / "a.txt.sim").write_bytes(b"corrupted")
        with self.assertRaises(ValueError):
            self.ws.restore("a.txt.sim")
        self.assertEqual((self.ws.inputs / "a.txt").read_bytes(), b"abc")

    def test_reject_path_traversal(self):
        with self.assertRaises(ValueError):
            self.ws.simulate("../secret.txt")


if __name__ == "__main__":
    unittest.main()
