class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        bankS, bankT = {}, {}

        for i in range(len(s)):
            bankS[s[i]] = bankS.get(s[i], 0) + 1
            bankT[t[i]] = bankT.get(t[i], 0) + 1

        return bankS == bankT