# %% [markdown]
# ### Berth allocation problem
#
# 1910101

# %%
import matplotlib.patches as mpatches
from pylab import *
import pandas as pd
import numpy as np
import operator
from dataclasses import dataclass
import matplotlib.pyplot as plt
from time import time
import math
import argparse
import os


@dataclass()
class Node:
    time: int         # time axis -- rename needed
    pos: int          # position axis
    cls: np.array     # type: ignore

    def __eq__(self, other):
        return self.time == other.time and self.pos == other.pos and np.array_equal(self.cls, other.cls)

    def __key(self):
        return (self.time, self.pos, str(list(self.cls)))

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return "{ %d, %d, %s }" % (self.time, self.pos, 'lower' if self.cls[0] == 1 else 'upper')


# %% [markdown]
# Import the input

# %%
# Sensei's format
# with open('input1.txt', 'r') as file:
#     infos = file.read().split("\n\n")
#     berth_len = int(infos[0].split("\n")[1])
#     berth_breaks_list = [int(x) for x in infos[1].split("\n")[1:]]
#     vessels_list = [line.split("\t") for line in infos[2].split("\n")[1:-1]
# print(f"""Berth len: {berth_len}
# Berth breaks: {berth_breaks_list}""
# vessels_df = pd.DataFrame.from_dict({
#     "vessel_idx": [i for i in range(1, len(vessels_list) + 1)],
#     "size_": [int(v[1]) for v in vessels_list],
#     "t_arrive": [int(v[2]) for v in vessels_list],
#     "t_process": [int(v[3]) for v in vessels_list],
#     "weight": [int(v[4]) if len(v) == 5 else 1 for v in vessels_list],
# })
# print(vessels_df)

parser = argparse.ArgumentParser(description='Continuous Static Berth Allocation Problem')
parser.add_argument('--log_res', default=False)
parser.add_argument('--res_dest', default='result')
parser.add_argument('--log_fig', default=False)
parser.add_argument('--figs_dest', default='fig')
parser.add_argument('--start_test')
parser.add_argument('--end_test')
parser.add_argument('--with_heuristic', default=False)

args = parser.parse_args()

if args.start_test is None:
    args.start_test = 1

if args.end_test is None:
    args.end_test = args.start_test

if args.log_res:
    os.makedirs(args.res_dest, exist_ok=True)

if args.log_fig:
    os.makedirs(args.figs_dest, exist_ok=True)

# Our input
for test_idx in range(int(args.start_test), int(args.end_test) + 1):
    with open(f"input/input-{test_idx:02}.txt", 'r') as file:
        infos = file.read().split("\n")
        berth_len = int(infos[0].split(" ")[0])
        TIME_HORIZON = int(infos[0].split(" ")[1])
        num_breaks = int(infos[1])
        berth_breaks_list = [int(x) for x in infos[2:2 + num_breaks]]
        vessels_list = [line.split(" ") for line in infos[2 + num_breaks + 1:-1]]

    print(f"""Berth len: {berth_len}
    Berth breaks: {berth_breaks_list}
    Num of vessels: {len(vessels_list)}""")


    vessels_df = pd.DataFrame.from_dict({
        "vessel_idx": [i for i in range(1, len(vessels_list) + 1)],
        "size_": [int(v[1]) for v in vessels_list],
        "t_arrive": [int(v[2]) for v in vessels_list],
        "t_process": [int(v[3]) for v in vessels_list],
        "weight": [int(v[4]) if len(v) == 5 else 1 for v in vessels_list],
    })
    print(vessels_df)

    # %% [markdown]
    # Construction phase
    #   1. Input the packing of previous `n-1` vessels and (size, t_arrive, t_process) of vessel `n`
    #   2. Classify nodes within ABCD to 5 classes, turn `[1,0,1,0]` and `[0,1,0,1]` nodes into Class1's
    #   3. Group C1 = `[1,0,0,0]` and `[0,0,0,1]` nodes, C3 = Class3 nodes
    #   4. Extend nodes in C3 to edges of the hole, add intersections to I1 and I2, update I1 and I2 vectors accordingly
    #   5. Test feasibility & optimality in C1 + I1 + I2 nodes
    #
    # Assume that there are `k` feasible positions, calculate Cost = sum(w(c - a)) for each position, filter "bad" positions relative to others.
    #
    # After screening, use a probability to choose the berth position among the candidates.

    # %%
    TIME_HORIZON = sum(vessels_df.t_process)
    ABCD_right = TIME_HORIZON
    ABCD_top = berth_len
    ABCD_bot = 0


    def generate_packing(sorted_df, log=True):

        packing = pd.DataFrame.from_dict({
            "vessel_idx": [0 for _ in range(len(berth_breaks_list))],
            "t_moore": [0 for _ in range(len(berth_breaks_list))],
            "t_finish": [TIME_HORIZON for _ in range(len(berth_breaks_list))],
            "p_start": [pos for pos in berth_breaks_list],
            "p_end": [pos for pos in berth_breaks_list],
            "t_wait": [0 for _ in berth_breaks_list],
        })

        # Take packing info and current vessel info
        for row in sorted_df.index:
            vessel = sorted_df.loc[row]
            if log:
                print(
                    f"🛳️ Vessel_{vessel.vessel_idx}, 📏 {vessel.size_}, ⏱️ {vessel.t_arrive}~{vessel.t_process}.")

            # If this cut through a block then it is a moore point
            ABCD_left = vessel.t_arrive

            # Set of vertical and horizontal lines to construct grid
            verticals = set([ABCD_left, ABCD_right])
            horizontals = set([ABCD_bot, ABCD_top])

            v_blobs = []
            h_blobs = []

            # Construct grid
            for idx in packing.index:
                rect = packing.loc[idx]
                if rect.t_finish > ABCD_left:
                    verticals.add(rect.t_finish)
                    horizontals.add(rect.p_start)  # type: ignore
                    horizontals.add(rect.p_end)  # type: ignore

                    h_blobs.append((rect.p_start, rect.p_end))
                    # type: ignore
                    v_blobs.append((max([rect.t_moore, ABCD_left]), rect.t_finish))

                if rect.t_moore > ABCD_left:
                    verticals.add(rect.t_moore)

            # Classify nodes
            t_moore_s = list(set(packing.t_moore.add(ABCD_left)))
            t_moore_s.sort()
            t_finish_es = list(set(packing.t_finish))
            t_finish_es.sort()
            p_start_s = list(set(packing.p_start))
            p_start_s.sort()
            p_end_s = list(set(packing.p_end))
            p_end_s.sort()
            nodes = []
            for time in verticals:
                for pos in horizontals:
                    new_node = Node(time, pos, np.array(
                        [1, 1, 1, 1]))  # type: ignore
                    walls = np.array([
                        time in t_moore_s and pos in p_start_s and pos not in p_end_s or time >= ABCD_right or pos >= ABCD_top,
                        time in t_finish_es and pos in p_start_s or time <= ABCD_left or pos >= ABCD_top,
                        time in t_finish_es and pos in p_end_s or time <= ABCD_left or pos <= ABCD_bot,
                        time in t_moore_s and pos in p_end_s or time >= ABCD_right or pos <= ABCD_bot
                    ])
                    new_node.cls -= walls

                    # Add missing vincinities
                    v_overlap = list(filter(
                        lambda bounds: bounds[1][0] <= time and time <= bounds[1][1], enumerate(v_blobs)))
                    h_overlap = [h_blobs[i] for i, _ in v_overlap]
                    v_overlap = [v for _, v in v_overlap]
                    for vb, hb in zip(v_overlap, h_overlap):
                        if hb[0] > pos or pos > hb[1]:
                            continue
                        vin = np.array([
                            not(time < vb[1] and pos < hb[1]),
                            not(time > vb[0] and pos < hb[1]),
                            not(time > vb[0] and pos > hb[0]),
                            not(time > vb[1] and pos > hb[0]),
                        ])
                        new_node.cls *= vin

                    # Turn Class 2 node into Class 1 nodes
                    if np.array_equal(new_node.cls, np.array([1, 0, 1, 0])):
                        nodes.append(
                            Node(new_node.time, new_node.pos, np.array([1, 0, 0, 0])))
                        nodes.append(
                            Node(new_node.time, new_node.pos, np.array([0, 0, 1, 0])))
                    elif np.array_equal(new_node.cls, np.array([0, 1, 0, 1])):
                        nodes.append(
                            Node(new_node.time, new_node.pos, np.array([0, 1, 0, 0])))
                        nodes.append(
                            Node(new_node.time, new_node.pos, np.array([0, 0, 0, 1])))
                    else:
                        nodes.append(new_node)

            # Grouping nodes to form a list of possible corner to stuck the next vessel in
            C1 = list(filter(
                lambda node: np.array_equal(node.cls, [1, 0, 0, 0]) or np.array_equal(node.cls, [0, 0, 0, 1]), nodes))
            C3 = list(filter(lambda node: np.sum(node.cls) == 3, nodes))
            I1 = []
            for node in C3:
                if node.cls[0] == 0:
                    # Extend leftwards
                    same_pos_nodes = list(
                        filter(lambda n: n.pos == node.pos, nodes))
                    same_pos_nodes.sort(
                        key=operator.attrgetter("time"), reverse=True)
                    # Get the first node that is not a Class4 (empty space) node
                    extended = next(
                        filter(lambda n: n.time < node.time and sum(n.cls) != 4, same_pos_nodes))
                    I1.append(Node(extended.time, extended.pos,
                            np.array([0, 0, 0, 1])))

                elif node.cls[3] == 0:
                    # Extend leftwards
                    same_pos_nodes = list(
                        filter(lambda n: n.pos == node.pos, nodes))
                    same_pos_nodes.sort(
                        key=operator.attrgetter("time"), reverse=True)
                    extended = next(
                        filter(lambda n: n.time < node.time and sum(n.cls) != 4, same_pos_nodes))
                    I1.append(Node(extended.time, extended.pos,
                            np.array([1, 0, 0, 0])))

                elif node.cls[1] == 0:
                    # Extend downwards
                    same_time_nodes = list(
                        filter(lambda n: n.time == node.time, nodes))
                    same_time_nodes.sort(
                        key=operator.attrgetter("pos"), reverse=True)
                    extended = next(
                        filter(lambda n: n.pos < node.pos and sum(n.cls) != 4, same_time_nodes))
                    I1.append(Node(extended.time, extended.pos,
                            np.array([1, 0, 0, 0])))

                else:
                    # Extend upwards
                    same_time_nodes = list(
                        filter(lambda n: n.time == node.time, nodes))
                    same_time_nodes.sort(key=operator.attrgetter("pos"))
                    extended = next(
                        filter(lambda n: n.pos > node.pos and sum(n.cls) != 4, same_time_nodes))
                    I1.append(Node(extended.time, extended.pos,
                            np.array([0, 0, 0, 1])))

            # Intersections of lines in I1, can defer this and do this later
            I2 = []
            POSSIBLE = list(set(I1 + C1))

            # Test feasibility
            pruned_list = []
            for position in POSSIBLE:
                time_range = (position.time, position.time + vessel.t_process)
                pos_range = (position.pos, position.pos + vessel.size_) if position.cls[0] else \
                            (position.pos - vessel.size_, position.pos)
                if pos_range[1] > berth_len or pos_range[0] < 0:
                    continue
                # Check if this range overlap any blobs
                idx_v_overlap = list(filter(
                    lambda bounds: bounds[1][0] < time_range[1] and time_range[0] < bounds[1][1], enumerate(v_blobs)))
                h_ = [h_blobs[i] for i, _ in idx_v_overlap]
                h_overlap = list(filter(
                    lambda bounds: bounds[0] < pos_range[1] and pos_range[0] < bounds[1], h_))
                v_overlap = [v for _, v in idx_v_overlap]
                if len(h_overlap) != 0:
                    # print(f"{position} overlap with {h_overlap}, {v_overlap}")
                    pass
                else:
                    pruned_list.append(position)
            POSSIBLE = pruned_list

            # Test optimality: for same positions and class, nodes that starts sooner is better

            # # Calculate cost of the above positions by makespan
            # makespans = []
            # for position in POSSIBLE:
            #     if len(packing.t_finish) == len(berth_breaks_list):
            #         break
            #     this_t_finish = packing.t_finish[len(berth_breaks_list):].copy() + [position.time + vessel.t_process]
            #     makespans.append(max(sorted_df.weight[:len(this_t_finish)] * np.array(this_t_finish)))
            # min_pos = np.argmin(makespans) if len(makespans) else 0

            # Calculate cost of the above positions by wait time
            waits = []
            padding = len(berth_breaks_list)
            POSSIBLE.sort(key=operator.attrgetter("pos"))
            for position in POSSIBLE:
                if len(packing.t_finish) == padding:
                    break
                this_t_wait = packing.t_wait[padding:].copy() + [position.time - vessel.t_arrive]
                waits.append(
                    sum(sorted_df.weight[:len(this_t_wait)] * np.array(this_t_wait)))
            min_pos = np.argmin(waits) if len(waits) else 0

            # Filter worse positions
            # Choose one position acc. to a probability

            if len(POSSIBLE) == 0:
                print("No solution can be found!!!")
                return None, None

            position = POSSIBLE[min_pos]
            packing.loc[len(packing.index)] = [  # type: ignore
                vessel.vessel_idx,
                position.time,
                position.time + vessel.t_process,
                position.pos if position.cls[0] else position.pos - vessel.size_,
                position.pos + vessel.size_ if position.cls[0] else position.pos,
                position.time - vessel.t_arrive
            ]

            result = packing.tail(1)
            if log:
                print(
                    f"⚓ Vessel_{vessel.vessel_idx}, 📌 {int(result.p_start)}-{int(result.p_end)}, ⌛ {int(result.t_moore)}-{int(result.t_finish)}.")
                print("")

            # print("💡Positions: " + ",".join([str(p) for p in POSSIBLE]))
            # print(nodes)
            # print("💡Possible positions: ", POSSIBLE)
            # print(C1, C3)

        if log:
            print("Makespan: ", max(packing.t_finish[padding:]))
            print("Weighted makespan: ", max(np.array(sorted_df.weight)
                * np.array(packing.t_finish[len(berth_breaks_list):])))
            print("Weighted wait time: ", waits[min_pos])

        return packing, waits[min_pos]


    # %%
    sorted_df = vessels_df.sort_values(by=['t_arrive'])
    print(sorted_df)

    # %%
    t1 = time()
    # The original sorted df
    res, score = generate_packing(sorted_df, log=True)
    other_packings = [(res, score)]

    # Swap adjacent ships to best preserve ordering
    if args.with_heuristic:
        for index in range(len(vessels_df) - 1):
            new_df = pd.DataFrame.from_records(sorted_df)
            r1, r2 = new_df.iloc[index].copy(), new_df.iloc[index + 1].copy()
            new_df.iloc[index], new_df.iloc[index + 1] = r2, r1

            result, score = generate_packing(new_df, log=False)
            other_packings.append((result, score))

    t2 = time()

    # %%
    min_wait = np.argmin(
        [t if t is not None else math.inf for (_, t) in other_packings])
    print(f"Heuristic finished in {t2 - t1} secs.")
    print(f"Min wait time: {other_packings[min_wait][1]}")

    if args.log_res:
        with open(f"{args.res_dest}/result-{test_idx:02}.txt", 'a') as file:
            file.write(f"Input {test_idx}\n")
            file.write(f"Min wait time: {other_packings[min_wait][1]}\n")
            file.write(f"Execution time: {t2 - t1}")

    # TUAN QM VIS.

    if args.log_fig:
        # Draw plot

        fig = plt.figure()
        ax = fig.add_subplot(111)

        # Grid
        grid(color='b', linestyle='-', linewidth=0.7, alpha=0.4)

        # Bright color
        low = 0.6
        high = 0.95
        if other_packings[min_wait][0] is None:
            continue

        for i in other_packings[min_wait][0].index:
            row = other_packings[min_wait][0].loc[i]
            if row.vessel_idx == 0:
                continue
            rgb = (np.random.uniform(low=low, high=high),
                np.random.uniform(low=low, high=high),
                np.random.uniform(low=low, high=high))
            rect = mpatches.Rectangle(
                (row.t_moore, row.p_start),
                row.t_finish - row.t_moore,
                row.p_end - row.p_start,
                fill=True,
                facecolor=rgb,
                edgecolor='black',
                linewidth=1,
                zorder=4)
            plt.gca().add_patch(rect)

            rx, ry = rect.get_xy()
            cx = rx + rect.get_width()/2.0
            cy = ry + rect.get_height()/2.0
            ax.annotate(str(row.vessel_idx if row.vessel_idx > 0 else ''), (cx, cy),
                        color='black', weight='bold', fontsize=10, ha='center', va='center', zorder=5)


        finish_times = other_packings[min_wait][0].t_finish[len(berth_breaks_list):]
        print(finish_times)

        end_time = max(finish_times)

        print(end_time)

        for i in berth_breaks_list:
            plot([0, end_time], [i, i], linestyle='dashed', c=(0, 0, 0), linewidth=1.5)

        # Draw Ox, Oy axis
        left, right = ax.get_xlim()
        low, high = ax.get_ylim()
        arrow(left, 0, right - left, 0, length_includes_head=True, head_width=0.55)
        arrow(0, low, 0, high-low, length_includes_head=True, head_width=0.55)

        # Show grid
        # show()

        fig.savefig(f"{args.figs_dest}/fig-{test_idx:02}.png")
