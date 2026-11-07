class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        numsLen = len(nums)

        products = [1] * numsLen

        prefix = 1
        for i in range(numsLen):
            products[i] = prefix
            prefix *= nums[i]
        
        suffix = 1
        for j in range(numsLen - 1, -1, -1):
            products[j] *= suffix
            suffix *= nums[j]
        
        return products