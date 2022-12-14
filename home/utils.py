import itertools

from pydub.silence import detect_nonsilent

# from the itertools documentation
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def split_on_silence(audio_segment):
    _len = len(audio_segment)
    keep_silence = 100

    output_ranges = [
        [ start - keep_silence, end + keep_silence,  start - _len, end + _len]
        for start, end in detect_nonsilent(
                audio_segment,
                min_silence_len=200,
                silence_thresh=audio_segment.dBFS - 16,
                seek_step=10,
            )
    ]

    for range_i, range_ii in pairwise(output_ranges):
        last_end = range_i[1]
        next_start = range_ii[0]
        if next_start < last_end:
            range_i[1] = (last_end+next_start)//2
            range_ii[0] = range_i[1]

        last_end1 = range_i[3]
        next_start1 = range_ii[2]
        if next_start1 < last_end1:
            range_i[3] = (last_end1+next_start1)//2
            range_ii[2] = range_i[3]

    return [
        [audio_segment[ max(start, 0) : min(end, _len) ], max(start1, 0), min(end1, _len)]
        for start,end,start1,end1 in output_ranges
    ]


def rechunk(chunks, max_length):
    if len(chunks) == 0:
        return

    chunk = None
    start = 0
    end = 999999999
    for i in range(len(chunks)):
        [_chunk, _start, _end] = chunks[i]
        if chunk is None:
            chunk = _chunk
            start = _start
            end = _end
            continue
        elif len(chunk) + len(_chunk) > max_length:
            yield [chunk, start, end]
            chunk = _chunk
            start = end
            end = _end
            continue
        else:
            chunk = chunk + _chunk
            end = _end
    yield [chunk, start, end]