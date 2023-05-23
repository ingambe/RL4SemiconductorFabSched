from simulation.classes import Lot, Machine
from simulation.randomizer import Randomizer

r = Randomizer()


class Dispatchers:
    
    @staticmethod
    def get_setup(new_setup, machine, actual_step_setup_time, setups):
        if new_setup != '' and machine.current_setup != new_setup:
            if actual_step_setup_time is not None:
                return actual_step_setup_time
            elif (machine.current_setup, new_setup) in setups:
                return setups[(machine.current_setup, new_setup)]
            elif ('', new_setup) in setups:
                return setups[('', new_setup)]
        return 0

    @staticmethod
    def fifo_ptuple_for_lot(lot: Lot, time, machine: Machine = None, setups=None):
        if machine is not None:
            lot.ptuple = (
                 0 if lot.cqt_waiting is not None else 1,
                 -lot.priority,
                0 if machine.min_runs_left is None or machine.min_runs_setup == lot.actual_step.setup_needed else 1,
                 Dispatchers.get_setup(lot.actual_step.setup_needed, machine, lot.actual_step.setup_time, setups),
                  lot.free_since, lot.deadline_at,
            )
            return lot.ptuple
        else:
            return 0 if lot.cqt_waiting is not None else 1, -lot.priority, lot.free_since, lot.deadline_at,

    @staticmethod
    def spt_ptuple_for_lot(lot: Lot, time, machine: Machine = None, setups=None):
        if machine is not None:
            lot.ptuple = (
                 0 if lot.cqt_waiting is not None else 1,
                 -lot.priority,
                0 if machine.min_runs_left is None or machine.min_runs_setup == lot.actual_step.setup_needed else 1,
                 Dispatchers.get_setup(lot.actual_step.setup_needed, machine, lot.actual_step.setup_time, setups),
                lot.actual_step.processing_time.avg(), lot.deadline_at,
            )
            return lot.ptuple
        else:
            return 0 if lot.cqt_waiting is not None else 1, -lot.priority, lot.actual_step.processing_time.avg(), lot.deadline_at,

    @staticmethod
    def srpt_ptuple_for_lot(lot: Lot, time, machine: Machine = None, setups=None):
        if machine is not None:
            lot.ptuple = (
                 0 if lot.cqt_waiting is not None else 1,
                 -lot.priority,
                0 if machine.min_runs_left is None or machine.min_runs_setup == lot.actual_step.setup_needed else 1,
                 Dispatchers.get_setup(lot.actual_step.setup_needed, machine, lot.actual_step.setup_time, setups),
                lot.remaining_time, lot.deadline_at,
            )
            return lot.ptuple
        else:
            return 0 if lot.cqt_waiting is not None else 1, -lot.priority, lot.remaining_time, lot.deadline_at,

    @staticmethod
    def hpt_ptuple_for_lot(lot: Lot, time, machine: Machine = None, setups=None):
        if machine is not None:
            lot.ptuple = (
                 0 if lot.cqt_waiting is not None else 1,
                 -lot.priority,
                0 if machine.min_runs_left is None or machine.min_runs_setup == lot.actual_step.setup_needed else 1,
                 Dispatchers.get_setup(lot.actual_step.setup_needed, machine, lot.actual_step.setup_time, setups),
                -lot.actual_step.processing_time.avg(), lot.deadline_at,
            )
            return lot.ptuple
        else:
            return 0 if lot.cqt_waiting is not None else 1, -lot.priority, -lot.actual_step.processing_time.avg(), lot.deadline_at,

    @staticmethod
    def setup_ptuple_for_lot(lot: Lot, time, machine: Machine = None, setups=None):
        if machine is not None:
            lot.ptuple = (
                 0 if lot.cqt_waiting is not None else 1,
                 -lot.priority,
                0 if machine.min_runs_left is None or machine.min_runs_setup == lot.actual_step.setup_needed else 1,
                 Dispatchers.get_setup(lot.actual_step.setup_needed, machine, lot.actual_step.setup_time, setups),
                 lot.deadline_at,
            )
            return lot.ptuple
        else:
            return 0 if lot.cqt_waiting is not None else 1, -lot.priority, 0 if lot.actual_step.setup_needed == "" else 1, lot.deadline_at,


    @staticmethod
    def edd_ptuple_for_lot(lot: Lot, time, machine: Machine = None, setups=None):
        if machine is not None:
            lot.ptuple = (
                 0 if lot.cqt_waiting is not None else 1,
                 -lot.priority,
                0 if machine.min_runs_left is None or machine.min_runs_setup == lot.actual_step.setup_needed else 1,
                Dispatchers.get_setup(lot.actual_step.setup_needed, machine, lot.actual_step.setup_time, setups),
                lot.deadline_at,
            )
            return lot.ptuple
        else:
            return 0 if lot.cqt_waiting is not None else 1, -lot.priority, lot.deadline_at,

    @staticmethod
    def cr_ptuple_for_lot(lot: Lot, time, machine: Machine = None, setups=None):
        if machine is not None:
            lot.ptuple = (
                 0 if lot.cqt_waiting is not None else 1,
                 -lot.priority,
                 0 if machine.min_runs_left is None or machine.min_runs_setup == lot.actual_step.setup_needed else 1,
                 Dispatchers.get_setup(lot.actual_step.setup_needed, machine, lot.actual_step.setup_time, setups),
                 lot.cr(time),
            )
            return lot.ptuple
        else:
            return 0 if lot.cqt_waiting is not None else 1, -lot.priority, lot.cr(time),
    
    @staticmethod
    def ls_ptuple_for_lot(lot: Lot, time, machine: Machine = None, setups=None):
        if machine is not None:
            lot.ptuple = (
                 0 if lot.cqt_waiting is not None else 1,
                 -lot.priority,
                 0 if machine.min_runs_left is None or machine.min_runs_setup == lot.actual_step.setup_needed else 1,
                 Dispatchers.get_setup(lot.actual_step.setup_needed, machine, lot.actual_step.setup_time, setups),
                 lot.deadline_at - lot.remaining_time,
            )
            return lot.ptuple
        else:
            return 0 if lot.cqt_waiting is not None else 1, -lot.priority, lot.deadline_at - lot.remaining_time,

    @staticmethod
    def random_ptuple_for_lot(lot: Lot, time, machine: Machine = None, setups=None):
        if machine is not None:
            return (
                0 if lot.cqt_waiting is not None else 1,
                0 if machine.min_runs_left is None or machine.min_runs_setup == lot.actual_step.setup_needed else 1,
                r.random.uniform(0, 99999),
            )
        else:
            return 0 if lot.cqt_waiting is not None else 1, r.random.uniform(0, 99999),


dispatcher_map = {
    'fifo': Dispatchers.fifo_ptuple_for_lot,
    'cr': Dispatchers.cr_ptuple_for_lot,
    'random': Dispatchers.random_ptuple_for_lot,
}
