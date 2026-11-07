class Solution:
    def search(self, nums: List[int], target: int) -> int:
        l, r = 0, len(nums) - 1

        while l <= r:
            guess = (l + r) // 2

            if target > nums[guess]:
                l = guess + 1
            elif target < nums[guess]:
                r = guess - 1
            else:
                return guess

        return -1