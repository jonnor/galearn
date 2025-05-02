#include <cstdint>
#include <cstdio>

#include "Vmul.h"
#include "verilated.h"

enum { MAX = 10000 };

int
main(int argc, char **argv)
{
	VerilatedContext *cp = new VerilatedContext;
	cp->commandArgs(argc, argv);

	Vmul *top = new Vmul{cp};
	top->clk = 0;

	int numclks = 0;
	for (int x = 0; x < MAX; ++x) {
		for (int y = 0; y < MAX; ++y) {
			top->x = x;
			top->y = y;
			top->clk = 1;
			top->eval();

			int p = top->p;
			if (p != (uint32_t)(x * y))
				printf("%4d * %4d = %4d\n", x, y, p);

			top->clk = 0;
			top->eval();
			++numclks;
		}
	}
	fprintf(stderr, "%d clock cycles\n", numclks);
}
