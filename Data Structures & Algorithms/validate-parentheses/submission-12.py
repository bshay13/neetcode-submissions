class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        bank = {']': '[', '}': '{', ')': '('}

        for char in s:
            if char in bank:
                if not stack or stack[-1] != bank[char]:
                    return False
                stack.pop()
            else:
                stack.append(char)
        
        return not stack