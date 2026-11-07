class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        maxP = 0
        buy = prices[0]

        for sell in prices:
            buy = min(buy, sell)
            maxP = max(maxP, sell - buy)
        
        return maxP