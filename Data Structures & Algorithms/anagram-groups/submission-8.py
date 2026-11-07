class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        anaMap = defaultdict(list)

        for s in strs:
            counts = [0] * 26

            for char in s:
                counts[ord(char) - ord('a')] += 1
            
            anaMap[tuple(counts)].append(s)
        
        return list(anaMap.values())
