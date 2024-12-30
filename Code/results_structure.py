#!/bin/python3

import os
import const


def checkFiles(destDir: str) -> bool:
    """
        Function to check if old test data already exists and create directories to store them 
    """

    if os.path.isdir(destDir) and len(os.listdir(destDir)) != 0 and os.path.isdir(f'{destDir}/quality'):
        choice = input('Experiments directories already exists. All files will be removed, continue? (y/n): ')

        if choice != 'y':
            print("Exit.")
            return False
        else:
            cleanOldData(f'{destDir}')
    else:
        if not os.path.isdir(destDir):
            os.mkdir(destDir)

        if not os.path.isdir(f'{destDir}/quality'):
            os.mkdir(f'{destDir}/quality')

        os.mkdir(f'{destDir}/datasets')
        os.mkdir(f'{destDir}/quality/raw_results')
        os.mkdir(f'{destDir}/quality/group_results')
        os.mkdir(f'{destDir}/quality/elaborated_results')
        os.mkdir(f'{destDir}/quality/raw_results/negotiation')
        os.mkdir(f'{destDir}/quality/raw_results/dynamic_trust')
        os.mkdir(f'{destDir}/quality/group_results/negotiation')
        os.mkdir(f'{destDir}/quality/group_results/dynamic_trust')

        for i in range(const.EXECUTION):
            os.mkdir(f'{destDir}/datasets/execution{i + 1}')

    if os.path.isdir(destDir) and not os.path.isdir(f'{destDir}/performance'):
        os.mkdir(f'{destDir}/performance')
        os.mkdir(f'{destDir}/performance/negotiation')
        os.mkdir(f'{destDir}/performance/dynamic_trust')

    return True


def cleanOldData(destDir: str):
    """
        Function to clean old data
        Useful while testing 
    """

    for f in os.listdir(destDir):
        if os.path.isdir(f'{destDir}/{f}'):
            cleanOldData(f'{destDir}/{f}')
        else:
            os.remove(f'{destDir}/{f}')
