from collections import defaultdict
from math import ceil

from simulation.plugins.interface import IPlugin


class CostPlugin(IPlugin):

    def on_sim_done(self, instance):
        super().on_sim_done(instance)
        self.cost = 0
        for lot in instance.done_lots:
            self.cost += 25 if lot.deadline_at < lot.done_at else 0
            self.cost += ceil(max(0, lot.done_at - lot.deadline_at) / 3600 / 24)
        self.cost += len(instance.active_lots) * 200
        self.done_lots = len(instance.done_lots)

    def get_output_name(self):
        super().get_output_name()
        return 'cost'

    def get_output_value(self):
        return self.cost


class PierreCostPlugin(IPlugin):

    def on_sim_done(self, instance):
        super().on_sim_done(instance)
        self.cost = 0
        self.lot_type_cost = defaultdict(int)
        self.lot_type_cost_nb = defaultdict(int)
        self.lot_type_priority = defaultdict(int)
        for lot in instance.done_lots:
            if lot.done_at > 3600 * 24 * 365:
                self.lot_type_cost_nb[lot.name] += 1
                self.lot_type_cost[lot.name] += 10 if lot.deadline_at < lot.done_at else 0
                self.lot_type_cost[lot.name] += max(0, lot.done_at - lot.deadline_at) / (3600 * 24)
                self.lot_type_priority[lot.name] = lot.priority

        for lot_name in self.lot_type_cost:
            self.cost += self.lot_type_priority[lot_name] * (self.lot_type_cost[lot_name] / self.lot_type_cost_nb[lot_name])

        self.lot_type_cost = defaultdict(int)
        self.lot_type_cost_nb = defaultdict(int)
        for lot in instance.active_lots:
            self.lot_type_cost_nb[lot.name] += 1
            lot.deadline_at = lot.deadline_at - 2 * lot.remaining_time
            self.lot_type_cost[lot.name] += 10 if lot.deadline_at < instance.current_time else 0
            self.lot_type_cost[lot.name] += max(0, instance.current_time - lot.deadline_at) / (3600 * 24)

        for lot_name in self.lot_type_cost:
            self.cost += self.lot_type_priority[lot_name] * (self.lot_type_cost[lot_name] / self.lot_type_cost_nb[lot_name])

        self.done_lots = len(instance.done_lots)


        columns = ['lot name', 'in progress', 'completed', 'completed on time', 'on time percent', 'average cycle time',
                   'theoretical processing time']
        groups = defaultdict(lambda: defaultdict(lambda: 0))
        for lot in instance.active_lots:
            groups[lot.name]['in progress'] += 1
        for lot in instance.done_lots:
            if lot.done_at > 3600 * 24 * 365:
                groups[lot.name]['completed'] += 1
                if lot.done_at <= lot.deadline_at:
                    groups[lot.name]['completed on time'] += 1
                groups[lot.name]['on time percent'] = round(
                    groups[lot.name]['completed on time'] / groups[lot.name]['completed'] * 100, 2)
                groups[lot.name]['act_sum'] += lot.done_at - lot.release_at
                groups[lot.name]['average cycle time'] = round(
                    groups[lot.name]['act_sum'] / groups[lot.name]['completed'] / 3600 / 24, 2)
                groups[lot.name]['theoretical processing time'] = round(lot.full_time / 3600 / 24, 2)

        rows = []
        for k, v in groups.items():
            r = [k]
            for c in columns[1:]:
                r.append(v[c])
            rows.append(r)
        rows.sort(key=lambda k: k[0])
        labels = [rows[i][0] for i in range(len(rows))]
        rows = [rows[i][1:] for i in range(len(rows))]
        self.output = (self.cost, labels, rows)

    def get_output_name(self):
        super().get_output_name()
        return 'cost'

    def get_output_value(self):
        return self.cost

class PierreCostPlugin(IPlugin):

    def on_sim_done(self, instance):
        super().on_sim_done(instance)
        self.cost = 0
        self.lot_type_cost = defaultdict(int)
        self.lot_type_cost_nb = defaultdict(int)
        self.lot_type_priority = defaultdict(int)
        self.act_sum = defaultdict(int)
        for lot in instance.done_lots:
            if lot.done_at > 3600 * 24 * 365:
                self.lot_type_cost_nb[lot.name] += 1
                self.lot_type_cost[lot.name] += 10 if lot.deadline_at < lot.done_at else 0
                self.lot_type_cost[lot.name] += max(0, lot.done_at - lot.deadline_at) / (3600 * 24)
                self.lot_type_priority[lot.name] = lot.priority
                self.act_sum[lot.name] += lot.done_at - lot.release_at

        self.avg_cycle_time = defaultdict(float)
        for lot_name in self.lot_type_cost:
            self.cost += self.lot_type_priority[lot_name] * (self.lot_type_cost[lot_name] / self.lot_type_cost_nb[lot_name])
            self.avg_cycle_time[lot_name] = round(self.act_sum[lot_name] / self.lot_type_cost_nb[lot_name] / 3600 / 24, 2)


        self.lot_type_cost = defaultdict(int)
        self.lot_type_cost_nb = defaultdict(int)
        for lot in instance.active_lots:
            self.lot_type_cost_nb[lot.name] += 1
            lot.deadline_at = lot.deadline_at - self.avg_cycle_time[lot.name] * lot.remaining_time
            self.lot_type_cost[lot.name] += 10 if lot.deadline_at < instance.current_time else 0
            self.lot_type_cost[lot.name] += max(0, instance.current_time - lot.deadline_at) / (3600 * 24)

        for lot_name in self.lot_type_cost:
            self.cost += self.lot_type_priority[lot_name] * (self.lot_type_cost[lot_name] / self.lot_type_cost_nb[lot_name])

        self.done_lots = len(instance.done_lots)


        columns = ['lot name', 'in progress', 'completed', 'completed on time', 'on time percent', 'average cycle time',
                   'theoretical processing time']
        groups = defaultdict(lambda: defaultdict(lambda: 0))
        for lot in instance.active_lots:
            groups[lot.name]['in progress'] += 1
        for lot in instance.done_lots:
            if lot.done_at > 3600 * 24 * 365:
                groups[lot.name]['completed'] += 1
                if lot.done_at <= lot.deadline_at:
                    groups[lot.name]['completed on time'] += 1
                groups[lot.name]['on time percent'] = round(
                    groups[lot.name]['completed on time'] / groups[lot.name]['completed'] * 100, 2)
                groups[lot.name]['act_sum'] += lot.done_at - lot.release_at
                groups[lot.name]['average cycle time'] = round(
                    groups[lot.name]['act_sum'] / groups[lot.name]['completed'] / 3600 / 24, 2)
                groups[lot.name]['theoretical processing time'] = round(lot.full_time / 3600 / 24, 2)

        rows = []
        for k, v in groups.items():
            r = [k]
            for c in columns[1:]:
                r.append(v[c])
            rows.append(r)
        rows.sort(key=lambda k: k[0])
        labels = [rows[i][0] for i in range(len(rows))]
        rows = [rows[i][1:] for i in range(len(rows))]
        self.output = (self.cost, labels, rows)

    def get_output_name(self):
        super().get_output_name()
        return 'cost'

    def get_output_value(self):
        return self.cost
