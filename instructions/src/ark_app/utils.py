"""Module for helper functions."""

from typing import List, Any


def sort_by_index(arr: List[Any], i: int) -> None:
    """
    Sort an array in place based on the value at a specific index in each element.

    Args:
        arr: The array to be sorted.
        i: The index of the elements in the array to use for sorting.

    This function does not return anything as it modifies the input array in place.
    """
    arr.sort(key=lambda x: x[i])
