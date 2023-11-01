"""Utility functions for horizon.
"""
import numpy as np


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


def select_deselect_actors(actors, elevation=0.001):
    """Push actors to front by the elevation.

    Parameters
    ----------
    actors : list(actor)
        list of actors which needs to be on front or pushed back.
    elevation: float, optional
        value with which the actors should be brought to front or pushed back,
        by default 0.001.
        To push it back provide elevation < 0 values.
    """
    for act in actors:
        act.SetPosition(
            tuple(
                np.array(act.GetPosition()) + elevation
            )
        )


def center_relative_value(value, value_range):
    """Calculate center relative value of the min_value based quantity.

    Parameters
    ----------
    value : int
        min_value base quantity.
    value_range : tuple
        tuple of (min_value, max_value).

    Returns
    -------
    int
        center relative value.
    """
    mid = int((value_range[0] + value_range[1]) / 2)
    return value - mid


def zero_relative_value(value, value_range):
    """Calculate zero relative value of the center relative quantity.

    Parameters
    ----------
    value : int
        center relative quantity.
    value_range : tuple
        tuple of (min_value, max_value).

    Returns
    -------
    int
        center relative value.
    """
    mid = int((value_range[0] + value_range[1]) / 2)
    return mid + value
