all: obj_dir/Vhello

check: all
	obj_dir/Vhello

clean:
	rm -fr obj_dir

.PHONY: all check clean

obj_dir/Vhello: hello.v
	verilator --binary -j 0 -Wall hello.v
