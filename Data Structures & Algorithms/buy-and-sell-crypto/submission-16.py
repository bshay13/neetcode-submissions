class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        bestTime = 0
        buy = prices[0]

        for price in prices:
            bestTime = max(bestTime, price - buy)
            buy = min(buy, price)
        
        return bestTime