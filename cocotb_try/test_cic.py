
# https://docs.cocotb.org/en/stable/quickstart.html
# test_my_design.py (extended)

import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer, with_timeout
from cocotb.clock import Clock
from cocotb.binary import BinaryValue

import numpy

from pcm2pdm import convert
from testsignal import generate_test_tone
from test_pdm import plot_reconstruct

sr = 16000
decimation = 64


async def drive_waveform(dut, waveform):
    for a_val in waveform:
        dut.pdm_in.value = bool(a_val)
        await RisingEdge(dut.clk)


async def collect_output(dut, samples):

    out = numpy.zeros(samples, dtype=numpy.int16)

    # wait for the PCM output
    for i in range(samples):
        await with_timeout(RisingEdge(dut.pcm_valid), 100000, 'ns')
        #dut._log.info("PCM is %s", dut.pcm_out.value)
        s = dut.pcm_out.value.signed_integer
        out[i] = s

    return out


async def process_pdm(dut, pdm_data, decimation):

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    cocotb.start_soon(drive_waveform(dut, pdm_data))

    pcm_samples = len(pdm_data)//decimation
    out = await collect_output(dut, pcm_samples)

    return out

@cocotb.test()
async def test_decode_sine_1000hz(dut):
    """Try running with PDM input"""

    sig = generate_test_tone(duration_sec=0.004,
        freqs=[1000.0], noise_level=0.0, sample_rate=sr, amplitude=0.9,
    )

    pdm_data = convert(sig)
    output = await process_pdm(dut, pdm_data, decimation)
    output = output / 1024

    fig = plot_reconstruct(sig, pdm_data, output, sr=sr, aspect=6.0)
    fig.savefig('pdm_cocotb_1khz.png')

@cocotb.test()
async def test_decode_sine_200hz(dut):
    """Try running with PDM input"""

    sig = generate_test_tone(duration_sec=0.008,
        freqs=[200.0], noise_level=0.0, sample_rate=sr, amplitude=0.9,
    )

    pdm_data = convert(sig)
    output = await process_pdm(dut, pdm_data, decimation)
    output = output / 1024

    fig = plot_reconstruct(sig, pdm_data, output, sr=sr, aspect=6.0)
    fig.savefig('pdm_cocotb_200hz.png')

