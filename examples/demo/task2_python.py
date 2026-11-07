"""Task 2: Binary Search and Array Statistics in Python.

Demonstrates interactive user input handling, list searching, and
formatted terminal output for automated lab assignment capture.
"""


def binary_search(arr, target):
    """Perform iterative binary search on a sorted list."""
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def main():
    print("=== Binary Search Demonstration ===")
    raw_input = input("Enter sorted numbers separated by spaces: ")
    numbers = [int(x) for x in raw_input.strip().split()]

    target = int(input("Enter number to search for: "))

    index = binary_search(numbers, target)

    if index != -1:
        print(f"Result: Element {target} found at index {index}.")
    else:
        print(f"Result: Element {target} not present in list.")

    print(f"Total elements: {len(numbers)}")
    print(f"Minimum value:  {min(numbers)}")
    print(f"Maximum value:  {max(numbers)}")


if __name__ == "__main__":
    main()
