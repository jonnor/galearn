
#include <cstdint>
#include <cstdio>
#include <stdexcept>

#include "Vcic3_pdm.h"
#include "verilated.h"

int
pdm2pcm_cic3(const uint8_t *pdm, int64_t pdm_length, int16_t *pcm, int32_t pcm_length, uint8_t hpf_alpha, uint8_t scale_shift)
{
    const int DECIMATION = 64;
    
    const int expect_length = pdm_length / DECIMATION; 
    if (pcm_length < expect_length) {
        throw std::runtime_error("PCM buffer too small");
    }

	// FIXME: verify that output buffer is large enough

	VerilatedContext *cp = new VerilatedContext;

	Vcic3_pdm *top = new Vcic3_pdm{cp};

    top->dc_alpha = hpf_alpha;
    top->scale_shift = scale_shift;

    // Reset on start
    top->rst = 0;
    top->eval();
    top->rst = 1;
    top->eval();
    top->rst = 0;
    top->eval();

	// Start clock off
	top->clk = 0;

	// Go through all the input data
	int pcm_sample = 0;
    bool last_valid = top->pcm_valid;

	for (int i = 0; i < pdm_length; i++) {

		top->pdm_in = bool(pdm[i]);
		top->clk = 1;
		top->eval();

        if (pcm_sample >= pcm_length) {
            throw std::runtime_error("PCM buffer overrun: pcm_sample=" + std::to_string(pcm_sample) + " pdm_sample="+std::to_string(i));
        }
        const bool valid = top->pcm_valid;
        // && (!last_valid);
		if (valid) {
			pcm[pcm_sample++] = top->pcm_out;
		}
        last_valid = top->pcm_valid;

		top->clk = 0;
		top->eval();
	}

    if (pcm_sample != expect_length) {
        throw std::runtime_error("Wrong length. expected="+std::to_string(expect_length) + std::string(" got=")+std::to_string(pcm_sample));
    }

	return pcm_sample;
}
