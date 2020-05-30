from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple

import numpy as np
import pandas as pd


class Run(NamedTuple):
    alg_name: str
    arch: str
    params: Tuple[Tuple[str, str]]
    path: Path
    runtime: Optional[str]
    durs: np.array
    mean: float

    @classmethod
    def from_path(cls, path: Path):
        tokens = path.name.split("!")
        alg_name = tokens[0]
        arch = tokens[1]
        runtime = None
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

        return cls(
            alg_name, arch, tuple(params.items()), path, runtime, durs, durs.mean(),
        )


def analyze():
    runs: List[Run] = list()

    log_path = Path("logs")
    for p in log_path.iterdir():
        if p.name == "err":
            continue
        r = Run.from_path(p)
        runs.append(r)

    df = pd.DataFrame(runs)
    gr = df.groupby(["alg_name", "params"])
    for k, v in gr.groups.items():
        group_df = df.iloc[v].drop(["alg_name", "params", "path"], axis=1)
        alg_name = k[0]
        params = dict(k[1])
        print(alg_name, params)
        print(group_df)
        print()


if __name__ == "__main__":
    analyze()
