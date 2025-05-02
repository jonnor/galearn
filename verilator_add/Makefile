all: obj_dir/Vadd

check: all
	obj_dir/Vadd

clean:
	rm -fr obj_dir

.PHONY: all check clean

obj_dir/Vadd: add.v sim_main.cc
	verilator --cc --exe --build -j 0 -Wall sim_main.cc add.v
