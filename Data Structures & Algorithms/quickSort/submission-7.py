# Definition for a pair.
# class Pair:
#     def __init__(self, key: int, value: str):
#         self.key = key
#         self.value = value
class Solution:
    def quickSort(self, pairs: List[Pair]) -> List[Pair]:
        def partition(arr, low, high):
            pivot = arr[high].key
            i = low - 1

            for j in range(low, high):
                if arr[j].key < pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                
            arr[i + 1], arr[high] = arr[high], arr[i + 1]

            return i + 1

        def quicksort_helper(arr, low, high):
            if low < high:
                pi = partition(arr, low, high)
                quicksort_helper(arr, low, pi - 1)
                quicksort_helper(arr, pi + 1, high)
            
        quicksort_helper(pairs, 0, len(pairs) - 1)
        return pairs