class Solution:
    def maxArea(self, heights: List[int]) -> int:
        maxA = 0
        l, r = 0, len(heights) - 1

        while l < r:
            height = min(heights[r], heights[l])
            width = r - l
            area = height * width
            maxA = max(maxA, area)

            if heights[l] < heights[r]:
                l += 1
            else:
                r -= 1
            
        return maxA