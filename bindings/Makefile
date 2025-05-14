
SHARED_LIB=obj_dir/libsim.so

# FIXME: 
PY_MODULE=galearn_pdm.cpython-313-x86_64-linux-gnu.so

all: ${PY_MODULE}

clean:
	rm -fr obj_dir

.PHONY: all check clean

${SHARED_LIB}: ../verilator_lib/mul.v ../verilator_lib/sim.cc
	verilator --cc --lib-create sim --build -j 0 -Wall $^

check: ${PY_MODULE}
	python test_galearn_pdm.py

${PY_MODULE}: ${SHARED_LIB}
	python setup.py build_ext --inplace

    
