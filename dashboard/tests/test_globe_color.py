"""Unit tests for lib/globe/color.py."""
from lib.globe.color import diverging_color, sequential_color, value_to_width


def test_diverging_color_at_zero_is_zero_anchor():
    zero = (71, 85, 105)
    r, g, b, _ = diverging_color(0.0, neg_anchor=(50, 140, 80), zero_anchor=zero, pos_anchor=(180, 70, 70))
    assert (r, g, b) == zero


def test_diverging_color_pos_one_reaches_pos_anchor():
    r, g, b, _ = diverging_color(1.0, neg_anchor=(50, 140, 80), zero_anchor=(71, 85, 105), pos_anchor=(180, 70, 70))
    assert r == 180 and g == 70 and b == 70


def test_diverging_color_neg_one_reaches_neg_anchor():
    r, g, b, _ = diverging_color(-1.0, neg_anchor=(50, 140, 80), zero_anchor=(71, 85, 105), pos_anchor=(180, 70, 70))
    assert r == 50 and g == 140 and b == 80


def test_diverging_color_alpha_scales_with_magnitude():
    _, _, _, a_weak = diverging_color(0.1, (0, 0, 0), (128, 128, 128), (255, 255, 255), alpha_range=(70, 200))
    _, _, _, a_strong = diverging_color(0.9, (0, 0, 0), (128, 128, 128), (255, 255, 255), alpha_range=(70, 200))
    assert a_weak < a_strong


def test_diverging_color_clamps_outside_range():
    assert diverging_color(2.0, (0, 0, 0), (128, 128, 128), (255, 255, 255)) == \
           diverging_color(1.0, (0, 0, 0), (128, 128, 128), (255, 255, 255))
    assert diverging_color(-2.0, (0, 0, 0), (128, 128, 128), (255, 255, 255)) == \
           diverging_color(-1.0, (0, 0, 0), (128, 128, 128), (255, 255, 255))


def test_sequential_color_at_zero_is_low_anchor():
    low = (50, 160, 80)
    r, g, b, _ = sequential_color(0.0, low_anchor=low, high_anchor=(180, 50, 50))
    assert (r, g, b) == low


def test_sequential_color_at_one_is_high_anchor():
    high = (180, 50, 50)
    r, g, b, _ = sequential_color(1.0, low_anchor=(50, 160, 80), high_anchor=high)
    assert (r, g, b) == high


def test_sequential_color_clamps():
    assert sequential_color(2.0, (0, 0, 0), (255, 255, 255)) == \
           sequential_color(1.0, (0, 0, 0), (255, 255, 255))


def test_value_to_width_min_at_zero():
    assert value_to_width(0.0, min_w=0.8, max_w=3.0) == 0.8


def test_value_to_width_max_at_one():
    assert value_to_width(1.0, min_w=0.8, max_w=3.0) == 3.0


def test_value_to_width_uses_abs():
    assert value_to_width(-0.5) == value_to_width(0.5)
