class Solution:
    def isPalindrome(self, s: str) -> bool:
        low, high = 0, len(s) - 1
        processed = s.strip().lower()

        while low < high:
            while low < high and not processed[low].isalnum():
                low += 1
            while low < high and not processed[high].isalnum():
                high -= 1
            if processed[low] != processed[high]:
                return False
            low += 1
            high -= 1
        return True
            
