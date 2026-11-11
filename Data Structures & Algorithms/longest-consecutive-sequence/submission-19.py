class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        numsSet = set(nums)
        longest = 0

        for num in numsSet:
            if num - 1 not in numsSet:
                count = 1

                while num + count in numsSet:
                    count += 1
                
                longest = max(longest, count)

        return longest