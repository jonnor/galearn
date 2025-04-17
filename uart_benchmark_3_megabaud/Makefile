TOP = top

all: check top.bin

check:
	verilator --lint-only --top $(TOP) top.v

clean:
	rm -f top.asc top.bin top.json

load: all
	iceprog top.bin

.PHONY: all check clean load

top.asc: top.json top.pcf
	nextpnr-ice40 --hx1k --package tq144 --json top.json --pcf top.pcf --asc top.asc --top $(TOP)

top.bin: top.asc
	icepack top.asc top.bin

top.json: top.v
	yosys -q -p "synth_ice40 -json top.json -top $(TOP)" top.v
