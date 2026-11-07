class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        bank = {'}':'{', ']':'[', ')':'('}

        for c in s:
            if c in bank:
                if stack and bank[c] == stack[-1]:
                    stack.pop()
                else:
                    return False
            else:
                stack.append(c)

        return not stack