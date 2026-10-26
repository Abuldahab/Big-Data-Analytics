# MapReduce Word Count

A small MapReduce engine in Python (no Hadoop, no Spark).

- Input: each `.txt` file in the folder is one split
- Map: emits `(word, 1)` pairs
- Mappers run at the same time, one thread per split
- Combine + Partition: local subtotals, then each word goes to one of 2 reducers
- Shuffle & Sort, then Reduce: sums counts and writes one file per reducer

## Run

```
cd mapreduce-word-count
python mapreduce.py
```

Reads `../datasets/text-files` and writes `output/reducer_0.txt` and `output/reducer_1.txt`.
