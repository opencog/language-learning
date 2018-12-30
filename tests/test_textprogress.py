import unittest
from time import sleep
from src.common.textprogress import TextProgress

class TextProgressTestCase(unittest.TestCase):

    @unittest.skip
    def test_update(self):
        bar = TextProgress(total=100, desc="parsing", unit="sentences")

        for i in range(100):
            sleep(0.1)
            bar.update(1)

        bar_type = type(bar)

        del bar

        bar = bar_type(total=1000, leave=False)

        for i in range(100):
            sleep(0.1)
            bar.update(10)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
