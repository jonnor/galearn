
import galearn_pdm
import numpy

def test_one():
    
    inp = numpy.ones(shape=10, dtype=numpy.uint8)
    out = numpy.zeros(shape=10, dtype=numpy.int16)    

    galearn_pdm.process(inp, out)
    print(out)
    assert out[0] == 2
    assert out[-1] == 2

if __name__ == '__main__':
    test_one()
