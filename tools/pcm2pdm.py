import numpy as np
import soundfile

def second_order_delta_sigma(pcm):

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

def first_order_delta_sigma(pcm):
    n = len(pcm)
    pdm = np.zeros(n, dtype=np.uint8)
    integrator = 0.0
    quantized = 0.0
    for i in range(n):
        integrator += pcm[i] - quantized
        if integrator >= 0:
            quantized = 1.0
            pdm[i] = 1
        else:
            quantized = -1.0
            pdm[i] = 0
    return pdm

def convert(pcm_data, oversample = 64, order=2):
    # Oversample
    pcm_upsampled = np.repeat(pcm_data, oversample)

    # --- Convert to PDM ---
    if order == 1:
        pdm_data = first_order_delta_sigma(pcm_upsampled)
    elif order == 2:
        pdm_data = second_order_delta_sigma(pcm_upsampled)

    return pdm_data

def save_pdm_bin(pdm_data, file):
    packed = np.packbits(pdm_data)
    file.write(packed)

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
    #parser.add_argument('--samplerate', type=int, default=16000)
    parser.add_argument('--oversample', type=int, default=64)    

    args = parser.parse_args()
    return args

def main():
    args = parse()

    out_path = args.output

    pdm_data = convert_file(args.input, oversample=args.oversample)
    with open(out_path, 'wb') as f:
        save_pdm_bin(pdm_data, f)

    print('Wrote', out_path)

if __name__ == '__main__':
    main()
