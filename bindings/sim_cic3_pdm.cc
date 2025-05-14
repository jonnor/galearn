
#include <cstdint>
#include <cstdio>

#include "Vcic3_pdm.h"
#include "verilated.h"

int
pdm2pcm_cic3(const uint8_t *pdm, int pdm_length, int16_t *pcm, int pcm_length)
{

	// FIXME: verify that output buffer is large enough

	VerilatedContext *cp = new VerilatedContext;

	Vcic3_pdm *top = new Vcic3_pdm{cp};

	// Start clock off
	top->clk = 0;

	// Go through all the input data
	int pcm_sample = 0;

	for (int i = 0; i < pdm_length; i++) {

		top->pdm_in = bool(pdm[i]);
		top->clk = 1;
		top->eval();

		if (top->pcm_valid) {
			pcm[pcm_sample++] = top->pcm_out;
		}

		top->clk = 0;
		top->eval();
	}

	return pcm_sample;
}
