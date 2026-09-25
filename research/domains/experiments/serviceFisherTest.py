import math


class serviceFisherTest:
    """Fisher's exact test on a 2×2 table, two-sided: how likely a split at least as uneven as the
    one seen, if the label did not depend on the arm."""

    def pValue(self, a, b, c, d):
        """a, b: the counted label and the rest in the first arm; c, d: in the second."""
        rowOne, rowTwo, columnOne = a + b, c + d, a + c
        total = rowOne + rowTwo
        if total == 0:
            return None
        observed = self._probability(a, rowOne, rowTwo, columnOne, total)
        low, high = max(0, columnOne - rowTwo), min(columnOne, rowOne)
        return min(1.0, sum(p for p in (self._probability(x, rowOne, rowTwo, columnOne, total)
                                        for x in range(low, high + 1)) if p <= observed * (1 + 1e-9)))

    @staticmethod
    def _probability(x, rowOne, rowTwo, columnOne, total):
        return (math.comb(rowOne, x) * math.comb(rowTwo, columnOne - x)) / math.comb(total, columnOne)
