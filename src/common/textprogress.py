import sys
from tqdm import tqdm
from .absclient import AbstractProgressClient


__all__ = [
    'TextProgress'
]


class TqdmFile(object):
    """Dummy file-like that will write to tqdm"""
    file = None

    def __init__(self, file):
        self.file = file

    def write(self, x):
        # Avoid print() second call (useless \n)
        if len(x.rstrip()) > 0:
            tqdm.write(x, file=self.file)

    def flush(self):
        return getattr(self.file, "flush", lambda: None)()


class TextProgress(AbstractProgressClient):
    """
    Console progress bar class
    """
    _positions = 0
    _streams = None

    def __init__(self, **kwargs):
        self.position = TextProgress._positions

        if self.position == 0:
            TextProgress._streams = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = map(TqdmFile, TextProgress._streams)

        self.bar = tqdm(position=self.position, file=sys.stdout, dynamic_ncols=True, **kwargs)
        TextProgress._positions += 1

    def __del__(self):
        if hasattr(self, "bar"):
            self.bar.close()

        TextProgress._positions -= 1

        if TextProgress._positions == 0:
            sys.stdout, sys.stderr = TextProgress._streams

    def set_total(self, total=None, leave=True, desc=None, unit="it"):
        if hasattr(self, "bar"):
            self.bar.close()
            del self.bar

        self.bar = self.bar = tqdm(total=total, leave=leave, desc=desc, unit=unit)

    def update(self, increment: int):
        self.bar.update(increment)

    def write(self, text: str) -> None:
        self.bar.write(text)
