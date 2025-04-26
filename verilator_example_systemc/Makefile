all: obj_dir/Vhello

check: all
	obj_dir/Vhello

clean:
	rm -fr obj_dir

.PHONY: all check clean

obj_dir/Vhello: hello.v sc_main.cc
	verilator --sc --exe --build -j 0 -Wall sc_main.cc hello.v
