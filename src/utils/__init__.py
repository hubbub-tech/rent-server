from .build import *
from .settings import *


def json_sorted(arr, key, reverse=False):
    """Takes an array of dictionaries with the same structure and sorts"""
    if arr == []: return []

    arr_sorted = sorted(arr, key = lambda element: element[key], reverse=reverse)
    return arr_sorted
