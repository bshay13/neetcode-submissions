class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        maxP = 0
        sell = prices[0]
        
        for price in prices:
            maxP = max(maxP, price - sell)
            sell = min(sell, price)
        
        return maxP