from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
import logging
import subprocess


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s -- %(levelname)s -- %(message)s",
    datefmt="%H.%M.%S",
)


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
    @abstractmethod
    def log_path(self) -> Path:
        pass


@dataclass
class ExpDataMixin:
    alg_name: str
    params: Dict[str, Any]
    repetitions: int
    browsers: List[str]


class Experiment(ExpDataMixin, ExpAbstract):
    """Experiment class for typing check"""

    @property
    def source(self) -> Path:
        return algname2path(self.alg_name)


class ExperimentNative(Experiment):
    def run(self) -> None:
        with open(self.log_path, "a") as f:
            for _ in range(self.repetitions):
                res = subprocess.run(
                    [self.dir_path / "main"],
                    stdout=subprocess.PIPE,
                    check=True)
                f.write(res.stdout.decode())
        logging.info(f"Finished measuring {self} -- {self.repetitions} times.")

    def __str__(self) -> str:
        params = " ".join([
            f"{k.lower()}={v}" for (k, v) in self.params.items()])
        return f"{self.alg_name} native {params}"

    @property
    def dir_path(self) -> Path:
        params = "X".join([f"{k.lower()}+{v}" for k, v in self.params.items()])
        return Path("out") / f"{self.alg_name}XnativeX{params}"

    @property
    def log_path(self) -> Path:
        return Path("logs") / self.dir_path.name

    @property
    def target_path(self) -> Path:
        return (self.dir_path / "main").resolve()

    @property
    def make_command(self) -> str:
        depends_on = self.source

        comm_strings = [
            "clang++ -O3 -pthread -std=c++17 -DNDEBUG",
            f"-o {self.dir_path.resolve()}/main",
        ]
        for k, v in self.params.items():
            comm_strings.append(f"-D {k}={v}")
        comm_strings.append(str(depends_on.resolve()))

        return (
            f"{self.target_path}: {depends_on}\n"
            f"\trm -f {(Path('logs') / self.dir_path.name).resolve()}\n"
            f"\t{' '.join(comm_strings)}"
        )


class ExperimentWasm(Experiment):
    def run(self):
        for browser in self.browsers:
            for _ in range(self.repetitions):
                log_path = str(self.log_path.resolve())+"X"+Path(browser).name
                p = subprocess.run([
                        "emrun",
                        "--browser",
                        browser,
                        "--serve_after_close",
                        "--serve_root",
                        self.dir_path.resolve(),
                        "--log_stdout",
                        log_path,
                        "--log_stderr",
                        Path("logs/err").resolve(),
                        "--verbose",
                        "index.html",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                # print(" ".join((str(a) for a in p.args)))
            logging.info((
                f"Finished measuring {self} {browser} -- "
                f"{self.repetitions} times."))


class ExperimentWasmSingle(ExperimentWasm):
    def __str__(self):
        params = " ".join([f"{k.lower()}={v}" for k, v in self.params.items()])
        return f"{self.alg_name} wasm_single {params}"

    @property
    def dir_path(self) -> Path:
        params = "X".join([f"{k.lower()}+{v}" for k, v in self.params.items()])
        return Path("out") / (
            f"{self.alg_name}Xwasm_singleX"
            f"{params}")

    @property
    def log_path(self) -> Path:
        return Path("logs") / self.dir_path.name

    @property
    def target_path(self) -> Path:
        return (self.dir_path / "t.js").resolve()

    @property
    def make_command(self) -> str:
        depends_on = self.source

        comm_strings = [
            "emcc -std=c++17 -Os -DNDEBUG --llvm-lto 1",
            "-s TOTAL_MEMORY=1073741824 --emrun",
            f"-o {self.dir_path.resolve()}/t.js",
            "-s NO_FILESYSTEM=1",
        ]
        for k, v in self.params.items():
            comm_strings.append(f"-D {k}={v}")
        comm_strings.append(str(depends_on.resolve()))

        return (
            f"{self.target_path}: {depends_on}\n"
            f"\trm -f {(Path('logs') / self.dir_path.name).resolve()}\n"
            f"\t{' '.join(comm_strings)}"
        )


class ExperimentWasmMulti(ExperimentWasm):
    def __str__(self):
        params = " ".join([f"{k.lower()}={v}" for k, v in self.params.items()])
        return f"{self.alg_name} wasm_multi {params}"

    @property
    def dir_path(self) -> Path:
        params = "X".join([f"{k.lower()}+{v}" for k, v in self.params.items()])
        return Path("out") / (
            f"{self.alg_name}Xwasm_multiX"
            f"{params}")

    @property
    def log_path(self) -> Path:
        return Path("logs") / self.dir_path.name

    @property
    def target_path(self) -> Path:
        return (self.dir_path / "t.js").resolve()

    @property
    def make_command(self) -> str:
        depends_on = self.source

        comm_strings = [
            "emcc -std=c++17 -Os -DNDEBUG --llvm-lto 1",
            "-s TOTAL_MEMORY=1073741824 --emrun",
            f"-o {self.dir_path.resolve()}/t.js",
            "-s USE_PTHREADS=1",
            "-s PTHREAD_POOL_SIZE=7",
            "-s PROXY_TO_PTHREAD=1",
            "--memory-init-file 0",
        ]
        for k, v in self.params.items():
            comm_strings.append(f"-D {k}={v}")
        comm_strings.append(str(depends_on.resolve()))

        return (
            f"{self.target_path}: {depends_on}\n"
            f"\trm -f {(Path('logs') / self.dir_path.name).resolve()}\n"
            f"\t{' '.join(comm_strings)}"
        )
