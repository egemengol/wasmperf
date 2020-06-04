#include <atomic>
#include <iostream>
#include <thread>
#include <assert.h>

using namespace std;

atomic<uint32_t> counter (0);

void increment(size_t num) {
    for (int i=0; i<num; i++)
        counter++;
}

chrono::microseconds measure_atomics(size_t total_count, size_t num_threads){
    thread threads[num_threads];
    auto start = chrono::steady_clock::now();
    for(int i=0; i<num_threads; i++) {
        threads[i] = thread(increment, total_count/num_threads);
    }
    for(auto &th : threads)
        if (th.joinable())
            th.join();
    auto end = chrono::steady_clock::now();

    assert(counter.load(memory_order_seq_cst));
    return chrono::duration_cast<chrono::microseconds>(end-start);
}

int main() {
    for(int i=0; i<MEASURE_PER_RUN; i++) {
        auto duration = measure_atomics(TOTAL_COUNT, NUM_THREADS);
        cout << duration.count() << endl;
    }
    return 0;
}
