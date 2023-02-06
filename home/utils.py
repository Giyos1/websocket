
import itertools
from datetime import datetime
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
        [start - keep_silence, end + keep_silence, start - _len, end + _len]
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
            range_i[1] = (last_end + next_start) // 2
            range_ii[0] = range_i[1]

        last_end1 = range_i[3]
        next_start1 = range_ii[2]
        if next_start1 < last_end1:
            range_i[3] = (last_end1 + next_start1) // 2
            range_ii[2] = range_i[3]

    return [
        [audio_segment[max(start, 0): min(end, _len)], max(start1, 0), min(end1, _len)]
        for start, end, start1, end1 in output_ranges
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


def get_time():
    current_time = datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    return get_time_to_word(str(hour)) + " dan " + get_time_to_word(str(minute)) + " daqiqa otdi"


def get_time_to_word(son) -> str:
    int_son = int(son)
    sonlar = {
        "9": "to'qqiz",
        "1": "bir",
        "2": "ikki",
        "3": "uch",
        "4": "to'rt",
        "5": "besh",
        "6": "olti",
        "7": "yetti",
        "8": "sakkiz",
        "0": "nol",
        "10": "o'n",
        "20": "yigirma",
        "30": "o'ttiz",
        "40": "qirq",
        "50": "ellik"
    }
    if int_son // 10 >= 1 and int_son % 10 != 0:
        return sonlar.get(str(int_son // 10 * 10)) + " " + sonlar.get(str(int_son % 10))
    return sonlar.get(son)


def number_to_word_uzbek(number):
    if number == 0:
        return "sifir"
    if number < 0:
        return "minus " + number_to_word_uzbek(-number)

    word = ""
    units = ["", "bir", "ikki", "uch", "to'rt", "besh", "olti", "yetti", "sakkiz", "to'qqiz"]
    tens = ["", "o'n", "yigirma", "o'ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to'qson"]
    scales = ["", "ming", "million", "milliard"]

    scale_counter = 0
    number_str = str(number)
    while number_str:
        block = number_str[-3:]
        number_str = number_str[:-3]

        block_word = ""
        block_int = int(block)
        if block_int > 99:
            block_word = block_word + units[block_int // 100] + " yuz"
            block_int = block_int % 100
        if block_int > 9:
            block_word = block_word + tens[block_int // 10]
            block_int = block_int % 10
        if block_int > 0:
            block_word = block_word + units[block_int]

        if block_word:
            if scale_counter == 0:
                word = block_word + word
            else:
                word = block_word + " " + scales[scale_counter] + " " + word
            scale_counter += 1

    return word.strip()


def replace_numbers_with_words_uzbek(sentence):
    words = sentence.split()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = number_to_word_uzbek(int(word))
        else:

            new_word = word
        new_words.append(new_word)

    return " ".join(new_words)


def translate_to_uzbek(text):
    translator = Translator('uz')
    translated_text = translator.translate(text)
    return translated_text


def get_weather():
    import requests
    api_key = "8bcf303b818a150ee52d4628a4602992"
    city = "toshkent"
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(weather_url)
    weather_data = response.json()
    return weather_data


def determine_side_of_the_world(degree):
    if 0 <= degree <= 90:
        return "shimoliy yarim shardan"
    elif 90 < degree <= 180:
        return "Sharqiy yarim shardan"
    elif 180 < degree <= 270:
        return "Janubiy yarim shardan"
    elif 270 < degree <= 360:
        return "G'arbiy yarim shardan"
    else:
        return "G'arbiy yarim shardan"


def get_weather_json_to_word():
    data = get_weather()
    weather_main = translate_to_uzbek(data.get('weather')[0].get('description'))  # tuman
    temp_date = int(data.get('main').get('temp')) - 273  # int C
    numlik_date = data.get('main').get('humidity')  # namlik %
    wind_date_speed = data.get('wind').get('speed')
    wind_date_deg = determine_side_of_the_world(data.get('wind').get('deg'))
    cloud_date = data.get('clouds').get('all')  # bulutni foizi
    text = f"toshkentimizda ob-havo {weather_main}li, havo harorati {temp_date} daraja bolishi kutulmoqda , havo namligi {numlik_date} " \
           f"foizni tashkil etadi,{wind_date_deg} sekundiga {wind_date_speed} metr tezlikda shamol esib turadi, havo bulutli bolish foizi {cloud_date} foiz"
    text = replace_numbers_with_words_uzbek(text)
    return text


if __name__ == '__main__':
    get_weather_json_to_word()
