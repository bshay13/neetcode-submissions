class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        l = 0
        count = {}
        maxF = 0
        res = 0

        for r, c in enumerate(s):
            count[c] = count.get(c, 0) + 1
            maxF = max(maxF, count[c])

            while (r - l + 1) - maxF > k:
                count[s[l]] -= 1
                l += 1
            
            res = max(res, r - l + 1)

        return res
