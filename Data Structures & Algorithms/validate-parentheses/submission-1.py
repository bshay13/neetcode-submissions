class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        store = { ")" : "(", "]" : "[", "}" : "{" }

        for c in s:
            if c in store:
                if stack and stack[-1] == store[c]:
                    stack.pop()
                else:
                    return False
            else:
                stack.append(c)
        
        return not stack