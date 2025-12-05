import unittest
from src.colours import generate_pattern


class PatternTests(unittest.TestCase):
    def setUp(self):
        self.colors = ["#010203", "#0A0B0C", "#AABBCC", "#112233"]

    def test_repeat(self):
        seq = generate_pattern(self.colors, length=8, mode="repeat")
        self.assertEqual(len(seq), 8)
        self.assertEqual(seq[:4], self.colors)

    def test_mirror(self):
        seq = generate_pattern(self.colors, length=8, mode="mirror")
        expected = self.colors + list(reversed(self.colors))
        self.assertEqual(seq, expected[:8])

    def test_rotate(self):
        seq = generate_pattern(self.colors, length=4, mode="rotate")
        self.assertEqual(seq, self.colors[:4])

    def test_invalid_colors(self):
        with self.assertRaises(ValueError):
            generate_pattern(["#000000"], length=4)


if __name__ == "__main__":
    unittest.main()
