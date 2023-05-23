import argparse
import os
import random
import sys
import ray
import cloudpickle

import numpy as np
import torch
import wandb

from simulation.classes import Lot
from simulation.dispatching.dispatcher import Dispatchers
from simulation.greedy import build_batch
from simulation.plugins.stats_plugin import StatPlugin
from simulation.randomizer import Randomizer



def get_lots_to_dispatch_by_lot(
    instance, current_time, last_sort_time
):
    if last_sort_time != current_time:
        for lot in instance.usable_lots:
            lot.ptuple = Dispatchers.fifo_ptuple_for_lot(lot, current_time, None)
        last_sort_time = current_time
        instance.usable_lots.sort(key=lambda k: k.ptuple)
    lots = instance.usable_lots
    setup_machine, setup_batch = None, None
    min_run_break_machine, min_run_break_batch = None, None
    family_lock = None
    for i in range(len(lots)):
        lot: Lot = lots[i]
        if family_lock is None or family_lock == lot.actual_step.family:
            family_lock = lot.actual_step.family
            # assert len(lot.waiting_machines) > 0
            if lot.actual_step.setup_needed == "":
                for machine in lot.waiting_machines:
                    if machine.current_setup == "":
                        return machine, build_batch(lot, lots[i + 1 :]), last_sort_time
            for machine in lot.waiting_machines:
                if (
                    lot.actual_step.setup_needed == ""
                    or lot.actual_step.setup_needed == machine.current_setup
                ):
                    return machine, build_batch(lot, lots[i + 1 :]), last_sort_time
                else:
                    if setup_machine is None and machine.min_runs_left is None:
                        setup_machine = machine
                        setup_batch = i
                    if min_run_break_machine is None:
                        min_run_break_machine = machine
                        min_run_break_batch = i
    if setup_machine is not None:
        return (
            setup_machine,
            build_batch(lots[setup_batch], lots[setup_batch + 1 :]),
            last_sort_time,
        )
    return (
        min_run_break_machine,
        build_batch(lots[min_run_break_batch], lots[min_run_break_batch + 1 :]),
        last_sort_time,
    )

@ray.remote
def one_pop_iter(seed: int, run_to: int, dataset: str):
    plugins = [StatPlugin()]
    # master_instance = FileInstance(files, run_to, False, plugins)
    if dataset == 'HVLM':
        with open("365days_HVLM.pkl", mode="rb") as file:
            instance = cloudpickle.load(file, fix_imports=True)
            instance.plugins = plugins
            for plugin in plugins:
                plugin.on_sim_init(instance)
    elif dataset == 'LVHM':
        with open("365days_LVHM.pkl", mode="rb") as file:
            instance = cloudpickle.load(file, fix_imports=True)
            instance.plugins = plugins
            for plugin in plugins:
                plugin.on_sim_init(instance)
    with torch.no_grad():
        random.seed(seed)
        os.environ["PYTHONHASHSEED"] = str(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        Randomizer().random.seed(seed)
        last_sort_time = -1
        while not instance.done:
            done = instance.next_decision_point()
            if done or instance.current_time > run_to:
                break
            machine, lots, last_sort_time = get_lots_to_dispatch_by_lot(
                instance, instance.current_time, last_sort_time
            )
            if lots is None:
                instance.usable_lots.clear()
                instance.lot_in_usable.clear()
                instance.next_step()
            else:
                instance.dispatch(machine, lots)
        instance.finalize()
        cost, rows = instance.plugins[0].get_output_value()
        return cost, rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", type=str, default="HVLM")
    p.add_argument("--days", type=int, default=365)
    a = p.parse_args()
    wandb.init(project="benchmark-fab-RL", tags=[a.dataset], group="static_dispatching")

    sys.stderr.write(f"Loading {a.dataset} for static greedy {a.days} \n")
    sys.stderr.flush()
    a.days += 365
    nb_workers = 100

    run_to = 3600 * 24 * a.days
    Randomizer().random.seed(0)

    random.seed(0)
    os.environ["PYTHONHASHSEED"] = str(0)
    np.random.seed(0)
    torch.manual_seed(0)
    torch.cuda.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.backends.cudnn.deterministic = True

    plugins = [StatPlugin()]
    # master_instance = FileInstance(files, run_to, False, plugins)
    if a.dataset == 'HVLM':
        with open("365days_HVLM.pkl", mode="rb") as file:
            master_instance = cloudpickle.load(file, fix_imports=True)
            master_instance.plugins = plugins
            for plugin in plugins:
                plugin.on_sim_init(master_instance)
    elif a.dataset == 'LVHM':
        with open("365days_LVHM.pkl", mode="rb") as file:
            master_instance = cloudpickle.load(file, fix_imports=True)
            master_instance.plugins = plugins
            for plugin in plugins:
                plugin.on_sim_init(master_instance)
    else:
        print("NO WARMED INSTANCE FOR THIS")
        assert False
    output_iter = ray.get(
        [
            one_pop_iter.remote(k, run_to, a.dataset)
            for k in range(nb_workers)
        ]
    )
    output_iter = np.array(output_iter, dtype=object)
    cost = np.array(output_iter[:, 0], dtype=float)
    rows = np.array(output_iter[:, 1], dtype=list)
    mean_result = []
    std_result = []
    for i in range(len(rows[0])):
        all_rows = []
        name = ''
        for j in range(nb_workers):
            all_rows.append(rows[j][i][1:])
            name = rows[j][i][0]
        all_rows = np.array(all_rows)
        mean_all_rows = [name] + list(np.mean(all_rows, axis=0))
        std_all_rows = [name] + list(np.std(all_rows, axis=0))
        mean_result.append(mean_all_rows)
        std_result.append(std_all_rows)
    print(f'Greedy with {nb_workers} runs')
    print(f'mean cost {cost.mean()}')
    print(f'std cost {cost.std()}')
    print('Mean results')
    print(mean_result)
    print('Std results')
    print(std_result)
    columns = ['lot name', 'in progress', 'completed', 'completed on time', 'on time percent', 'average cycle time',
               'theoretical processing time']
    html = '<table border="1"><thead><tr>' + \
           ''.join([f'<th>{c}</th>' for c in columns]) + \
           '</tr></thead><tbody>' + \
           ''.join(['<tr>' + ''.join([f'<td>{c} ± {s} </td>' for c, s in zip(row1, row2)]) + '</tr>' for row1, row2 in zip(mean_result, std_result)]) + \
           '</tbody></table>'
    wandb.log({
        'lot_stats': wandb.Html(html)
    })


if __name__ == "__main__":
    main()

