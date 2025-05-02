#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

int sim(void);

namespace py = pybind11;

void process(py::array_t<uint8_t> arr1, py::array_t<int16_t> arr2) {
    // Check shapes or sizes if needed
    auto buf1 = arr1.request();
    auto buf2 = arr2.request();

    if (buf1.ndim != 1 || buf2.ndim != 1) {
        throw std::runtime_error("Only 1D arrays supported");
    }

    if (buf1.size < buf2.size) {
        throw std::runtime_error("Input 1 must be same or larger than input 2");
    }

#if 0
    // Example: access data
    uint8_t* in = static_cast<uint8_t*>(buf1.ptr);
    int16_t* out = static_cast<int16_t*>(buf2.ptr);
    for (int i=0; i<buf2.size; i++) {
        out[i] = in[i] + 1;
    }
#else

    sim();

#endif

}

PYBIND11_MODULE(galearn_pdm, m) {
    m.def("process", &process, "Process two numpy arrays (uint8 and int16)");
}
