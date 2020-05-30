#include "memcpy.hpp"

using namespace std;

/*
Compile time variables:
SIZE of array
NUM_THREADS
MEASURE_PER_RUN take multiple measurements per run
*/

int main() {
    for(int i=0; i<MEASURE_PER_RUN; i++) {
        auto duration = measure_block_mycpy(SIZE, NUM_THREADS);
        cout << duration.count() << endl;
    }

    return 0;
}
