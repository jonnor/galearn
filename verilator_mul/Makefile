all: obj_dir/Vmul

check: all
	obj_dir/Vmul

clean:
	rm -fr obj_dir

.PHONY: all check clean

obj_dir/Vmul: mul.v sim_main.cc
	verilator --cc --exe --build -j 0 -Wall sim_main.cc mul.v
