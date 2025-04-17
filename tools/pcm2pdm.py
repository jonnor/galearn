import numpy as np
import soundfile

def second_order_delta_sigma(pcm):
    # Normalize input XXX: remove normalization
    #pcm = pcm / np.max(np.abs(pcm))

    n = len(pcm)
    pdm = np.zeros(n, dtype=np.uint8)

    integrator1 = 0.0
    integrator2 = 0.0
    quantized = 0.0

    for i in range(n):
        integrator1 += pcm[i] - quantized
        integrator2 += integrator1 - quantized

        if integrator2 >= 0:
            quantized = 1.0
            pdm[i] = 1
        else:
            quantized = -1.0
            pdm[i] = 0

    return pdm

def save_pdm_bin(pdm_data, file):
    packed = np.packbits(pdm_data)
    file.write(packed)

def convert(pcm_data, oversample = 64):
    # Oversample
    pcm_upsampled = np.repeat(pcm_data, oversample)

    # --- Convert to PDM ---
    pdm_data = second_order_delta_sigma(pcm_upsampled)

    return pdm_data

def convert_file(input_file, **kwargs):
    # --- Load audio ---
    pcm_data, samplerate = soundfile.read(input_file)

    # If stereo, use one channel
    if pcm_data.ndim > 1:
        pcm_data = pcm_data[:, 0]

    pdm_data = convert(pcm_data, **kwargs)
    return pdm_data


def parse():
    import argparse

    parser = argparse.ArgumentParser(description='Process an input file and write to an output file.')
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the input file')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to the output file')
    
    args = parser.parse_args()
    return args

def main():
    args = parse()

    out_path = args.output

    pdm_data = convert_file(args.input, oversample=64)
    with open(out_path, 'wb') as f:
        save_pdm_bin(pdm_data, f)


if __name__ == '__main__':
    main()
