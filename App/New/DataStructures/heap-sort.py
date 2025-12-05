
# base code written by Zach M.
# referenced: https://www.geeksforgeeks.org/dsa/python-program-for-heap-sort/
def heap(lst, size, index):
    running = True
    while running:
        largest = index         # set largest to current index (should be at the "root")
        left = 2 * index + 1        # setup left and right indices
        right = 2 * index + 2


        # Check that left index is not deeper than the size of the "heap"
        # Check if value at left index is larger than the value at the index stored in largest
        if left < size and lst[left] > lst[largest]:
            largest = left

        # Check that right index is not deeper than the size of the "heap"
        # Check if value at right index is larger than the value at the index stored in largest
        if right < size and lst[right] > lst[largest]:
            largest = right

        # if the largest value changed swap the original index and largest index
        # if the largest value remains end loop
        if largest != index:
            lst[index], lst[largest] = lst[index], lst[index]
            index = largest
        else:
            running = False

# Base code written by Zach M.
# referenced: https://www.geeksforgeeks.org/dsa/python-program-for-heap-sort/
def heap_sort(lst):
    size = len(lst)

    # organize list into a heap
    for i in range(size // 2 - 1, -1, -1):
        heap(lst, size, i)


    for i in range(size-1, 0, -1):
        # swap root with last element
        lst[i], lst[0] = lst[0], lst[i]

        # re-heap with the new root, size will be reduced by one for each loop
        heap(lst, i, 0)


# This is a test
def test():
    lst = [5,1,6,7,2,4]
    heap_sort(lst)
    print(lst)