"""make_figures.py: fixture Python entry point (never run by census.py)."""
import subprocess


def main():
    subprocess.run(["python3", "plot_helpers.py"], check=True)


if __name__ == "__main__":
    main()
