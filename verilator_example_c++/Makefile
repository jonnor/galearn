all: obj_dir/Vhello

check: all
	obj_dir/Vhello

clean:
	rm -fr obj_dir

.PHONY: all check clean

obj_dir/Vhello: hello.v sim_main.cc
	verilator --cc --exe --build -j 0 -Wall sim_main.cc hello.v
