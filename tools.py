def map_value[T: (int, float)](
        value: T,
        in_min: T,
        in_max: T,
        out_min: T,
        out_max: T
) -> T:
    """
    maps a value from one range to another

    (https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another)
    """
    # Figure out how 'wide' each range is
    left_span = in_max - in_min
    right_span = out_max - out_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - in_min) / float(left_span)

    # Convert the 0-1 range into a value in the right range.
    return out_min + (value_scaled * right_span)


def sized_color(
        size,
        value_center: float = 7.5,
        min_val: float = 5,
        max_val: float = 10
) -> tuple[float, float, float]:
    """
    creates a gradiant for sizes
    """
    if size > value_center:
        green_val = 255 - map_value(size, value_center, max_val, 0, 255)
        blue_val = 0

    else:
        green_val = map_value(size, min_val, value_center, 0, 255)
        blue_val = (255 - map_value(size, min_val, value_center, 0, 255))

    if size < value_center:
        red_val = 0

    else:
        red_val = map_value(size, value_center, max_val, 0, 255)

    return red_val, green_val, blue_val
