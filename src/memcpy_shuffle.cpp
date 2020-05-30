#include <random>
#include <chrono>
#include <algorithm>
#include <thread>
#include <assert.h>
#include <iostream>

using namespace std;

void thread_f(int* dest, const int* src, const int *shuf_beg, const size_t num) {
    for (int i=0; i<num; i++) {
        int index = shuf_beg[i];
        dest[index] = src[index];
    }
}

chrono::microseconds measure_memcpy_shuffle(size_t size, size_t nof_threads, int seed) {
    int *a = new int[size];
    int *shuf = new int[size];
    for(int i=0; i<size; i++) {
        a[i] = i;
        shuf[i] = i;
    }
    random_device rd;
    mt19937 g(rd());
    g.seed(seed);
    shuffle(shuf, &(shuf[size]), g);

    int *b = new int[size];

    thread t[nof_threads];
    auto start = chrono::steady_clock::now();
    for(int i=0; i<nof_threads; i++) {
        size_t num = size / nof_threads;
        int *shf = &(shuf[i * num]);
        if (i==nof_threads-1) {
            num += size % nof_threads;
        }
        t[i] = std::thread(thread_f, b, a, shf, num);
    }
    for(auto &th : t)
        if (th.joinable())
            th.join();
    auto end = chrono::steady_clock::now();

    for(int i=0; i<size; i++)
        assert(a[i] == b[i]);
    delete[] a;
    delete[] b;
    delete[] shuf;
    return chrono::duration_cast<chrono::microseconds>(end-start);
}

int main() {
    for(int i=0; i<MEASURE_PER_RUN; i++) {
        auto duration = measure_memcpy_shuffle(SIZE, NUM_THREADS, 13);
        cout << duration.count() << endl;
    }

    return 0;
}
