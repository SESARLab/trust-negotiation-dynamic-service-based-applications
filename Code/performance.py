#!/bin/python3

import subprocess
import const
import json
import os
import pandas as pd


def getExpSettings(settings: list[dict]) -> list[str]:
    """
        Function to get all the settings on which perform benchmark
    """

    sett = []

    for n in const.SERVICES_NUM:
        for t in const.SDS_NUM:
            for s in const.getSettings():
                # get sd bad and strict reqs or tp good and loose reqs
                if ((s['SD_P'][0] == 0.5 and s['REQS_P']['REQUIREMENTS'][1] == 2 / 3) or (
                        s['SD_P'][2] == 0.5 and s['REQS_P']['REQUIREMENTS'][0] == 2 / 3)):
                    sett.append(f"{s['SETTING_NAME']}_{n}_{t}")

    return sett


def exportPerformanceResult(destDir):
    """
        Function to launch benchmark and export results 
    """

    negotiation_dataframes = []
    dynamic_service_dataframes = []
    indexes = []

    for setting in getExpSettings(const.getSettings()):
        subprocess.run(['pytest', 'benchmarks.py', '--benchmark-time-unit=s',
                        '--path', destDir, '--setting', setting,
                        f'--benchmark-json={destDir}/.tmp.json'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        f = open(f'{destDir}/.tmp.json')
        tmpData = json.load(f)

        negotiation_data = {
            'SERVICES': setting.split('_')[1],
            'SERVICE_DATA': setting.split('_')[2],
            'MIN': tmpData['benchmarks'][0]['stats']['min'],
            'MAX': tmpData['benchmarks'][0]['stats']['max'],
            'AVG': tmpData['benchmarks'][0]['stats']['mean'],
            'STD': tmpData['benchmarks'][0]['stats']['stddev']
        }

        dynamicTrust_data = {
            'SERVICES': setting.split('_')[1],
            'SERVICE_DATA': setting.split('_')[2],
            'MIN_ALL': tmpData['benchmarks'][1]['stats']['min'],
            'MIN_ANALYSIS': tmpData['benchmarks'][2]['stats']['min'],
            'MIN_PLANNING': tmpData['benchmarks'][3]['stats']['min'],
            'MIN_EXECUTION': tmpData['benchmarks'][4]['stats']['min'],
            'MAX_ALL': tmpData['benchmarks'][1]['stats']['max'],
            'MAX_ANALYSIS': tmpData['benchmarks'][2]['stats']['max'],
            'MAX_PLANNING': tmpData['benchmarks'][3]['stats']['max'],
            'MAX_EXECUTION': tmpData['benchmarks'][4]['stats']['max'],
            'AVG_ALL': tmpData['benchmarks'][1]['stats']['mean'],
            'AVG_ANALYSIS': tmpData['benchmarks'][2]['stats']['mean'],
            'AVG_PLANNING': tmpData['benchmarks'][3]['stats']['mean'],
            'AVG_EXECUTION': tmpData['benchmarks'][4]['stats']['mean'],
            'STD_ALL': tmpData['benchmarks'][1]['stats']['stddev'],
            'STD_ANALYSIS': tmpData['benchmarks'][2]['stats']['stddev'],
            'STD_PLANNING': tmpData['benchmarks'][3]['stats']['stddev'],
            'STD_EXECUTION': tmpData['benchmarks'][4]['stats']['stddev']
        }

        indexes.append(setting.split('_')[0])

        negotiation_dataframes.append(negotiation_data)
        dynamic_service_dataframes.append(dynamicTrust_data)

        f.close()

    h_df = pd.DataFrame(negotiation_dataframes)
    cm_df = pd.DataFrame(dynamic_service_dataframes)

    h_df.index = indexes
    cm_df.index = indexes

    h_df.to_csv(f"{destDir}/performance/negotiation/results.csv")
    cm_df.to_csv(f"{destDir}/performance/dynamic_trust/results.csv")

    os.remove(f'{destDir}/.tmp.json')
