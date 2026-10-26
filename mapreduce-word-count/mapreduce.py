import os
import sys
import threading

NUM_REDUCERS = 2


def map_split(path):
    pairs = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for word in f.read().lower().split():
            word = word.strip(".,!?;:\"'()[]{}")
            if word:
                pairs.append((word, 1))
    return pairs


def combine(pairs):
    counts = {}
    for word, one in pairs:
        counts[word] = counts.get(word, 0) + one
    return counts


def partition(counts):
    parts = [[] for _ in range(NUM_REDUCERS)]
    for word, count in counts.items():
        parts[hash(word) % NUM_REDUCERS].append((word, count))
    return parts


def mapper(path, results, i):
    pairs = map_split(path)
    counts = combine(pairs)
    results[i] = partition(counts)
    print(f"Mapper {i} finished {os.path.basename(path)}")


def shuffle_and_sort(results):
    reducer_inputs = [[] for _ in range(NUM_REDUCERS)]
    for parts in results:
        for r in range(NUM_REDUCERS):
            reducer_inputs[r].extend(parts[r])
    for r in range(NUM_REDUCERS):
        reducer_inputs[r].sort()
    return reducer_inputs


def reducer(r, pairs, output_dir):
    totals = {}
    for word, count in pairs:
        totals[word] = totals.get(word, 0) + count
    out_path = os.path.join(output_dir, f"reducer_{r}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        for word in sorted(totals):
            f.write(f"{word}\t{totals[word]}\n")
    print(f"Reducer {r} wrote {out_path}")


def main():
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "../datasets/text-files"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    os.makedirs(output_dir, exist_ok=True)

    files = [os.path.join(input_dir, f) for f in sorted(os.listdir(input_dir)) if f.endswith(".txt") and not f.startswith("expected")]
    results = [None] * len(files)

    threads = []
    for i, path in enumerate(files):
        t = threading.Thread(target=mapper, args=(path, results, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    reducer_inputs = shuffle_and_sort(results)

    for r in range(NUM_REDUCERS):
        reducer(r, reducer_inputs[r], output_dir)


if __name__ == "__main__":
    main()
