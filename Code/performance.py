import json
import subprocess
from pathlib import Path

import joblib
import polars as pl

from settings_data import get_settings


def run_all_performance(dataset_dir: Path, output_dir: Path, n_jobs: int = -1):
    """
    Main entry point for performance test
    """
    jobs = []
    for setting in get_settings():
        # work only on these settings for the performance.
        if setting.name.startswith('G2.3') or setting.name.startswith('G4.2'):
            datasets = get_dataset_paths(dataset_dir, setting.name)
            for dataset in datasets:
                # argument of the nested function
                jobs.append((dataset, setting.name))

    performance_data = joblib.Parallel(n_jobs=n_jobs, verbose=1, backend='loky')(
        joblib.delayed(run_single_performance_benchmark)(
            dataset=dataset,
            setting_name=setting_name,
            output_dir=output_dir
        )
        for dataset, setting_name in jobs
    )
    # create and sort the dataframe.
    performance_df = pl.DataFrame(performance_data).sort(['setting_name', 'n_services', 'n_trust_attributes'])
    if output_dir:
        performance_df.write_csv(output_dir / 'performance.csv')


def run_single_performance_benchmark(dataset: Path, setting_name: str, output_dir: Path) -> dict:
    """
    Nested function to exploit parallelism
    """
    # the path of a dataset is: quality/snapshots/setting_name/services_X_attributes_Y/run_0/services.json
    # the -3 part gives the number of services and attributes which is what we need to name
    # the raw output file.
    # we also need to create the output directory, because under performance/
    # (already created by the caller) we don't have other sub-dirs:
    # we want to create performance/setting_name/services_X_attributes_Y.json
    # so: build the path
    output_sub_dir = output_dir / setting_name
    output_sub_dir.mkdir(parents=True, exist_ok=True)
    # and define the name of the output file.
    raw_output_file = output_sub_dir / f'{dataset.parts[-3]}.json'
    # run!
    try:
        subprocess.run(
            [
                'pytest',
                'benchmarks.py',
                '--benchmark-time-unit=s',
                '--dataset-dir',
                str(dataset),
                f'--benchmark-json={raw_output_file}',
            ],
            check=True,
            # need to really set the std streams otherwise the subprocesses fail.
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f'Performance benchmark failed for:\n'
            f'  setting: {setting_name}\n'
            f'  dataset: {dataset}\n'
            f'  return code: {e.returncode}\n\n'
            f'================ STDOUT ================\n'
            f'{e.stdout}\n'
            f'================ STDERR ================\n'
            f'{e.stderr}\n'
        ) from e

    # we have one result for each setting, |services|, |trust attributes|
    with open(raw_output_file) as f:
        data = json.load(f)
    # these are always the same, regardless the type of function we're benchmarking.
    obj = {
        'setting_name': data['benchmarks'][0]['extra_info']['setting_name'],
        'n_services': data['benchmarks'][0]['extra_info']['n_services'],
        'n_trust_attributes': data['benchmarks'][0]['extra_info']['n_trust_attributes'],
        'execution_id': data['benchmarks'][0]['extra_info']['execution_id'],
    }

    for benchmark in data['benchmarks']:
        if benchmark['group'] == 'negotiation':
            fill_key = 'negotiation'
        elif benchmark['group'] == 'dynamic_trust' and benchmark['name'] == 'test_dynamic_trust':
            fill_key = 'dynamic_trust'
        elif benchmark['group'] == 'dynamic_trust' and benchmark['name'] == 'test_dynamic_analysis':
            fill_key = 'dynamic_analysis'
        elif benchmark['group'] == 'dynamic_trust' and benchmark['name'] == 'test_dynamic_planning':
            fill_key = 'dynamic_planning'
        else:
            raise Exception(f'Unknown benchmark group: {benchmark["group"]}')
        obj[f'{fill_key}_avg'] = benchmark['stats']['mean']
        obj[f'{fill_key}_std'] = benchmark['stats']['stddev']
        obj[f'{fill_key}_median'] = benchmark['stats']['median']

    return obj


def get_dataset_paths(base_dir: Path, setting_name: str) -> list[Path]:
    """
    Return list of paths to datasets given this setting.

    Under each setting, we have different datasets varying the number of services
    and trust attributes, and then different versions one for each run. We pick
    *one* dataset for each combination of |services| and |trust attributes|.
    """
    paths = []
    # main_output_dir/snapshots/setting_name is the directory where we save stuff.
    # so here we determine the main starting point, depending on whether base_dir
    # already contains the snapshot or not.
    different_srv_base = base_dir / 'snapshots' / setting_name \
        if base_dir.parts[-1] != 'snapshots' \
        else base_dir / setting_name
    # now here, we have as children directories like services_10_attributes_100/run_1
    children = different_srv_base.iterdir()
    for child in children:
        if child.is_dir():
            # we use sorted to ensure deterministic extraction.
            # and we are getting here 'run_0', basically.
            execution = sorted(list(filter(lambda x: x.is_dir(), child.iterdir())))[0]
            # add the file name.
            paths.append(execution / 'services.json')
    return paths
