from ymci.utils import pretty_duration, pretty_duration_round


def test_pretty_duration():
    assert pretty_duration(0) == ''
    assert pretty_duration(.001) == '1ms'
    assert pretty_duration(.125178213) == '125ms'
    assert pretty_duration(1) == '1s'
    assert pretty_duration(1.12) == '1s 120ms'
    assert pretty_duration(45) == '45s'
    assert pretty_duration(1000) == '16min 40s'
    assert pretty_duration(60) == '1min'
    assert pretty_duration(60.01) == '1min 10ms'
    assert pretty_duration(111111111.111) == (
        '3 years 6 months 11 days 11min 51s 111ms')


def test_pretty_duration_round():
    assert pretty_duration_round(0) == ''
    assert pretty_duration_round(.001) == '1ms'
    assert pretty_duration_round(.125178213) == '125ms'
    assert pretty_duration_round(1) == '1s'
    assert pretty_duration_round(1.12) == '1s'
    assert pretty_duration_round(45) == '1min'
    assert pretty_duration_round(1000) == '17min'
    assert pretty_duration_round(60) == '1min'
    assert pretty_duration_round(60.01) == '1min'
    assert pretty_duration_round(111111111.111) == '4 years'
