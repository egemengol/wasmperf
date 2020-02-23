import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Type
import logging
import subprocess
import shutil
import os

from experiment import (
    Experiment,
    ExperimentNative,
    ExperimentWasm,
    ExperimentWasmSingle,
    ExperimentWasmMulti,
    )


@dataclass
class Lab:
    exps: List[Experiment]

    @staticmethod
    def from_yaml(path: Path):
        with open(path) as f:
            yam = yaml.load(f, Loader=yaml.SafeLoader)

        experiments: List[Experiment] = list()

        for alg_name, comparisons in yam["algs"].items():
            for comp in comparisons:
                arches: List[str] = comp['arch']
                runs: List[Dict[str, Any]] = comp['runs']
                for arch in arches:
                    for run in runs:
                        cl: Type[Experiment]
                        browsers = list()
                        if arch == "NATIVE":
                            cl = ExperimentNative
                        elif arch.startswith("WASM_SINGLE"):
                            browsers = arch.split(" - ")[1:]
                            cl = ExperimentWasmSingle
                        elif arch.startswith("WASM_MULTI"):
                            browsers = arch.split(" - ")[1:]
                            cl = ExperimentWasmMulti
                        else:
                            logging.warning(f"Not supported arch: {arch}")
                            continue
                        e = cl(
                            alg_name=alg_name,
                            params=run['params'],
                            repetitions=run['reps'],
                            browsers=browsers,
                        )
                        experiments.append(e)
        return Lab(experiments)

    def mkdirs(self) -> None:
        dirs = [e.dir_path for e in self.exps]
        for p in dirs:
            p.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(parents=True, exist_ok=True)

    def create_makefile(self) -> None:
        with open("out/Makefile", "w") as f:
            rules = list()
            targets = list()
            for exp in self.exps:
                targets.append(exp.target_path)
                rules.append(exp.make_command)

            targets = ' '.join([str(t) for t in targets])

            f.write(f"all: {targets}\n\n")

            f.write("\n\n".join(rules))
            f.write("\n\n")

            f.flush()

    @staticmethod
    def clear_out():
        shutil.rmtree(Path("out"))

    @staticmethod
    def clear_logs():
        shutil.rmtree(Path("logs"))

    @classmethod
    def clear(cls):
        cls.clear_out()
        cls.clear_logs()

    def copy_index_html(self):
        for e in self.exps:
            if issubclass(type(e), ExperimentWasm):
                shutil.copyfile(
                    Path("static/index.html"),
                    e.dir_path / "index.html")

    def make(self):
        cwd = Path.cwd()
        os.chdir("out")
        subprocess.run(
            ["make", "-j4"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.chdir(cwd)
        logging.info("Finished make")

    def run_exps(self):
        for e in self.exps:
            e.run()


lab = Lab.from_yaml(Path("experiments.yaml"))
lab.clear_logs()
lab.mkdirs()
lab.create_makefile()
lab.copy_index_html()
lab.make()

lab.run_exps()
