
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


class CICFilter:
    def __init__(self, decimation=64, delay=1, stages=3):
        self.R = decimation
        self.M = delay
        self.N = stages

        # Integrator and comb delay lines
        self.integrators = [0] * self.N
        self.comb_buffers = [[0] * self.M for _ in range(self.N)]
        self.comb_indices = [0] * self.N

        self.input_count = 0

    def process_sample(self, sample):
        sample = int(sample)  # ensure it's Python int

        for i in range(self.N):
            self.integrators[i] = int(self.integrators[i] + sample)
            sample = self.integrators[i]

        self.input_count += 1

        if self.input_count == self.R:
            self.input_count = 0
            comb_input = sample

            for i in range(self.N):
                idx = self.comb_indices[i]
                delayed = self.comb_buffers[i][idx]
                self.comb_buffers[i][idx] = comb_input
                self.comb_indices[i] = (idx + 1) % self.M
                comb_input = int(comb_input - delayed)

            return comb_input
        else:
            return None

    def process(self, signal):
        output = []
        for s in signal:
            y = self.process_sample(s)
            if y is not None:
                output.append(y)
        return output


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
        defaults = dict(stages=4, delay=1)
        kwargs = {}
        kwargs.update(defaults)
        kwargs.update(filter_kwargs)
        pdm_signal = pdm_signal.astype(int)
        cic = CICFilter(decimation=decimation_factor, **kwargs)
        # Convert 1-bit PDM to +/-1 format
        pdm_signal = [2*s - 1 for s in pdm_signal.astype(int)]
        pcm_signal = cic.process(pdm_signal)
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
    pcm_data = pcm_data / (numpy.max(numpy.abs(pcm_data)) * 2.0) # normalize scale
    print(numpy.min(pcm_data), numpy.max(pcm_data), numpy.mean(pcm_data), pcm_data.dtype)


    soundfile.write(out_path, pcm_data, samplerate, subtype='PCM_16')
    print('Wrote', out_path)

if __name__ == '__main__':
    main()
