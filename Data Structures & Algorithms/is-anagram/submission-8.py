class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        
        bs = Counter(s)
        bt = Counter(t)

        return bs == bt