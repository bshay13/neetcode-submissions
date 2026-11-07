class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        map = {}
        l = 0
        res = 0

        for r in range(len(s)):
            char = s[r]

            if char in map and map[char] >= l:
                l = map[char] + 1
            
            map[char] = r

            current_window = r - l + 1
            res = max(res, current_window)
        
        return res