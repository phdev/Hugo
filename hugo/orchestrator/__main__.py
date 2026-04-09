"""Entry point for running Hugo via `python -m hugo.orchestrator`."""

from hugo.orchestrator.pipeline import run_loop

if __name__ == "__main__":
    run_loop()
