
# https://docs.cocotb.org/en/stable/quickstart.html
# test_my_design.py (extended)

import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer, with_timeout
from cocotb.clock import Clock


async def generate_clock(dut):
    """Generate clock pulses."""

    for cycle in range(10):
        dut.clk.value = 0
        await Timer(1, units="ns")
        dut.clk.value = 1
        await Timer(1, units="ns")

async def drive_waveform(dut, waveform):
    for a_val in waveform:
        dut.pdm_in.value = a_val
        await RisingEdge(dut.clk)


@cocotb.test()
async def my_second_test(dut):
    """Try running with PDM input"""

    #dut.rst.value = 1
    #await RisingEdge(dut.clk)
    #dut.rst.value = 0

    pcm_samples = 10
    decimation = 64
    pdm_data = [0, 0, 1] * (pcm_samples*decimation)

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    cocotb.start_soon(drive_waveform(dut, pdm_data))

    # wait for the PCM output
    for _ in range(pcm_samples):
        await with_timeout(RisingEdge(dut.pcm_valid), 100000, 'ns')
        dut._log.info("PCM is %s", dut.pcm_out.value)

    #dut._log.info("pdm_out is %s", dut.pdm_out.value)
    #assert dut.pdm_out.value == 1

    dut._log.info("my_signal_1 is %s", dut.pcm_out.value)
    assert dut.pcm_out.value == 1212

