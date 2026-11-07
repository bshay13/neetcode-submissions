# Definition for a pair.
# class Pair:
#     def __init__(self, key: int, value: str):
#         self.key = key
#         self.value = value
class Solution:
    def quickSort(self, pairs: List[Pair]) -> List[Pair]:
        def partition(arr, low, high):
            pivot = arr[high].key  # Use the right-most element as pivot
            i = low - 1  # Pointer for smaller element
            
            for j in range(low, high):
                if arr[j].key < pivot:  # Place elements smaller than pivot to the left
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            
            arr[i + 1], arr[high] = arr[high], arr[i + 1]  # Place pivot in correct position
            return i + 1
        
        def quick_sort_helper(arr, low, high):
            if low < high:
                pi = partition(arr, low, high)  # Get partition index
                quick_sort_helper(arr, low, pi - 1)
                quick_sort_helper(arr, pi + 1, high)
        
        quick_sort_helper(pairs, 0, len(pairs) - 1)
        return pairs