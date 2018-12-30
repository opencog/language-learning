from tqdm import tqdm
from .absclient import AbstractProgressClient

class TextProgress(AbstractProgressClient):
    """
    Console progress bar class
    """
    _positions = 0

    def __init__(self, **kwargs):
        self.position = TextProgress._positions
        self.bar = tqdm(position=self.position, **kwargs)
        TextProgress._positions += 1

    def __del__(self):
        if hasattr(self, "bar"):
            self.bar.close()

    def set_total(self, total=None, leave=True, desc=None, unit="it"):
        if hasattr(self, "bar"):
            self.bar.close()
            del self.bar

        self.bar = self.bar = tqdm(total=total, leave=leave, desc=desc, unit=unit)

    def update(self, increment: int):
        self.bar.update(increment)

    def write(self, text: str) -> None:
        self.bar.write(text)