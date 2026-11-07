# Definition for a pair.
# class Pair:
#     def __init__(self, key: int, value: str):
#         self.key = key
#         self.value = value
class Solution:
    def quickSort(self, pairs: List[Pair]) -> List[Pair]:
        def partition(arr, low, high):
            pivot = arr[high].key  # Using the right-most element as pivot
            i = low - 1  # Index for smaller elements
            
            for j in range(low, high):
                if arr[j].key < pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]  # Swap if key is smaller than pivot
            
            arr[i + 1], arr[high] = arr[high], arr[i + 1]  # Place pivot at correct position
            return i + 1  # Return partition index

        def quicksort(arr, low, high):
            if low < high:
                pi = partition(arr, low, high)  # Get partition index
                quicksort(arr, low, pi - 1)  # Recursively sort left sub-array
                quicksort(arr, pi + 1, high)  # Recursively sort right sub-array

        quicksort(pairs, 0, len(pairs) - 1)  # Start Quick Sort
        return pairs  # Return sorted list