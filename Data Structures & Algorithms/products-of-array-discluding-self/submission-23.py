class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        
        if n < 2:
            return nums
        
        products = [1] * n

        prefix = 1
        for i in range(n):
            products[i] = prefix
            prefix *= nums[i]
        
        suffix = 1
        for j in range(n - 1, -1, -1):
            products[j] *= suffix
            suffix *= nums[j]
        
        return products