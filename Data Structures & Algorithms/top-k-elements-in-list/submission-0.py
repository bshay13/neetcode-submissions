class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        freq_map = Counter(nums)  # Step 1: Count frequencies
        buckets = [[] for _ in range(len(nums) + 1)]  # Step 2: Create buckets
        
        for num, freq in freq_map.items():
            buckets[freq].append(num)  # Store number at index = frequency
        
        result = []
        for i in range(len(buckets) - 1, 0, -1):  # Step 3: Collect top-k from the highest frequency
            for num in buckets[i]:
                result.append(num)
                if len(result) == k:
                    return result