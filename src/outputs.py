"""Output driver abstractions and a console driver stub."""
from typing import List


class OutputDriver:
    async def connect(self) -> None:
        raise NotImplementedError

    async def send(self, colors: List[str]) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError


class ConsoleOutputDriver:
    """Simple synchronous console driver for demonstration."""

    def connect(self) -> None:
        print("ConsoleOutputDriver: connected")

    def send(self, colors: List[str]) -> None:
        print("ConsoleOutputDriver: sending pattern:")
        print(colors)

    def close(self) -> None:
        print("ConsoleOutputDriver: closed")
