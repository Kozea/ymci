

def pretty_duration(seconds):
    """Transform a float time in secoands to human readable duration."""

    ms = int((seconds or 0) * 1000)
    periods = [
        (' year', 1000 * 60 * 60 * 24 * 365),
        (' month', 1000 * 60 * 60 * 24 * 30),
        (' day', 1000 * 60 * 60 * 24),
        ('h', 1000 * 60 * 60),
        ('min', 1000 * 60),
        ('s', 1000),
        ('ms', 1)
    ]
    out = ''
    for name, nms in periods:
        if ms >= nms:
            val, ms = divmod(ms, nms)
            part = str(val) + name
            out += part
            if name in (' year', ' month', ' day') and val > 1:
                out += 's'
            out += ' '


    return out.strip()


def pretty_duration_abbr(seconds):
    """Transform a float time in secoands to human readable duration."""
    return pretty_duration(seconds).split(' ')[0]
