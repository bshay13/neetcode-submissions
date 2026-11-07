class Solution:
    def isPalindrome(self, s: str) -> bool:
        lowS = s.strip().lower()

        l, r = 0, len(lowS) - 1

        while l < r:
            while l < r and not lowS[l].isalnum():
                l += 1
            while l < r and not lowS[r].isalnum():
                r -= 1
            if lowS[l] != lowS[r]:
                return False
            l += 1
            r -= 1
            
        return True