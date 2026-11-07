class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        lens = len(s)
        if lens != len(t):
            return False

        ds = Counter(s)
        dt = Counter(t)

        return ds == dt
