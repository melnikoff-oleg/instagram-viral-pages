#!/usr/bin/env python3
"""Download generation results into a run folder.

    python3 full-pipeline/fetch-results.py <run> candidates 11=https://... 12=https://... 
    python3 full-pipeline/fetch-results.py <run> clips 1=https://...mp4 2=https://...mp4

The subfolder (candidates, clips, ...) is created inside the run. Names keep the extension of
the URL; clip indices are zero-padded to two digits (1 -> 01.mp4). Runs the downloads in parallel.
"""
import sys, urllib.request, concurrent.futures as cf
from pathlib import Path


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    run, sub = Path(sys.argv[1]), sys.argv[2]
    out = run / sub
    out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for arg in sys.argv[3:]:
        name, url = arg.split("=", 1)
        ext = Path(url.split("?")[0]).suffix or ".bin"
        if name.isdigit() and len(name) == 1:
            name = f"0{name}"
        jobs.append((out / f"{name}{ext}", url))

    def get(job):
        path, url = job
        urllib.request.urlretrieve(url, path)
        return path

    with cf.ThreadPoolExecutor(8) as ex:
        for p in ex.map(get, jobs):
            print(f"   {p.relative_to(run)}  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
