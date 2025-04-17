
import numpy
import soundfile
import numpy as np
import matplotlib.pyplot as plt

from pcm2pdm import convert, convert_file, save_pdm_bin
from pdm2pcm import pdm_to_pcm, load_pdm_file
from testsignal import generate_test_tone

def plot_reconstruct(pcm_in, pdm, pcm_reconstructed, sr, aspect = 4.0, height = 3.0):
    # --- Plotting using OO API ---
    
    width = height * aspect
    figheight = height * 3
    fig, axs = plt.subplots(3, 1, figsize=(width, figheight), sharex=True)

    duration = pcm_in.shape[0] / sr
    print(duration)
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Plot original PCM
    axs[0].plot(t, pcm_in, label="PCM_in", color='blue')
    axs[0].set_title("Original PCM")
    axs[0].set_ylabel("Amplitude")
    axs[0].set_ylim(-1.2, 1.2)
    axs[0].grid(True)

    # Plot PDM bitstream
    time_pdm = np.linspace(0, duration, len(pdm), endpoint=False)
    axs[1].step(time_pdm, pdm, where='mid', color='black')
    axs[1].set_title("PDM Bitstream")
    axs[1].set_ylabel("Bit")
    axs[1].set_ylim(-0.2, 1.2)
    axs[1].grid(True)

    # Plot reconstructed PCM
    axs[2].plot(t, pcm_reconstructed[:len(t)], label="PCM_rec", color='green')
    axs[2].set_title("Reconstructed PCM")
    axs[2].set_ylabel("Amplitude")
    axs[2].set_xlabel("Time [s]")
    axs[2].set_ylim(-1.2, 1.2)
    axs[2].grid(True)

    fig.tight_layout()
    return fig

def test_sine():

    # temp files
    pcm_file = 'test.wav'
    pdm_file = 'test.pdm'

    # Generate test data
    oversample = 32
    sample_rate = 16000
    signal = generate_test_tone(sample_rate=sample_rate,
        duration_sec=1.000, freqs=[1000.0], noise_level=0.0)
    pcm = signal
    soundfile.write(pcm_file, signal, sample_rate)

    # Convert to PDM

    pdm_data = convert_file(pcm_file, oversample=oversample)
    with open(pdm_file, 'wb') as f:
        save_pdm_bin(pdm_data, f)

    pdm_loaded = load_pdm_file(pdm_file)

    numpy.testing.assert_equal(pdm_loaded, pdm_data)

    print(pdm_data)
    print(pdm_loaded)

    # PDM to PCM conversion
    pcm_reconstructed = pdm_to_pcm(pdm_loaded, decimation_factor=oversample)

    # Remove DC offset
    pcm_reconstructed -= numpy.mean(pcm_reconstructed)

    fig = plot_reconstruct(pcm, pdm_loaded, pcm_reconstructed, sr=sample_rate)
    print(fig.axes)
    offset = 0.2
    fig.axes[0].set_xlim(offset+0.0010,offset+0.0020)

    plot_path = 'test.png'
    fig.savefig(plot_path)
    print(f'Saved {plot_path}')

if __name__ == '__main__':
    test_sine()
