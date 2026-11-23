"""
VeriCBAM Master Deterministic Reproduction Pipeline.
Executes the active 5-stage scientific evaluation pipeline and test suite end-to-end.
"""

import subprocess
import sys
import time
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parents[1]


def run_step(step_name: str, cmd: list) -> bool:
    print(f"\n[{time.strftime('%H:%M:%S')}] >>> STEP: {step_name}")
    start = time.time()
    res = subprocess.run(cmd, cwd=WORKSPACE_ROOT, capture_output=True, text=True)
    elapsed = time.time() - start
    if res.returncode == 0:
        print(f"[{time.strftime('%H:%M:%S')}] OK ({elapsed:.2f}s)")
        return True
    print(f"[{time.strftime('%H:%M:%S')}] FAILED ({elapsed:.2f}s)\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    return False


def main():
    print("VeriCBAM Master Reproduction Pipeline (Active 325-Case Suite)")
    steps = [
        ("1. Rebuild Multi-Pollutant Cohort from EEA Tables", [sys.executable, "src/data_loaders/build_cohort.py"]),
        ("2. Rebuild Verified Technology Registry", [sys.executable, "src/data_loaders/technology_registry.py"]),
        ("3. Generate 325-Case Graded Benchmark", [sys.executable, "src/benchmark/graded_benchmark_generator.py"]),
        ("4. Execute Graded Benchmark & Stage 2 EO Evaluation", [sys.executable, "experiments/run_graded_evaluation.py"]),
        ("5. Run Automated Pytest Suite", [sys.executable, "-m", "pytest", "-v"]),
    ]
    for name, cmd in steps:
        if not run_step(name, cmd):
            sys.exit(1)
    print("\nALL 5 PIPELINE STEPS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
