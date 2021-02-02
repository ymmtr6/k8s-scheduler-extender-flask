# -*- coding : utf-8

import numpy as np
from numpy.core.numeric import True_

"""
\begin{align*}
    % \begin{array}{c}
    %     \mathrm{node1} \\
    %     \mathrm{node2} \\
    %     \mathrm{node3} \\
    %     \mathrm{node4} \\
    % \end{array}
    \left (
    \begin{array}{ccccc}
        0.30 & 0.24 & 1.0 & 3.5 & 10.25 \\
        0.90 & 0.67 & 1.0 & 3.1 & 3.7 \\
        0.85 & 0.52 & 1.0 & 3.2 & 3.9 \\
        0.78 & 0.55 & 1.0 & 3.2 & 3.9
    \end{array}
    \right )
\end{align*}

"""


class TOPSIS(object):
    """
    TOPISISにより計算する
    """

    def __init__(self, dm, weight=None, isBest=None):
        if type(dm) == list:
            dm = np.array(dm)
        if len(dm.shape) != 2:
            raise ValueError("shape Error: only 2 axis.")
        self.DM = dm
        # weight, isBest
        if weight is None:
            self.weight = np.full(dm.shape[1], 1/dm.shape[1])
        else:
            self.weight = weight
        if isBest is None:
            self.isBest = np.full(dm.shape[1], True)
        else:
            self.isBest = isBest

    def set_weight(self, weight):
        if type(weight) == list:
            weight = np.array(weight)
        self.weight = weight
        return self

    def set_isbest(self, isBest):
        if type(isBest) == list:
            isBest = np.array(isBest)
        self.isBest = isBest
        return self

    def _normalize(self):
        N = np.sqrt(np.sum(self.DM * self.DM, axis=0))
        # self.NDM = self.DM / N
        # true_divide を回避
        self.NDM = np.divide(
            self.DM, N, out=np.zeros_like(self.DM), where=N != 0)
        return self.NDM

    def _weighted_ndm(self):
        self.WNDM = self.NDM * self.weight
        return self.WNDM

    def _choise_best(self):
        max = np.max(self.WNDM, axis=0)
        min = np.min(self.WNDM, axis=0)
        self.best = np.array(
            [b if t else w for t, b, w in zip(self.isBest, max, min)])
        self.worst = np.array(
            [b if not t else w for t, b, w in zip(self.isBest, max, min)]
        )
        return self.best, self.worst

    def _separation_measure(self):
        diff = self.WNDM - self.best
        pow = diff * diff
        sum = np.sum(pow, axis=1)
        self.sm_plus = np.array([s ** 1/2 for s in sum])
        diff = self.WNDM - self.worst
        pow = diff * diff
        sum = np.sum(pow, axis=1)
        self.sm_minus = np.array([s**1/2 for s in sum])
        return self.sm_plus, self.sm_minus

    def _rc(self):
        self.last = np.array([m / (p + m)
                              for p, m in zip(self.sm_plus, self.sm_minus)])
        return np.argmax(self.last), np.argmin(self.last)

    def get_rank(self):
        self._normalize()
        self._weighted_ndm()
        self._choise_best()
        print(self.WNDM)
        print(self.best)

        self._separation_measure()
        return self._rc()


if __name__ == "__main__":
    sample = [
        [0.50, 0.64, 1.0, 3.5, 10.25],
        [0.90, 0.67, 0.0, 3.1, 0.0],
        [0.85, 0.62, 1.0, 3.2, 3.9],
        [0.78, 0.52, 1.0, 3.2, 3.9]
    ]
    weight = np.array([0.1, 0.4, 0.3, 0.2])
    isBest = np.array([True, True, True, True, True])
    print(TOPSIS(sample).set_isbest(isBest).get_rank())
