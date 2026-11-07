class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        res = []
        nums.sort()

        for i, val in enumerate(nums):
            if val > 0:
                break
            
            if i > 0 and val == nums[i - 1]:
                continue
            
            j, k = i + 1, len(nums) - 1

            while j < k:
                tot = val + nums[j] + nums[k]

                if tot > 0:
                    k -= 1
                elif tot < 0:
                    j += 1
                else:
                    res.append([val, nums[j] , nums[k]])
                    j += 1
                    k -= 1

                    while j < k and nums[j] == nums[j - 1]:
                        j += 1
                    
        return res