import argparse
import os
from pathlib import Path

import performance
import settings_data
import simulation


def create_directories(parent: str) -> tuple[Path, Path]:
    _parent = Path(parent)
    _quality = _parent / '01_quality'
    _performance = _parent / '02_performance'
    os.makedirs(_quality, exist_ok=True)
    os.makedirs(_performance, exist_ok=True)
    return _quality, _performance


EXPERIMENT_TYPE_QUALITY = 'quality'
EXPERIMENT_TYPE_PERFORMANCE = 'performance'
EXPERIMENT_TYPE = {
    EXPERIMENT_TYPE_QUALITY: True,
    EXPERIMENT_TYPE_PERFORMANCE: True
}

parser = argparse.ArgumentParser()

parser.add_argument('-o', '--output-dir', type=str, required=True)
parser.add_argument('-n', '--services', nargs='+', type=int,
                    help='manually set the number of services for the experiments')
parser.add_argument('-d', '--trust-attributes', nargs='+', type=int,
                    help='manually set the number of trust attributes for the experiments')
parser.add_argument('--n-changes', type=int, default=settings_data.N_CHANGES,
                    help='manually set the number of changes for the experiments')
parser.add_argument('--n-executions', type=int, default=settings_data.N_EXECUTIONS,
                    help='manually set the number of executions for the experiments')
parser.add_argument('-s', '--skip', nargs='*', help='skip experiments',
                    choices=[EXPERIMENT_TYPE_QUALITY, EXPERIMENT_TYPE_PERFORMANCE], )
parser.add_argument('--overwrite', action='store_true', default=True,)
parser.add_argument('-J', '--jobs', type=int, default=-1, help='number of jobs to run in parallel')

args = parser.parse_args()

output_dir = args.output_dir

if args.services is not None:
    settings_data.N_SERVICES = args.services
if args.trust_attributes is not None:
    settings_data.N_TRUST_ATTRIBUTES = args.trust_attributes
if args.n_changes is not None:
    settings_data.N_CHANGES = args.n_changes
if args.n_executions is not None:
    settings_data.N_EXECUTIONS = args.n_executions

if args.skip is not None:
    for e in args.skip:
        EXPERIMENT_TYPE[e] = False

print(f'Running with {settings_data.N_SERVICES} services and {settings_data.N_TRUST_ATTRIBUTES} trust attributes')

# create directories
if os.path.exists(output_dir):
    if not args.overwrite:
        print('Output directory already exists and overwrite set to False.')
        exit(0)
    else:
        quality_dir, performance_dir = create_directories(output_dir)
else:
    quality_dir, performance_dir = create_directories(output_dir)

# and run the experiments.
if EXPERIMENT_TYPE[EXPERIMENT_TYPE_QUALITY]:
    print('Quality...')
    simulation.run_all_experiments(output_dir=quality_dir, n_jobs=args.jobs)
if EXPERIMENT_TYPE[EXPERIMENT_TYPE_PERFORMANCE]:
    print('Performance...')
    performance.run_all_performance(output_dir=performance_dir, dataset_dir=quality_dir, n_jobs=args.jobs)
