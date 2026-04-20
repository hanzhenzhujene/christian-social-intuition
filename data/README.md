# Data Map

This directory holds the benchmark source file path and the locked processed splits used by the released experiments.

## Layout

- `raw/`
  - local download target for the upstream Moral Stories source file
  - not committed in the public release
- `processed/`
  - committed benchmark artifacts used by the released pipeline

## Canonical processed files

- `candidate_pool_v1.jsonl`
  - the 150-item candidate pool after automated construction
- `item_review_v1.csv`
  - manual audit sheet used to accept/reject items and override tags
- `dev_items_locked_v1.jsonl`
  - 30-item locked development split
- `eval_items_locked_v1.jsonl`
  - 120-item locked evaluation split used for the paper

## Rebuild path

If you need to reconstruct the item workflow from upstream Moral Stories:

```bash
csi-sim fetch-moral-stories
csi-sim build-items
csi-sim apply-item-review
```

The public paper-facing release uses the committed locked splits rather than rebuilding them on every run.
