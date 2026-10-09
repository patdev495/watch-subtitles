from main import calculate_window_bounds


def test_window_bounds_center_in_the_available_work_area() -> None:
    width, height, x, y = calculate_window_bounds((0, 0, 1920, 1040))

    assert (width, height) == (1240, 820)
    assert (x, y) == (340, 110)


def test_window_bounds_shrink_without_leaving_a_small_work_area() -> None:
    width, height, x, y = calculate_window_bounds((100, 50, 900, 650))

    assert (width, height, x, y) == (800, 600, 100, 50)


def test_window_bounds_keeps_a_small_margin_on_a_low_height_display() -> None:
    width, height, x, y = calculate_window_bounds((0, 0, 1280, 672))

    assert (width, height, x, y) == (1240, 640, 20, 16)
