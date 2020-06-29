#include <iostream>
#include <thread>
#include <assert.h>
#include <chrono>

using namespace std;

void mycpy(int * destination, int * source, size_t num) {
    for(int i=0; i<num; i++)
        destination[i] = source[i];
}

chrono::microseconds measure_block_mycpy(size_t size, size_t nof_threads) {
    int *a, *b;
    a = new int[size];
    b = new int[size];

    for (size_t i=0; i<size; i++)
        a[i] = i;

    std::thread t[nof_threads];
    auto start = chrono::steady_clock::now();
    for(int i=0; i<nof_threads; i++) {
        size_t num = size / nof_threads;
        //void *d = &(b[i * num]);
        //void *s = &(a[i * num]);
        if (i==nof_threads-1) {
            num += size % nof_threads;
        }
        t[i] = std::thread(mycpy, &b[i*num], &a[i*num], num);
    }
    for(auto &th : t)
        if (th.joinable())
            th.join();
    auto end = chrono::steady_clock::now();
    for(int i=0; i<size; i++)
        assert(b[i] == a[i]);
    delete[] a;
    delete[] b;
    return chrono::duration_cast<chrono::microseconds>(end-start);
}