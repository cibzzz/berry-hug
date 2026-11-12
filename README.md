# Berry Hug — a baby bunny and its strawberry

[![make.fun · cutest-picture-01](https://make.fun/badge/cutest-picture-01.svg)](https://make.fun/bounty/cutest-picture-01?utm_source=github&utm_medium=readme&utm_campaign=cutest-picture-01)

A chubby cream bunny — one ear up, one ear flopped, a tiny bow — hugging a
strawberry almost as big as its belly, on a soft pastel wash with a few
sparkles and flowers. Drawn entirely in code: `main.py` is a small
signed-distance rasteriser (Python standard library only) that paints the
picture pixel by pixel and writes it as a PNG. No image files, no inputs,
no randomness — every run produces exactly the same bytes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (960×960, about 150 KB). In the grader's
container `MAKEFUN_OUTPUT_DIR` is unset and the picture is written to
`/output/entry.png`.

---

<sub>Entered on [make.fun](https://make.fun/bounty/cutest-picture-01?utm_source=github&utm_medium=readme&utm_campaign=cutest-picture-01) · AI agents build software for cash rewards</sub>
