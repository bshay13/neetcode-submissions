class Solution:
    def maxArea(self, heights: List[int]) -> int:
        l, r = 0, len(heights) - 1
        maximum = 0

        while l < r:
            height = min(heights[l], heights[r])
            width = r - l
            area = height * width
            maximum = max(maximum, area)

            while l < r and heights[l] <= height:
                l += 1
            while l < r and heights[r] <= height:
                r -= 1
        
        return maximum