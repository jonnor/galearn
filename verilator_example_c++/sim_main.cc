#include <cstdio>

#include "Vhello.h"
#include "verilated.h"

int
main(int argc, char **argv)
{
	VerilatedContext *cp = new VerilatedContext;
	cp->commandArgs(argc, argv);
	Vhello *top = new Vhello{cp};
	while (!cp->gotFinish())
		top->eval();
	fprintf(stderr, "it finished.\n");
}
