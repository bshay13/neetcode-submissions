class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        map = {}
        buckets = [[] for _ in range(len(nums) + 1)]

        for num in nums:
            map[num] = map.get(num, 0) + 1

        for num, count in map.items():
            buckets[count].append(num)
        
        top = []
        for i in range(len(buckets) - 1, -1, -1):
            for val in buckets[i]:
                top.append(val)

                if len(top) == k:
                    return top