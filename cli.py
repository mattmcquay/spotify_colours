"""Simple CLI to demonstrate the pattern generator and ConsoleOutputDriver.

Usage:
    python cli.py demo
"""
import sys
from src.colours import extract_top4, generate_pattern
from src.outputs import ConsoleOutputDriver


def demo():
    # Use a sample artwork identifier (in real use: artwork URL)
    artwork_id = "https://example.com/artwork-large.jpg"
    colours = extract_top4(artwork_id)
    pattern = generate_pattern(colours, length=16, mode="repeat")

    driver = ConsoleOutputDriver()
    driver.connect()
    driver.send(pattern)
    driver.close()


def main(argv):
    if len(argv) >= 2 and argv[1] == "demo":
        demo()
    else:
        print("Usage: python cli.py demo")


if __name__ == "__main__":
    main(sys.argv)
