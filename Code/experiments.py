#!/bin/python3

import argparse
import const
from results_structure import checkFiles
from quality import exportQualityResult
from performance import exportPerformanceResult

experiments = {
    'quality': True,
    'performance': True
}

parser = argparse.ArgumentParser()

parser.add_argument('-o', '--output-dir', type=str, required=True)
parser.add_argument('-n', '--services', nargs=1, help='set the number of services for the experiments')
parser.add_argument('-d', '--servicedata', nargs=1, help='set the number of service data for the experiments')
parser.add_argument('-s', '--skip', nargs='*', help='skip experiments',
                    choices=['quality', 'performance'], )

args = parser.parse_args()

destDir = args.output_dir

if args.services is not None:
    if ',' in args.services[0]:
        const.SERVICES_NUM = []

        for s in args.services[0].split(','):
            const.SERVICES_NUM.append(int(s))
    else:
        const.SERVICES_NUM = [int(args.services[0])]

if args.servicedata is not None:
    if ',' in args.servicedata[0]:
        const.SDS_NUM = []

        for s in args.servicedata[0].split(','):
            const.SDS_NUM.append(int(s))
    else:
        const.SDS_NUM = [int(args.servicedata[0])]

if args.skip is not None:
    for e in args.skip:
        if e in experiments.keys():
            experiments[e] = False

if checkFiles(destDir):
    choice = input(
        f'Will be generated: {len(const.getSettings()) * len(const.SERVICES_NUM) * len(const.SDS_NUM) * const.EXECUTION} datasets, continue? (y/n): ')

    if choice != 'y':
        print('Exit.')
        quit(1)

    print('Running quality experiments... ', end='')

    exportQualityResult(experiments['quality'], destDir)

    print('ok.\nRunning performance experiments... ', end='')

    if experiments['performance']:
        exportPerformanceResult(destDir)

    print('ok.')
else:
    quit(1)
