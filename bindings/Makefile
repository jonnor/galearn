
SHARED_LIB=obj_dir/libsim.so

# FIXME: handle different Python versions
PY_MODULE=galearn_pdm.cpython-313-x86_64-linux-gnu.so

all: ${PY_MODULE}

clean:
	rm -fr obj_dir

.PHONY: all check clean

${SHARED_LIB}: ../cocotb_try/cic3_pdm.v ./sim_cic3_pdm.cc
	verilator --cc --lib-create sim --build -j 0 -Wall $^

check: ${PY_MODULE}
	PYTHONPATH=../tools python test_galearn_pdm.py

${PY_MODULE}: ${SHARED_LIB}
	python setup.py build_ext --inplace

