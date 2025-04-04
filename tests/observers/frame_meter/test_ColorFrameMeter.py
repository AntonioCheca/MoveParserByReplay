from move_parser_by_replay.observers.frame_meter.ColorFrameMeter import ColorFrameMeter


def test_no_actual_color_has_less_distance_with_another_than_threshold():
    all_colors = ColorFrameMeter.ALL_COLORS

    min_distance = -1
    for first_color in all_colors:
        color = ColorFrameMeter(all_colors[first_color])
        for second_color in all_colors:
            if second_color != first_color:
                distance = color.distance_with_tuple_color(all_colors[second_color])
                if min_distance >= distance or min_distance == -1:
                    min_distance = distance

    assert min_distance >= ColorFrameMeter.THRESHOLD_FOR_DISTANCE
