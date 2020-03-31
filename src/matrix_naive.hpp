
#include <vector>
#include <cstdint>
#include <assert.h>
#include <iostream>
#include <iomanip>
#include <random>
#include <algorithm>
#include <chrono>
#include <thread>



using namespace std;

typedef int32_t num;

std::mt19937 rng;

struct M {
    vector<vector<num>> data;
    size_t first;
    size_t second;
};

M init(vector<vector<num>> &data) {
    M m;
    m.first = data.size();
    assert(m.first != 0);
    m.second = data.front().size();
    for (size_t r=1; r<m.first; r++)
        assert(data[r].size() == m.second);

    m.data = data;
    return m;
}

void multiply_simple_single(const M &l, const M &r, M &res) {
    for (size_t i=0; i<l.first; i++)
        for (size_t j=0; j<r.second; j++)
            for (size_t k=0; k<l.second; k++)
                res.data[i][j] += l.data[i][k] * r.data[k][j];
}


M multiply_simple_single_wrapper(const M &l, const M &r) {
    assert(l.second == r.first);
    M m = {
            vector<vector<num>>(l.first, vector<num>(r.second, 0)),
            l.first,
            r.second,
    };
    multiply_simple_single(l, r, m);
    return m;
}

void multiply_simple_multi_threadf(const M &l, const M &r, M &res, size_t low, size_t high) {
    for (size_t ix=low; ix<high; ix++) {
        size_t i = ix / r.second;
        size_t j = ix - r.second * i;
        for (size_t k=0; k<l.second; k++)
            res.data[i][j] += l.data[i][k] * r.data[k][j];
    }
}

void multiply_simple_multi(const M &l, const M &r, M &res, size_t nof_threads) {
    const size_t total = l.first * r.second;
    const size_t incr = total / nof_threads;
    size_t begin = 0;

    vector<thread> threads;
    threads.reserve(nof_threads);
    for (size_t i=0; i<nof_threads-1; i++) {
        threads.push_back(std::thread(multiply_simple_multi_threadf,
                                      ref(l), ref(r), ref(res),
                                      begin, begin+incr));
        begin += incr;
    }
    threads.push_back(std::thread(multiply_simple_multi_threadf,
                                  ref(l), ref(r), ref(res),
                                  begin, total));

    for (auto &t : threads)
        if (t.joinable())
            t.join();
}


M multiply_simple_multi_wrapper(const M &l, const M &r, std::size_t nof_threads) {
    assert(l.second == r.first);
    M m = {
            vector<vector<num>>(l.first, vector<num>(r.second, 0)),
            l.first,
            r.second,
    };

    multiply_simple_multi(l, r, m, nof_threads);

    return m;
}

void print(M &m) {
    cout << m.first << "x" << m.second << endl;
    for (auto &l : m.data) {
        for (auto val : l)
            cout << val << ',';
        cout << endl;
    }
}

struct RandGen {
    std::uniform_int_distribution<num> dist;
    RandGen(num low, num high) : dist(low, high) {}
    num operator()() {
        return dist(rng);
    }
};


M createMatrix(size_t first, size_t second) {
    RandGen randgen(-99, 99);

    vector<vector<num>> data(first, vector<num>(second));
    for (auto &v : data)
        std::generate(v.begin(), v.end(), randgen);

    M m = {
        data,
        first,
        second,
    };
    return m;
}

chrono::milliseconds bench_simple_single(size_t left, size_t mid, size_t right) {
    M l = createMatrix(left, mid);
    M r = createMatrix(mid, right);
    assert(l.second == r.first);
    M m = {
            vector<vector<num>>(l.first, vector<num>(r.second, 0)),
            l.first,
            r.second,
    };

    auto start = chrono::steady_clock::now();
    multiply_simple_single(l, r, m);
    auto end = chrono::steady_clock::now();

    return chrono::duration_cast<chrono::milliseconds>(end - start);
}


chrono::milliseconds bench_simple_multi(size_t left, size_t mid, size_t right, size_t nof_threads) {
    M l = createMatrix(left, mid);
    M r = createMatrix(mid, right);
    assert(l.second == r.first);
    M m = {
            vector<vector<num>>(l.first, vector<num>(r.second, 0)),
            l.first,
            r.second,
    };

    auto start = chrono::steady_clock::now();
    multiply_simple_multi(l, r, m, nof_threads);
    auto end = chrono::steady_clock::now();

    return chrono::duration_cast<chrono::milliseconds>(end - start);
}