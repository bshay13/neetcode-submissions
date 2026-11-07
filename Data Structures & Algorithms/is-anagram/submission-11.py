class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        ds, dt = Counter(s), Counter(t)

        return ds == dt