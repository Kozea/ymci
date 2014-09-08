from ymci.utils import pretty_duration, pretty_duration_abbr


def test_pretty_duration():
    assert pretty_duration(.001) == '1ms'
    assert pretty_duration(.125178213) == '125ms'
    assert pretty_duration(1) == '1s'
    assert pretty_duration(1.12) == '1s 120ms'
    assert pretty_duration(45) == '45s'
    assert pretty_duration(1000) == '16min 40s'
    assert pretty_duration(60) == '1min'
    assert pretty_duration(60.01) == '1min 10ms'
    assert pretty_duration(111111111.111) == (
        '3 years 6 months 11 days 11min 51s 111ms')


def test_pretty_duration_abbr():
    assert pretty_duration_abbr(.001) == '1ms'
    assert pretty_duration_abbr(.125178213) == '125ms'
    assert pretty_duration_abbr(1) == '1s'
    assert pretty_duration_abbr(1.12) == '1s'
    assert pretty_duration_abbr(45) == '45s'
    assert pretty_duration_abbr(1000) == '16min'
    assert pretty_duration_abbr(60) == '1min'
    assert pretty_duration_abbr(60.01) == '1min'
    assert pretty_duration_abbr(111111111.111) == '3 years'
