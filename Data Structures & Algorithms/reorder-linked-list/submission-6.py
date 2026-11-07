# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        if head == None or head.next == None:
            return

        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        
        print('Reached second')

        curr = slow.next
        prev = None
        while curr:
            tmp = curr.next
            curr.next = prev
            prev = curr
            curr = tmp
            # print(f'{tmp.val=} {curr.val=} {prev.val=}')
        
        print('Reached third')
        
        # while prev:
        #     print(prev.val)
        #     prev = prev.next

        first, second = head, prev
        i = 0
        while second:
            tmp1, tmp2 = first, second
            first = first.next
            second = second.next
            
            print(f'{first=} {second=} {i=}')
            
            tmp1.next = tmp2
            tmp2.next = first
            # i += 1
        
        tmp2.next.next = None
        
        # while head:
        #     print(head.val)
        #     head = head.next
        
        # head.next = None