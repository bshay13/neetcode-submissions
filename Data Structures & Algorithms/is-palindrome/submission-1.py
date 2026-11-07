class Solution:
    def isPalindrome(self, s: str) -> bool:
        sClean = s.strip().lower()

        l, r = 0, len(sClean) - 1

        while l < r:
            while l < r and not sClean[l].isalnum():
                l += 1
            while l < r and not sClean[r].isalnum():
                r -= 1
            if sClean[l] != sClean[r]:
                return False
            l += 1
            r -= 1
        
        return True