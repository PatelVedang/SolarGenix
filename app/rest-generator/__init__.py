import os
import subprocess


def main():
    script_path = os.path.join(os.path.dirname(__file__), "rest_generator.sh")
    subprocess.call(["bash", script_path])
