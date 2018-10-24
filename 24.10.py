import wave
import pyaudio


def input_wave(filename, frames=10000000):  # 10000000 is an arbitrary large number of frames
    with wave.open(filename, 'rb') as wave_file:
        params = wave_file.getparams()
        audio = wave_file.readframes(frames)
    return params, audio

def output_wave(audio, params, stem, suffix):
    # dynamically format the filename by passing in data
    filename = stem.replace('.wav', '_{}.wav'.format(suffix))
    with wave.open(filename, 'wb') as wave_file:
        wave_file.setparams(params)
        wave_file.writeframes(audio)


from audioop import add, mul


def delay(audio_bytes, params, offset_ms, factor=1, num=1):
    """version 4: 'num' delays after 'offset_ms' milliseconds amplified by 'factor'
    with additional space"""
    if factor >= 1:
        warn("These settings may produce a very loud audio file. \
              Please use caution when listening")
    # calculate the number of bytes which corresponds to the offset in milliseconds
    offset = params.sampwidth * offset_ms * int(params.framerate / 1000)
    # add extra space at the end for the delays
    audio_bytes = audio_bytes + b'\0' * offset * (num)
    # create a copy of the original to apply the delays
    delayed_bytes = audio_bytes
    for i in range(num):
        # create some silence
        beginning = b'\0' * offset * (i + 1)
        # remove space from the end
        end = audio_bytes[:-offset * (i + 1)]
        # multiply by the factor
        multiplied_end = mul(end, params.sampwidth, factor ** (i + 1))
        delayed_bytes = add(delayed_bytes, beginning + multiplied_end, params.sampwidth)
    return delayed_bytes


from IPython.display import Audio, display, HTML


def delay_to_file(audio_bytes, params, offset_ms, file_stem, factor=1, num=1):
    echoed_bytes = delay(audio_bytes, params, offset_ms, factor, num)
    output_wave(echoed_bytes, params, file_stem,
                'delay_{}ms_{}f_{}n'.format(offset_ms, factor, num))


def saving_of_recording():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

saving_of_recording()

trumpet_params, trumpet_bytes = input_wave('output.wav')
delay_to_file(trumpet_bytes, trumpet_params, offset_ms=50, file_stem='output.wav',
              factor=.7)

delay_to_file(trumpet_bytes, trumpet_params, offset_ms=50, file_stem='output.wav',
              factor=.7)