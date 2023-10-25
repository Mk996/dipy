"""Utility functions for horizon.
"""


def check_img_shapes(images):
    """
    Checks if the images have same shapes
    """

    # No need to check if there is less than 2 images
    if len(images) < 2:
        return False
    base_shape = images[0][0].shape[:3]
    for img in images:
        data, _ = img
        if base_shape != data.shape[:3]:
            return False
    return True


def fetch_centered_value(value_range, current_value):
    """Calculate current value relative to center.

    Parameters
    ----------
    value_range : (float, float)
        min and max value of the value_range
    current_value : float
        current value on zero based scale

    Return
    ------
    (current_value: float, mid: float)
    """
    mid = (value_range[0] + value_range[1]) / 2
    return (current_value - mid, mid)
