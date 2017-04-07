import json
import math


# blocks specifies which pool found which block (as reported by blockchain.info)
with open('blocks') as f:
    lines = f.readlines()
suspects = {}
for line in lines:
    height, pool, block_hash = line[:-1].split('\t')
    if not suspects.get(pool):
        suspects[pool] = []
    # downloaded from blockchain.info/rawblocks/{block_hash}
    with open("cached_blocks/{}".format(block_hash)) as f:
        block = json.loads(f.read())
    num_tx = len(block["tx"])
    if num_tx == 1:
        continue
    merkle_depth = math.ceil(math.log(num_tx, 2))
    right_side_begin = int(2**(merkle_depth - 1))
    histogram = {}
    for tx in block["tx"][right_side_begin:]:
        fee = sum([i["prev_out"]["value"] for i in tx["inputs"]]) - \
              sum([o["value"] for o in tx["out"]])
        if not histogram.get(fee):
            histogram[fee] = 0
        histogram[fee] += 1
    num_right_side = num_tx - right_side_begin
    most_frequent = max([v for v in histogram.values()])
    percentage = round(most_frequent/float(num_right_side) * 100, 2)
    suspects[pool].append([most_frequent, percentage])

for k in sorted(suspects.keys()):
    print("{}: {}".format(k, suspects[k]))
