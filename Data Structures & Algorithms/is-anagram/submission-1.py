class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        ls = len(s)

        if ls != len(t):
            return False

        bs, bt = {}, {}

        for i in range(ls):
            bs[s[i]] = bs.get(s[i], 0) + 1
            bt[t[i]] = bt.get(t[i], 0) + 1

        return bs == bt