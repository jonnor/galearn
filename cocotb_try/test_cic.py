
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


async def drive_waveform(dut, waveform):

    high_delay = Timer(1, units="ns")
    low_delay = Timer(1, units="ns")

    for a_val in waveform:
        dut.pdm_in.value = bool(a_val)

        #dut.clk.value = 0
        #await low_delay
        #dut.clk.value = 1
        #await high_delay

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


@cocotb.test()
async def my_second_test(dut):
    """Try running with PDM input"""

    sr = 16000
    decimation = 64

    sig = generate_test_tone(duration_sec=0.004,
        freqs=[1000.0], noise_level=0.0, sample_rate=sr, amplitude=0.9,
    )

    pdm_data = convert(sig)

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    cocotb.start_soon(drive_waveform(dut, pdm_data))

    pcm_samples = len(pdm_data)//decimation
    output = await collect_output(dut, pcm_samples)

    output = output / 1024

    fig = plot_reconstruct(sig, pdm_data, output, sr=sr, aspect=6.0)
    fig.savefig('pdm_cocotb.png')

