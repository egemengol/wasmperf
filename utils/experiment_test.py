import unittest
from pathlib import Path
from experiment import algname2path, ExperimentNative, ExperimentWasmSingle


class Test(unittest.TestCase):

    def test_algname2path(self):
        self.assertEqual(
            Path("/home/egeme/code/tez_c/src/merge.cpp"),
            algname2path("merge")
        )

    def test_makecomm_native(self):
        e = ExperimentNative(
            alg_name="merge",
            params={"SIZE": 100, "N_LEVELS": 2},
            repetitions=2,
        )
        expected = (
            "merge_native: /home/egeme/code/tez_c/src/merge.cpp\n"
            "\tclang++ -O3 -pthread -std=c++17 -DNDEBUG "
            "-o out/'merge native size=100 n_levels=2'/main "
            "-D SIZE=100 -D N_LEVELS=2 /home/egeme/code/tez_c/src/merge.cpp"
        )
        self.assertEqual(e.make_command, expected)

    def test_makecomm_wasm_single(self):
        e = ExperimentWasmSingle(
            alg_name="merge",
            params={"SIZE": 100, "N_LEVELS": 2},
            repetitions=0,
        )
        expected = (
            "merge_wasm_single: /home/egeme/code/tez_c/src/merge.cpp\n"
            "\temcc -std=c++17 -Os -DNDEBUG --llvm-lto 1 "
            "-s TOTAL_MEMORY=1073741824 --emrun "
            "-o out/'merge wasm_single size=100 n_levels=2'/t.js "
            "-s NO_FILESYSTEM=1 -D SIZE=100 -D N_LEVELS=2 "
            "/home/egeme/code/tez_c/src/merge.cpp"
        )
        self.assertEqual(e.make_command, expected)


if __name__ == '__main__':
    unittest.main()
