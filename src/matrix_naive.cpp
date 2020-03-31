#include "matrix_naive.hpp"

/*
Compile time variables:
    A, B, C         matrix sizes
    IS_MULTI        indicates if multithreaded
    NUM_THREADS     ..
    SEED            random seed
*/

int main() {

#if defined(SEED)
    rng.seed(SEED);
#endif

#if defined(NUM_THREADS)
    cout << bench_simple_multi(A, B, C, NUM_THREADS).count() << endl;
#else
    cout << bench_simple_single(A, B, C).count() << endl;
#endif
    return 0;
}

/*

int main() {
    rng.seed(13);
/*
    M l = createMatrix(14,6);
    M r = createMatrix(6,9);

    M res = multiply_simple_multi_wrapper(l, r);
    print(res);
    

    cout << "\nSingle threaded" << endl;
    for (int i=0; i<4; i++)
        cout << bench_simple_single(999, 1588, 777).count() << "ms" << endl;
    
    cout << "\nMulti threaded 1" << endl;
    for (int i=0; i<4; i++)
        cout << bench_simple_multi(999, 1588, 777, 1).count() << "ms" << endl;
    
    cout << "\nMulti threaded 2" << endl;
    for (int i=0; i<4; i++)
        cout << bench_simple_multi(999, 1588, 777, 2).count() << "ms" << endl;
    
    cout << "\nMulti threaded 4" << endl;
    for (int i=0; i<4; i++)
        cout << bench_simple_multi(999, 1588, 777, 4).count() << "ms" << endl;
    
    cout << "\nMulti threaded 8" << endl;
    for (int i=0; i<4; i++)
        cout << bench_simple_multi(999, 1588, 777, 8).count() << "ms" << endl;
    return 0;
}
*/