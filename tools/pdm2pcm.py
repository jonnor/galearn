
import numpy
import numpy as np
from scipy.signal import firwin, lfilter, decimate
import soundfile

def load_pdm_file(filename):
    with open(filename, 'rb') as f:
        byte_data = np.frombuffer(f.read(), dtype=np.uint8)
    bit_data = np.unpackbits(byte_data)
    # Convert to +1 (for 1s) and -1 (for 0s)
    #pdm_signal = 2 * bit_data - 1
    pdm_signal = bit_data
    return pdm_signal


def cic_decimate(input_signal, decimation_factor=64, stages=3, delay=1):
    R = decimation_factor
    N = stages
    M = delay

    # Integrator stages
    integrators = [0] * N
    integrator_outputs = []

    for sample in input_signal:
        integrators[0] += sample
        for i in range(1, N):
            integrators[i] += integrators[i-1]
        integrator_outputs.append(integrators[-1])

    # Decimation
    decimated = integrator_outputs[R-1::R]

    # Comb stages
    combs = [0] * N
    comb_outputs = []
    delays = [[0]*M for _ in range(N)]

    for sample in decimated:
        diff = sample
        for i in range(N):
            delayed = delays[i].pop(0)
            delays[i].append(diff)
            diff = diff - delayed
            combs[i] = diff
        comb_outputs.append(combs[-1])

    return comb_outputs


def pdm_to_pcm(pdm_signal, decimation_factor=64, filter_type='fir', filter_kwargs={}):
    if filter_type == 'fir':
        # Design a low-pass filter
        defaults = dict(numtaps=501, cutoff=0.5/decimation_factor)
        kwargs = {}
        kwargs.update(defaults)
        kwargs.update(filter_kwargs)
        fir_filter = firwin(**kwargs)
        # Filter the PDM signal
        filtered = lfilter(fir_filter, [1.0], pdm_signal)
        # Decimate (downsample)
        pcm_signal = filtered[::decimation_factor]

    elif filter_type == 'cic':
        # Use CIC filter
        defaults = dict(stages=3, delay=1)
        kwargs = {}
        kwargs.update(defaults)
        kwargs.update(filter_kwargs)
        # Convert 1-bit PDM to +/-1 format
        print(pdm_signal)
        pdm_signal = pdm_signal.astype(int)
        #pdm_signal = [2*s - 1 for s in pdm_signal.astype(int)]
        pcm_signal = cic_decimate(pdm_signal, decimation_factor=decimation_factor, **kwargs) 
        pcm_signal = numpy.array(pcm_signal, dtype=float)

    return pcm_signal

def parse():
    import argparse

    parser = argparse.ArgumentParser(description='Process an input file and write to an output file.')
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the input file')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to the output file')
    parser.add_argument('--filter', type=str, default='fir')
    parser.add_argument('--samplerate', type=int, default=16000)
    parser.add_argument('--oversample', type=int, default=64)
    
    args = parser.parse_args()
    return args

def main():
    args = parse()

    pdm_path = args.input
    out_path = args.output
    pdm_data = load_pdm_file(pdm_path)

    print('loaded', pdm_data.shape)

    # Convert to PCM
    oversample = args.oversample
    samplerate = args.samplerate
    pcm_data = pdm_to_pcm(pdm_data, decimation_factor=oversample, filter_type=args.filter)

    # Normalize and save to WAV
    pcm_data = np.expand_dims(pcm_data, axis=1)
    #print(pcm_data.shape)

    pcm_data -= numpy.mean(pcm_data) # remove DC offset
    print(numpy.min(pcm_data), numpy.max(pcm_data), numpy.mean(pcm_data), pcm_data.dtype)

    soundfile.write(out_path, pcm_data, samplerate)
    print('Wrote', out_path)

if __name__ == '__main__':
    main()
