base_native := clang++ -O3 -pthread -std=c++17 -DNDEBUG -o out/main
base_wasm := emcc -std=c++17 -Os -DNDEBUG --llvm-lto 1 -s TOTAL_MEMORY=1073741824 --emrun -o out/t.js

demo_native: src/demo.cpp
	$(base_native) -D SIZE=$(SIZE) -D NOF_THREADS=$(NOF_THREADS) src/demo.cpp

merge_native: src/merge.cpp
	$(base_native) -D SIZE=$(SIZE) -D N_LEVELS=$(N_LEVELS) src/merge.cpp

merge_wasm_single: src/merge.cpp
	$(base_wasm) -s NO_FILESYSTEM=1 -D SIZE=$(SIZE) -D N_LEVELS=$(N_LEVELS) src/merge.cpp

merge_wasm_multi: src/merge.cpp
	$(base_wasm) -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=7 -s PROXY_TO_PTHREAD=1 --memory-init-file 0 -D SIZE=$(SIZE) -D N_LEVELS=$(N_LEVELS) src/merge.cpp

clear:
	rm -rf out/*