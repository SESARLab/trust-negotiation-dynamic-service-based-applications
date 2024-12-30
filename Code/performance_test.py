#!/bin/python3

import pytest
import const
import os

from quality import exportQualityResult
from results_structure import checkFiles, cleanOldData
from performance import exportPerformanceResult, getExpSettings

const.SERVICES_NUM = [10]
const.SDS_NUM = [10]

@pytest.mark.parametrize("f", ['./.experiements_test'])
def test_exportPerformanceResult(f):
    """
        Check that the function creates the right number of files
    """

    fileCount = 0
    totalFile = 2

    checkFiles(f)

    exportQualityResult(True, f)
    exportPerformanceResult(f)

    for d in os.listdir(f'{f}/performance'):
        for d2 in os.listdir(f'{f}/performance/{d}'):
            fileCount += 1

    assert fileCount == totalFile

    cleanOldData(f)

    for d in os.listdir(f'{f}/quality'):
        for d2 in os.listdir(f'{f}/quality/{d}'):
            if os.path.isdir(f'{f}/quality/{d}/{d2}'):
                for d3 in os.listdir(f'{f}/quality/{d}/{d2}'):
                    os.rmdir(f'{f}/quality/{d}/{d2}/{d3}')
            os.rmdir(f'{f}/quality/{d}/{d2}')
        os.rmdir(f'{f}/quality/{d}')

    os.rmdir(f'{f}/quality')

    for d in os.listdir(f'{f}/performance'):
        os.rmdir(f'{f}/performance/{d}')

    os.rmdir(f'{f}/performance')
    
    for d in os.listdir(f'{f}/datasets'):
        os.rmdir(f'{f}/datasets/{d}')

    os.rmdir(f'{f}/datasets')

    os.rmdir(f)