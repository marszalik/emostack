import itertools
import math
import statistics


class serviceCompareArms:
    """Differences between the arms of an experiment, in plain Python.

    The unit is a run: its score is the mean of the judge's scores for one criterion in that run,
    so n is the number of repeats, not of turns (turns of one run are not independent). For each
    pair of arms: Cliff's delta (effect size without assumptions, −1..+1, |δ| ≥ 0.47 large), the
    two-sided Mann–Whitney p (exact by enumeration for small n), and a paired sign-permutation p
    over the repeats, since the arms of one repeat were judged together. With n < 4 per arm no
    test can reach p < 0.05."""

    def compare(self, perArm):
        """perArm: {arm: {repeat: score}} for one judge and one criterion."""
        rows = []
        for first, second in itertools.combinations(sorted(perArm), 2):
            a = [perArm[first][repeat] for repeat in sorted(perArm[first])]
            b = [perArm[second][repeat] for repeat in sorted(perArm[second])]
            pairs = sorted(set(perArm[first]) & set(perArm[second]))
            differences = [perArm[first][repeat] - perArm[second][repeat] for repeat in pairs]
            delta = self.cliffsDelta(a, b)
            pUnpaired = self.mannWhitney(a, b)
            pPaired = self.pairedPermutation(differences)
            row = {"a": first, "b": second, "meanA": self._mean(a), "meanB": self._mean(b), "nA": len(a),
                   "nB": len(b), "delta": None if delta is None else round(delta, 2),
                   "pUnpaired": None if pUnpaired is None else round(pUnpaired, 4),
                   "pPaired": None if pPaired is None else round(pPaired, 4), "pairs": len(differences)}
            row["verdict"] = self._verdict(row)
            rows.append(row)
        return rows

    @staticmethod
    def cliffsDelta(a, b):
        if not a or not b:
            return None
        more = sum(1 for x in a for y in b if x > y)
        less = sum(1 for x in a for y in b if x < y)
        return (more - less) / (len(a) * len(b))

    def mannWhitney(self, a, b, exactUpTo=24):
        if not a or not b:
            return None
        values = list(a) + list(b)
        ranks = self._ranks(values)
        na, nb = len(a), len(b)
        ua = sum(ranks[:na]) - na * (na + 1) / 2.0
        observed = min(ua, na * nb - ua)
        if na + nb <= exactUpTo:
            count = total = 0
            for chosen in itertools.combinations(range(na + nb), na):
                total += 1
                u = sum(ranks[i] for i in chosen) - na * (na + 1) / 2.0
                if min(u, na * nb - u) <= observed + 1e-9:
                    count += 1
            return count / total
        n = na + nb
        ties = {}
        for value in values:
            ties[value] = ties.get(value, 0) + 1
        variance = na * nb / 12.0 * ((n + 1) - sum(t ** 3 - t for t in ties.values()) / (n * (n - 1)))
        if variance <= 0:
            return 1.0
        z = (abs(ua - na * nb / 2.0) - 0.5) / math.sqrt(variance)
        return max(0.0, min(1.0, 2 * (1 - self._normal(z))))

    def pairedPermutation(self, differences, exactUpTo=20):
        nonZero = [d for d in differences if d != 0]
        if not nonZero:
            return None
        observed = abs(sum(nonZero))
        if len(nonZero) <= exactUpTo:
            count = sum(1 for signs in itertools.product((1, -1), repeat=len(nonZero))
                        if abs(sum(d * s for d, s in zip(nonZero, signs))) >= observed - 1e-9)
            return count / 2 ** len(nonZero)
        sigma = math.sqrt(sum(d * d for d in nonZero))
        return 2 * (1 - self._normal(observed / sigma)) if sigma else 1.0

    @staticmethod
    def _ranks(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            for k in range(i, j + 1):
                ranks[order[k]] = (i + j) / 2.0 + 1.0
            i = j + 1
        return ranks

    @staticmethod
    def _normal(z):
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))

    @staticmethod
    def _mean(values):
        return round(statistics.mean(values), 2) if values else None

    @staticmethod
    def _verdict(row):
        if row["nA"] < 4 or row["nB"] < 4:
            return f"too few repeats (n={row['nA']} and {row['nB']}); no test can reach p < 0.05"
        size = abs(row["delta"] or 0)
        size = "large" if size >= 0.47 else "medium" if size >= 0.33 else "small" if size >= 0.15 else "negligible"
        higher = row["a"] if (row["meanA"] or 0) > (row["meanB"] or 0) else row["b"]
        significant = row["pUnpaired"] is not None and row["pUnpaired"] < 0.05
        return (f"{'significant' if significant else 'no significant'} difference (p={row['pUnpaired']}), "
                f"{size} effect (δ={row['delta']:+.2f}); {higher} higher")
