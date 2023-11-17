#!/usr/bin/env python3

import logging
import subprocess

logging.basicConfig(
    filename="post-receive.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

cmd = "git --work-tree=/home/gaotianchi/repo/prod --git-dir=/home/gaotianchi/repo/remote checkout -f"

try:
    subprocess.run(cmd, shell=True, check=True)
    logging.info(f"Command [{cmd}] executed successfully.")
except subprocess.CalledProcessError as e:
    logging.error(
        f"Command execution failed with error code {e.returncode}: {e.output}"
    )
