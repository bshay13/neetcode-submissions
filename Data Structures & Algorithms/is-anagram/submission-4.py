class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        ds, dt = {}, {}
        for n in s:
            ds[n] = ds.get(n, 0) + 1

        for m in t:
            dt[m] = dt.get(m, 0) + 1
        
        return ds == dt
