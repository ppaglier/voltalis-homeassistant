from typing import Generator


def pretty_dictdiffer(diff: Generator | list) -> str:
    """Pretty display of a dict diff difference.

    Arguments
    ---------
    diff
        Iterator result of the dictdiffer.diff function or list generator from the iterator

    Example
    -------
    >>> from dictdiffer import diff
    >>> pretty_dictdiffer(diff([1, 20.3, "element"], [1, 20.35]))
    * change [1] (20.3, 20.35)
    * remove [(2, 'element')]
    """
    # Get the list of difference in list of tuple format
    diff_list = diff if isinstance(diff, list) else list(diff)
    # Return difference message
    if diff_list:
        return "* " + "\n* ".join(" ".join(str(e) for e in diff_element) for diff_element in diff_list)
    return ""
