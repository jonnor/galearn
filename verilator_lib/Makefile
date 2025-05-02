all: wrap

check: all
	./wrap

clean:
	rm -fr obj_dir

.PHONY: all check clean

obj_dir/libsim.so: mul.v sim.cc
	verilator --cc --lib-create sim --build -j 0 -Wall mul.v sim.cc

wrap: obj_dir/libsim.so
	g++ -Iobj_dir -I/usr/share/verilator/include -I/usr/share/verilator/include/vltstd -o wrap wrap.cc obj_dir/libsim.so
