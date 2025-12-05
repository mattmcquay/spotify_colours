import unittest
from src.colours import extract_top4


class ColoursStubTests(unittest.TestCase):
    def test_extract_deterministic(self):
        a = extract_top4("https://example.com/artwork-large.jpg")
        b = extract_top4("https://example.com/artwork-large.jpg")
        self.assertEqual(a, b)
        self.assertEqual(len(a), 4)
        for c in a:
            self.assertTrue(isinstance(c, str) and c.startswith("#") and len(c) == 7)


if __name__ == "__main__":
    unittest.main()
