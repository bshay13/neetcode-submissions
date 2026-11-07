class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        bank = {}

        for i in range(len(nums)):
            diff = target - nums[i]
            if diff in bank:
                return [bank[diff], i]

            bank[nums[i]] = i

        return []