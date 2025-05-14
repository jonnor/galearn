
import numpy

from pcm2pdm import convert
from testsignal import generate_test_tone
from test_pdm import plot_reconstruct
import galearn_pdm

sr = 16000
decimation = 64

def test_one():
    
    sig = generate_test_tone(duration_sec=0.004,
        freqs=[1000.0], noise_level=0.0, sample_rate=sr, amplitude=0.9,
    )

    pdm_data = convert(sig)

    inp = pdm_data # numpy.ones(shape=10, dtype=numpy.uint8)
    print(inp.shape, inp.dtype)
    print(inp)

    out = numpy.zeros(shape=len(inp)//decimation, dtype=numpy.int16)

    n_samples = galearn_pdm.process(inp, out)
    out = out / 1024

    print(numpy.mean(out))
    print(out)


    fig = plot_reconstruct(sig, pdm_data, out, sr=sr, aspect=6.0)
    plot_path = 'pdm_verilated_1khz.png'
    fig.savefig(plot_path)

    #assert out[0] == 2
    #assert out[-1] == 2


if __name__ == '__main__':
    test_one()
