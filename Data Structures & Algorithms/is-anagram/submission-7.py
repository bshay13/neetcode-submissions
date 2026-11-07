class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        ds = Counter(s)
        dt = Counter(t)

        return ds == dt