
import numpy
import soundfile
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal

from pcm2pdm import convert, convert_file, save_pdm_bin
from pdm2pcm import pdm_to_pcm, load_pdm_file
from testsignal import generate_test_tone

def plot_reconstruct(pcm_in, pdm, pcm_reconstructed, sr,
    aspect = 4.0,
    height = 3.0,
    pcm_marker = None,
    ):
    # --- Plotting using OO API ---
    
    width = height * aspect
    figheight = height * 3
    fig, axs = plt.subplots(3, 1, figsize=(width, figheight), sharex=True)

    duration = pcm_in.shape[0] / sr
    print(duration)
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Plot original PCM
    axs[0].plot(t, pcm_in, label="PCM_in", color='blue', marker=pcm_marker)
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
    axs[2].plot(t, pcm_reconstructed[:len(t)], label="PCM_rec", color='green', marker=pcm_marker)
    axs[2].set_title("Reconstructed PCM")
    axs[2].set_ylabel("Amplitude")
    axs[2].set_xlabel("Time [s]")
    axs[2].set_ylim(-1.2, 1.2)
    axs[2].grid(True)

    fig.tight_layout()
    return fig



def measure_snr_white_noise(filter_func, fs=48000, duration=1.0, noise_std=0.1, noisefloor_frequency=8000.0,
                               freq_bands=None):
    """
    Measure SNR and noise floor of a CIC filter using white noise input.
    
    Parameters:
    -----------
    filter_func : callable
        Black box filter function that takes input array and returns output array
    fs : float
        Sampling frequency (Hz)
    duration : float
        Test duration (seconds)
    noise_std : float
        Standard deviation of input white noise
    freq_bands : list of tuples
        Frequency bands for SNR analysis [(f_low, f_high), ...]
        If None, uses default bands
    
    Returns:
    --------
    dict : Contains 'metrics' (dict), 'psd_data' (DataFrame), 'time_data' (DataFrame)
    """
    
    # Generate time vector and white noise input
    t = np.arange(0, duration, 1/fs)
    N = len(t)
    
    # Generate white noise input
    input_signal = np.random.normal(0, noise_std, N)
    
    # Apply filter
    output_signal = filter_func(input_signal)
    
    # Calculate power spectral densities
    f_input, psd_input = signal.welch(input_signal, fs, nperseg=min(1024, N//4))
    f_output, psd_output = signal.welch(output_signal, fs, nperseg=min(1024, N//4))
    
    # Overall power calculations
    input_power = np.var(input_signal)
    output_power = np.var(output_signal)
    
    # Estimate noise floor from high frequency content
    # For audio, use frequencies above 20kHz as noise reference
    high_freq_idx = f_output > noisefloor_frequency
    noise_floor_psd = np.mean(psd_output[high_freq_idx])
    noise_floor_power = noise_floor_psd * fs / 2
    
    # Calculate overall SNR
    signal_power = output_power - noise_floor_power
    if signal_power <= 0:
        snr_db = -np.inf
    else:
        snr_db = 10 * np.log10(signal_power / noise_floor_power)
    
    # Frequency band analysis
    if freq_bands is None:
        freq_bands = [(20, 200), (200, 2000), (2000, 8000), (8000, 20000)]
    
    band_data = []
    for f_low, f_high in freq_bands:
        band_idx = (f_output >= f_low) & (f_output <= f_high)
        
        if np.any(band_idx):
            signal_psd_band = np.mean(psd_output[band_idx])
            band_snr_db = 10 * np.log10(signal_psd_band / noise_floor_psd)
            
            band_data.append({
                'freq_low': f_low,
                'freq_high': f_high,
                'band_name': f"{f_low:.0f}-{f_high:.0f}Hz",
                'snr_db': band_snr_db,
                'signal_psd': signal_psd_band,
                'noise_psd': noise_floor_psd
            })
    
    # Create DataFrames
    psd_data = pd.DataFrame({
        'frequency': f_output,
        'input_psd': np.interp(f_output, f_input, psd_input),
        'output_psd': psd_output,
        'frequency_response_db': 10 * np.log10(psd_output / np.interp(f_output, f_input, psd_input))
    })
    
    time_data = pd.DataFrame({
        'time': t,
        'input_signal': input_signal,
        'output_signal': output_signal
    })
    
    band_df = pd.DataFrame(band_data) if band_data else pd.DataFrame()
    
    # Metrics dictionary
    metrics = {
        'overall_snr_db': snr_db,
        'input_power_db': 10 * np.log10(input_power),
        'output_power_db': 10 * np.log10(output_power),
        'noise_floor_db': 10 * np.log10(noise_floor_power),
        'noise_floor_psd': noise_floor_psd,
        'sampling_freq': fs,
        'test_duration': duration,
        'input_noise_std': noise_std
    }
    
    return {
        'metrics': metrics,
        'psd_data': psd_data,
        'time_data': time_data,
        'band_data': band_df
    }

def plot_snr_results(results):
    """
    Plot SNR measurement results from measure_cic_snr_white_noise().
    
    Parameters:
    -----------
    results : dict
        Results dictionary from measure_cic_snr_white_noise()
    """
    
    metrics = results['metrics']
    psd_data = results['psd_data']
    time_data = results['time_data']
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Assign individual axes
    ax_time = axes[0,0]
    ax_input_psd = axes[0,1]
    ax_output_psd = axes[1,0]
    ax_freq_resp = axes[1,1]
    
    # Time domain signals (first 500 samples)
    n_samples = min(500, len(time_data))
    ax_time.plot(time_data['time'][:n_samples], time_data['input_signal'][:n_samples], 
                 'b-', alpha=0.7, label='Input')
    ax_time.plot(time_data['time'][:n_samples], time_data['output_signal'][:n_samples], 
                 'r-', alpha=0.7, label='Output')
    ax_time.set_xlabel('Time (s)')
    ax_time.set_ylabel('Amplitude')
    ax_time.set_title('Time Domain Signals')
    ax_time.legend()
    ax_time.grid(True)
    
    # Input PSD
    ax_input_psd.semilogy(psd_data['frequency'], psd_data['input_psd'], 'b-', label='Input PSD')
    ax_input_psd.set_xlabel('Frequency (Hz)')
    ax_input_psd.set_ylabel('PSD')
    ax_input_psd.set_title('Input Power Spectral Density')
    ax_input_psd.grid(True)
    
    # Output PSD with noise floor
    ax_output_psd.semilogy(psd_data['frequency'], psd_data['output_psd'], 'r-', label='Output PSD')
    ax_output_psd.axhline(metrics['noise_floor_psd'], color='k', linestyle='--', 
                         label=f'Noise Floor: {10*np.log10(metrics["noise_floor_psd"]):.1f} dB')
    ax_output_psd.set_xlabel('Frequency (Hz)')
    ax_output_psd.set_ylabel('PSD')
    ax_output_psd.set_title(f'Output PSD (SNR: {metrics["overall_snr_db"]:.1f} dB)')
    ax_output_psd.legend()
    ax_output_psd.grid(True)
    
    # Frequency response
    ax_freq_resp.semilogx(psd_data['frequency'], psd_data['frequency_response_db'], 'g-')
    ax_freq_resp.set_xlabel('Frequency (Hz)')
    ax_freq_resp.set_ylabel('Magnitude (dB)')
    ax_freq_resp.set_title('Estimated Frequency Response')
    ax_freq_resp.grid(True)

    fig.tight_layout()    
    return fig



# Example usage
def example_cic_filter(x):
    """Example CIC filter - replace with your black box function."""
    # Simple moving average with added noise
    filtered = np.convolve(x, np.ones(5)/5, mode='same')
    noise = np.random.normal(0, 0.01, len(filtered))
    return filtered + noise

if __name__ == "__main__":
    # Measurement and plotting
    results = measure_cic_snr_white_noise(
        filter_func=example_cic_filter,
        fs=48000,
        duration=2.0,
        freq_bands=[(20, 200), (200, 2000), (2000, 8000), (8000, 16000)]
    )
    
    fig = plot_snr_results(results)
    plt.show()

