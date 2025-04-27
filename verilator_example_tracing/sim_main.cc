#include <cstdio>

#include "Vhello.h"
#include "verilated.h"

int
main(int argc, char **argv)
{
	VerilatedContext *cp = new VerilatedContext;
	cp->traceEverOn(true);
	cp->commandArgs(argc, argv);

	Vhello *top = new Vhello{cp};
	top->clk = 0;

	while (!cp->gotFinish()) {
		cp->timeInc(1);

		top->clk = !top->clk;
		top->eval();
	}
	top->final();
	VL_PRINTF("[%" PRId64 "]\n", cp->time());
	fprintf(stderr, "it finished.\n");
}
