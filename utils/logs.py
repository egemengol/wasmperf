from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple

import numpy as np


class Run(NamedTuple):
    alg_name: str
    arch: str
    params: Tuple[Tuple[str, str]]
    path: Path
    runtime: Optional[str]
    durs: np.array

    @classmethod
    def from_path(cls, path: Path):
        tokens = path.name.split("!")
        alg_name = tokens[0]
        arch = tokens[1]
        runtime = "native"
        if arch == "wasm_single" or arch == "wasm_multi":
            runtime = tokens.pop()
        params = dict()
        for pair in tokens[2:]:
            items = pair.split("+", maxsplit=1)
            params[items[0]] = items[1]

        durs: List[float] = list()
        with open(path) as f:
            for l in f:
                durs.append(float(l.strip()))

        durs = np.array(durs)

        return cls(alg_name, arch, tuple(params.items()), path, runtime, durs)


def get_runs(alg_name: str = None):
    runs: List[Run] = list()

    log_path = Path("logs")
    for p in log_path.iterdir():
        if p.name == "err":
            continue
        r = Run.from_path(p)
        if alg_name is None or alg_name == r.alg_name:
            runs.append(r)
    return runs
