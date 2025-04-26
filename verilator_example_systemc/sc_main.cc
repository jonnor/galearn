#include <cstdio>

#include "Vhello.h"

using namespace sc_core;

int
sc_main(int argc, char **argv)
{
	Verilated::commandArgs(argc, argv);
	sc_clock clk{"clk", 10, SC_NS, 0.5, 3, SC_NS, true};

	Vhello *top = new Vhello{"top"};
	top->clk(clk);
	while (!Verilated::gotFinish())
		sc_start(1, SC_NS);
	fprintf(stderr, "it finished.\n");
	return 0;
}
