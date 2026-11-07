class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        numsLen = len(nums)

        res = [1] * numsLen

        prefix = 1
        for i in range(numsLen):
            res[i] = prefix
            prefix *= nums[i]
        
        suffix = 1
        for i in range(numsLen - 1, -1, -1):
            res[i] *= suffix
            suffix *= nums[i]
        
        return res