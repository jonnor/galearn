
import numpy
import numpy as np
from scipy.signal import firwin, lfilter, decimate
import soundfile

def load_pdm_file(filename):
    with open(filename, 'rb') as f:
        byte_data = np.frombuffer(f.read(), dtype=np.uint8)
    bit_data = np.unpackbits(byte_data)
    # Convert to +1 (for 1s) and -1 (for 0s)
    pdm_signal = 2 * bit_data - 1
    return pdm_signal

def pdm_to_pcm(pdm_signal, decimation_factor=64):
    # Design a low-pass filter
    fir_filter = firwin(numtaps=101, cutoff=0.5/decimation_factor)
    # Filter the PDM signal
    filtered = lfilter(fir_filter, [1.0], pdm_signal)
    # Decimate (downsample)
    pcm_signal = filtered[::decimation_factor]
    return pcm_signal

def main():

    pdm_path = 'test_tone.pdm'
    out_path = 'output.wav'
    pdm_data = load_pdm_file(pdm_path)

    # Convert to PCM
    oversample = 64
    samplerate = 16000
    pcm_data = pdm_to_pcm(pdm_data, decimation_factor=oversample)

    # Normalize and save to WAV
    pcm_data = np.expand_dims(pcm_data, axis=1)
    #print(pcm_data.shape)

    print(numpy.min(pcm_data), numpy.max(pcm_data), numpy.mean(pcm_data))

    # Normalize
    pcm_data -= 128.0
    pcm_data = 2**13 * (pcm_data / np.max(np.abs(pcm_data)))

    print(numpy.min(pcm_data), numpy.max(pcm_data), numpy.mean(pcm_data))

    soundfile.write(out_path, pcm_data, samplerate)

if __name__ == '__main__':
    main()
