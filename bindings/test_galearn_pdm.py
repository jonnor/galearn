
"""
Test the PDM filter
"""

import time
import os
import sys
import math

import numpy
import pandas
import pytest

from pcm2pdm import convert
from testsignal import generate_test_tone
from test_pdm import plot_reconstruct, measure_snr_white_noise, plot_snr_results, measure_frequency_response, plot_filter_response
import galearn_pdm

SAMPLERATE_DEFAULT = 16000
DECIMATION = 64

# a place to put diagnostic outputs, like plots etc
here = os.path.dirname(__file__)
out_dir = os.path.join(here, 'out')

enable_plotting = bool(int(os.environ.get('TEST_ENABLE_PLOTS', '1')))

def ensure_dir_for_file(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def find_forward_shift(reference, signal, max_shift=None):
    np = numpy
    from scipy.signal import correlate
    
    correlation = correlate(signal, reference, mode='full')
    lags = np.arange(-len(reference) + 1, len(signal))
    
    # Keep only non-negative lags
    positive_mask = lags >= 0
    if max_shift:
        positive_mask &= (lags <= max_shift)
    
    if not np.any(positive_mask):
        return None
        
    correlation = correlation[positive_mask]
    lags = lags[positive_mask]
    
    df = pandas.DataFrame({
        'lag': lags,
        'correlation': correlation,
    })
    #print(df)

    shift = lags[np.argmax(correlation)]
    return shift


# TODO: test closer to Nyquist (sr/2), like 6 Khz for 16 khz samplerate
# Need to take gain reduction/shift into account, since CIC filter has a falloff at high frequencies
@pytest.mark.parametrize('frequency', [50, 250, 2000])
def test_sine_simple(frequency):
    function = sys._getframe().f_code.co_name # looks up function name
    test_name = f'{function},frequency={frequency}' 
    sr = SAMPLERATE_DEFAULT
    test_duration = 10 * (1/frequency) # have a reasonable set of samples

    # Generate test data
    pcm_input = generate_test_tone(duration_sec=test_duration,
        freqs=[frequency], noise_level=0.0, sample_rate=sr, amplitude=0.9,
    )
    pdm_input = convert(pcm_input)
    out = numpy.zeros(shape=math.ceil(len(pdm_input)/DECIMATION), dtype=numpy.int16)

    # Process using filter
    n_samples = galearn_pdm.process(pdm_input, out, 0, 0)
    out = out / (2**12)

    # Compensate for delay through filter
    delay = find_forward_shift(pcm_input, out)
    out_shifted = out[delay:-1]
    input_trimmed = pcm_input[:len(out_shifted)]
    #out_shifted = out_shifted[5:-5]
    #input_trimmed = input_trimmed[5:-5]
    error = out_shifted - input_trimmed

    # Plot diagnostics, if enabled
    if enable_plotting:
        plot_path = os.path.join(out_dir, test_name, 'reconstructed.png')
        ensure_dir_for_file(plot_path)
        fig = plot_reconstruct(pcm_input, pdm_input, out, sr=sr,
            aspect=6.0, pcm_marker='o')
        fig.savefig(plot_path)
        print('Wrote', plot_path)

        plot_path = os.path.join(out_dir, test_name, 'shifted.png')
        ensure_dir_for_file(plot_path)
        fig = plot_reconstruct(input_trimmed, pdm_input, error, sr=sr,
            aspect=6.0, pcm_marker='o')
        fig.savefig(plot_path)
        print('Wrote', plot_path)

    # Do checks
    n_stages = 3
    expect_delay = n_stages + 1 # XXX: might not be fully correct
    assert delay == expect_delay
    delay = expect_delay

    # Check that waveform is quite similar
    # NOTE: at high frequencies there is an expected reduction in gain/amplitude
    # if one would compensate for that, could probably tighten these limits
    mse = numpy.mean(error**2)
    mae = numpy.mean(numpy.abs(error))
    assert mse < 0.10
    assert mae < 0.06

    # Check there is no DC
    average = numpy.mean(out)
    assert abs(average) < 0.06


def test_dc():
    function = sys._getframe().f_code.co_name # looks up function name
    test_name = f'{function}' 
    sr = SAMPLERATE_DEFAULT
    test_duration = 0.030

    # Generate test data
    frequency = 1000
    pcm_input = generate_test_tone(duration_sec=test_duration,
        freqs=[frequency], noise_level=0.0, sample_rate=sr, amplitude=0.1,
    ) + 0.20 # DC
    pdm_input = convert(pcm_input)
    out = numpy.zeros(shape=len(pdm_input)//DECIMATION, dtype=numpy.int16)

    # Process using filter
    n_samples = galearn_pdm.process(pdm_input, out, 255, 0)
    out = out / (2**12)

    # Compensate for delay through filter
    delay = find_forward_shift(pcm_input, out)
    out_shifted = out[delay:-1]
    input_trimmed = pcm_input[:len(out_shifted)]
    #out_shifted = out_shifted[5:-5]
    #input_trimmed = input_trimmed[5:-5]
    error = out_shifted - input_trimmed

    # Plot diagnostics, if enabled
    if enable_plotting:
        plot_path = os.path.join(out_dir, test_name, 'reconstructed.png')
        ensure_dir_for_file(plot_path)
        fig = plot_reconstruct(pcm_input, pdm_input, out, sr=sr,
            aspect=6.0, pcm_marker='o')
        fig.savefig(plot_path)
        print('Wrote', plot_path)

        plot_path = os.path.join(out_dir, test_name, 'shifted.png')
        ensure_dir_for_file(plot_path)
        fig = plot_reconstruct(input_trimmed, pdm_input, error, sr=sr,
            aspect=6.0, pcm_marker='o')
        fig.savefig(plot_path)
        print('Wrote', plot_path)

    # Do checks
    n_stages = 3
    expect_delay = n_stages + 1 # XXX: might not be fully correct
    assert delay == expect_delay
    delay = expect_delay

    # Check that waveform is quite similar
    # NOTE: at high frequencies there is an expected reduction in gain/amplitude
    # if one would compensate for that, could probably tighten these limits
    mse = numpy.mean(error**2)
    mae = numpy.mean(numpy.abs(error))
    assert mse < 0.10
    assert mae < 0.06

    # Check there is no DC
    average = numpy.mean(out)
    assert abs(average) < 0.06


def test_whitenoise():
    function = sys._getframe().f_code.co_name # looks up function name
    test_name = f'{function}' 
    sr = SAMPLERATE_DEFAULT
    test_duration = 2.0

    def filter(pcm_input):
        pdm_input = convert(pcm_input)
        out = numpy.zeros(shape=len(pdm_input)//DECIMATION, dtype=numpy.int16)
        n_samples = galearn_pdm.process(pdm_input, out, 0, 0)
        out = out / (2**12)
        return out

    results = measure_snr_white_noise(
        filter_func=filter,
        fs=sr,
        duration=test_duration,
        freq_bands=[(20, 200), (200, 2000), (2000, 8000), (8000, 16000)]
    )

    # Plot diagnostics, if enabled
    if enable_plotting:
        # FIXME:
        plot_path = os.path.join(out_dir, test_name, 'shifted.png')
        ensure_dir_for_file(plot_path)
        fig = plot_snr_results(results)
        fig.savefig(plot_path)
        print('Wrote', plot_path)

    # FIXME: add checks

def test_frequency_response():
    function = sys._getframe().f_code.co_name # looks up function name
    test_name = f'{function}' 
    sr = SAMPLERATE_DEFAULT
    test_duration = 2.0

    def filter(pcm_input):
        pdm_input = convert(pcm_input)
        out = numpy.zeros(shape=len(pdm_input)//DECIMATION, dtype=numpy.int16)
        n_samples = galearn_pdm.process(pdm_input, out, 0, 0)
        out = out / (2**12)
        return out

    results = measure_frequency_response(filter, 10.0, 8000.0, steps=50, fs=sr)

    # Plot diagnostics, if enabled
    if enable_plotting:
        # FIXME:
        plot_path = os.path.join(out_dir, test_name, 'shifted.png')
        ensure_dir_for_file(plot_path)
        fig = plot_filter_response(results)
        fig.savefig(plot_path)
        print('Wrote', plot_path)

    # FIXME: add checks


