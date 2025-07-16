TOP = top
VS = top.v ../cocotb_try/cic3_pdm.v

all: check top.bin

check:
	verilator --lint-only --top $(TOP) $(VS)

clean:
	rm -f top.asc top.bin top.json

gui:
	nextpnr-ice40 --hx1k --package tq144 --json top.json --pcf top.pcf --asc top.asc --top $(TOP) --gui

load: all
	iceprog top.bin

.PHONY: all check clean gui load

top.asc: top.json top.pcf
	nextpnr-ice40 --hx1k --package tq144 --json top.json --pcf top.pcf --asc top.asc --top $(TOP)

top.bin: top.asc
	icepack top.asc top.bin

top.json: $(VS)
	yosys -q -p "synth_ice40 -json top.json -top $(TOP)" $(VS)
