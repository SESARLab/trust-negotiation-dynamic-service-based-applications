#!/bin/python3

import pytest
import const
import os
from quality import exportQualityResult
from results_structure import cleanOldData, checkFiles

@pytest.mark.parametrize("f", ['./.experiements_test'])
def test_exportQualityResult(f):
    """
        Check that the function creates the right number of files
    """

    fileCount = 0
    totalFile = (const.EXECUTION * len(const.getSettings()) * len(const.SERVICES_NUM) * len(const.SDS_NUM)) + 2 + (4 * len(const.getSettings()))

    checkFiles(f)
    
    exportQualityResult(True, f)

    for d in os.listdir(f'{f}/datasets'):
        for d2 in os.listdir(f'{f}/datasets/{d}'):
            fileCount += 1

    for d in os.listdir(f'{f}/quality'):
        for d2 in os.listdir(f'{f}/quality/{d}'):
            if os.path.isdir(f'{f}/quality/{d}/{d2}'):
                for d3 in os.listdir(f'{f}/quality/{d}/{d2}'):
                    fileCount += 1
            else:
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

