# Definition for a pair.
# class Pair:
#     def __init__(self, key: int, value: str):
#         self.key = key
#         self.value = value
class Solution:
    def quickSort(self, pairs: List[Pair]) -> List[Pair]:
        if not pairs:
            return []
        
        self.quickSortHelper(pairs, 0, len(pairs) - 1)
        return pairs
    
    def partition(self, arr: List[Pair], s: int, e: int) -> int:
        pivot = arr[e]
        left = s

        for i in range(s, e):
            if arr[i].key < pivot.key:
                arr[left], arr[i] = arr[i], arr[left]
                left += 1
            
        arr[left], arr[e] = arr[e], arr[left]
        return left
    
    def quickSortHelper(self, arr: List[Pair], s: int, e: int) -> None:
        while s < e:
            pivot_index = self.partition(arr, s, e)

            if pivot_index - s < e - pivot_index:
                self.quickSortHelper(arr, s, pivot_index - 1)
                s = pivot_index + 1
            else:
                self.quickSortHelper(arr, pivot_index + 1, e)
                e = pivot_index - 1