# Optional: fill a profile README's top 5 (NOT enabled)

The top-5 list is the `top5` rank (1 to 5) in `data/entries.json`. The same block can be written into any README that contains these markers:

```
<!-- radar:top5:start -->
<!-- radar:top5:end -->
```

Manual use (nothing runs automatically):

```
python scripts/radar.py top5                          # print the block
python scripts/radar.py top5 --write path/README.md   # replace the marker block
```

To automate it later, add a job that checks out the profile repository with a token scoped to that one repository (`contents: write`), runs the command above and opens a pull request instead of pushing. No such job exists in this repository today; enabling it is a deliberate owner decision.
