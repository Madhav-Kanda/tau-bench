import argparse
import os
import sys
from experiments.libgen.runner import LibGenExperimentRunner
from experiments.libgen.utils import load_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Generalized LibGen Experiment Runner")
    parser.add_argument("--config", type=str, required=True, help="Path to experiment config JSON")
    args = parser.parse_args()
    config_path = os.path.abspath(args.config)
    config = load_json(config_path)
    runner = LibGenExperimentRunner(config)
    runner.run()


if __name__ == "__main__":
    main()