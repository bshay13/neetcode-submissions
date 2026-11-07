class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        numsLen = len(nums)

        products = [0] * numsLen

        prefix = 1
        for i in range(numsLen):
            products[i] = prefix
            prefix *= nums[i]
        
        suffix = 1
        for i in range(numsLen - 1, -1, -1):
            products[i] *= suffix
            suffix *= nums[i]
        
        return products