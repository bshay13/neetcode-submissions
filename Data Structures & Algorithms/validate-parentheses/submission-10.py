class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        bank = {']':'[', '}':'{', ')':'('}

        for n in s:
            if n in bank:
                if stack and bank[n] == stack[-1]:
                    stack.pop()
                else:
                    return False
            else:
                stack.append(n)
            
        return not stack