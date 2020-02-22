import yaml
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
import logging
import subprocess
from shlex import quote

"""
with open("experiments.yaml") as f:
    from pprint import pprint
    exs = yaml.load(f, Loader=yaml.SafeLoader)
    pprint(exs)
"""


def algname2path(alg_name: str) -> Path:
    return Path(f"src/{alg_name}.cpp").resolve()


class ExpAbstract(ABC):
    @property
    @abstractmethod
    def make_command(self) -> str:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    @abstractmethod
    def dir_path(self) -> Path:
        pass

    @property
    def log_path(self) -> Path:
        return Path("logs") / str(self)


@dataclass
class ExpDataMixin:
    alg_name: str
    params: Dict[str, Any]
    repetitions: int


class Experiment(ExpDataMixin, ExpAbstract):
    """Experiment class for typing check"""

    @property
    def source(self) -> Path:
        return algname2path(self.alg_name)

    @property
    def dir_path(self) -> Path:
        return Path("out") / quote(str(self))


class ExperimentNative(Experiment):
    def run(self) -> None:
        with open(self.log_path, "wb") as f:
            for _ in range(self.repetitions):
                res = subprocess.run(
                    [self.dir_path / "main"],
                    stdout=subprocess.PIPE,
                    check=True)
                f.write(res.stdout)
        logging.info(f"Finished measuring {self} {self.repetitions} times.")

    def __str__(self) -> str:
        params = " ".join([
            f"{k.lower()}={v}" for (k, v) in self.params.items()])
        return f"{self.alg_name} native {params}"

    @property
    def make_command(self) -> str:
        depends_on = self.source

        comm_strings = [
            "clang++ -O3 -pthread -std=c++17 -DNDEBUG",
            f"-o {self.dir_path}/main",
        ]
        for k, v in self.params.items():
            comm_strings.append(f"-D {k}={v}")
        comm_strings.append(str(depends_on.resolve()))

        return (
            f"{self.alg_name}_native: {depends_on}\n"
            f"\t{' '.join(comm_strings)}"
        )


class ExperimentWasm(Experiment):
    BROWSERS = [
        Path("/usr/bin/firefox"),
        Path("/usr/bin/google-chrome"),
    ]

    def run(self):
        for p in self.BROWSERS:
            for _ in range(self.repetitions):
                subprocess.run([
                        "emrun",
                        "--browser",
                        p,
                        "--serve_after_close",
                        "--serve_root",
                        self.dir_path,
                        "--log_stdout",
                        self.log_path(p),
                        "--verbose",
                        "index.html",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            logging.info(f"Finished measuring {p} {self.repetitions} times.")

    @property
    def log_path(self, with_browser) -> Path:
        return super().log_path + f" {with_browser}"


class ExperimentWasmSingle(ExperimentWasm):
    def __str__(self):
        params = " ".join([f"{k.lower()}={v}" for k, v in self.params.items()])
        return f"{self.alg_name} wasm_single {params}"

    @property
    def make_command(self) -> str:
        depends_on = self.source

        comm_strings = [
            "emcc -std=c++17 -Os -DNDEBUG --llvm-lto 1",
            "-s TOTAL_MEMORY=1073741824 --emrun",
            f"-o {self.dir_path}/t.js",
            "-s NO_FILESYSTEM=1",
        ]
        for k, v in self.params.items():
            comm_strings.append(f"-D {k}={v}")
        comm_strings.append(str(depends_on.resolve()))

        return (
            f"{self.alg_name}_wasm_single: {depends_on}\n"
            f"\t{' '.join(comm_strings)}"
        )


@dataclass
class Lab:
    exps: List[Experiment]
    browsers: List[str]

    def from_yaml(path: Path):
        with open(path) as f:
            yam = yaml.load(f, Loader=yaml.SafeLoader)

        experiments: List[Experiment] = list()

        for alg_name, comparisons in yam["algs"].items():
            comparisons: Dict[Any]
            for comp in comparisons:
                arches: List[str] = comp['arch']
                runs: List[Dict[str, Any]] = comp['runs']
                for arch in arches:
                    for run in runs:
                        if arch == "NATIVE":
                            cl = ExperimentNative
                        elif arch == "WASM_SINGLE":
                            cl = ExperimentWasmSingle
                        else:
                            continue
                        e: Experiment = cl(
                            alg_name=alg_name,
                            params=run['params'],
                            repetitions=run['reps']
                        )
                        experiments.append(e)

        return Lab(
            exps=experiments,
            browsers=yam["browsers"],
        )


    def create_makefile(self):
        #TODO
        pass


lab = Lab.from_yaml("experiments.yaml")
print(lab)
