#!/bin/python3

import const
import sys
import numpy as np
import pandas as pd
from joblib import Parallel, delayed


def generateTrustData(probabilities: list[float]) -> (int, bool):
    """
        Function that generates a service data value (according to probabilities) 
    """

    return (
        np.random.default_rng().choice(
            [const.SD_VALUE['BAD'], const.SD_VALUE['AVG'], const.SD_VALUE['GOOD']],
            p = probabilities
        ),
        np.random.default_rng().choice(
            [True, False],
            p = [0.5, 0.5]
        )
    )


def generateRequirement(val_probabilities: list[float], card_probabilities: list[float]) -> tuple[list[int], int, bool]:
    """
        Function that generates a tuple containing: range of accepted value (according to val_probabilities), and cardinality (according to card_probabilities)  
    """

    return (
        [
            np.random.default_rng().choice(
                [const.SD_VALUE['BAD'], const.SD_VALUE['AVG'], const.SD_VALUE['GOOD']],
                p=val_probabilities
            ),
            const.SD_VALUE['GOOD']  # to represent an open range [x, +inf), the second value is the maximum
        ],
        np.random.default_rng().choice(
            [const.REQ_CARDINALITY['EXISTS'], const.REQ_CARDINALITY['FORALL']],
            p=card_probabilities
        ),
        np.random.default_rng().choice(
            [True, False],
            p=[0.5, 0.5]
        )
    )


def generatePolicy(probabilities: list[float]) -> list[float]:
    """
        Function that generate a list of float (according to probabilities) representing: 
         - list[0] the minimum satisfaction to join
         - list[1] the minimum satisfaction to perform the best action 
    """

    return np.random.default_rng().choice(
        [const.POLICIES['LOOSE'], const.POLICIES['STRICT']],
        p=probabilities
    ).tolist()

def generateNumberOfChangingServices(service_num: int, probabilities: list[float]) -> int:
    """
        Function to generate the number of changing service:
         - in a loop on each service, we decide if a service change or not with probabilities p
    """

    count = 0

    for i in range(service_num):
        if np.random.default_rng().choice([True, False], p = probabilities):
            count += 1

    return count

def generateChangingServices(service_num: int, change_num: int) -> list[int]:
    """ 
        Function that generate a list of n different random services on which to make changes  
    """

    return (np.arange(0, service_num)[np.random.choice(service_num, size=change_num, replace=False)]).tolist()

def generateNumberOfChangingSds(sds_num: int, probabilities: list[float]) -> int:
    """
        Function to generate the number of changing service:
         - in a loop on each sd, we decide if a sd change or not with probabilities p
    """

    count = 0

    for i in range(sds_num):
        if np.random.default_rng().choice([True, False], p = probabilities): 
            count += 1

    return count

def generateChangingSds(sds_num: int, change_num: int) -> list[int]:
    """ 
        Function that generate a list of n different random services on which to make changes  
    """

    return (np.arange(0, sds_num)[np.random.choice(sds_num, size=change_num, replace=False)]).tolist()

def generateChange(service: dict, changing_sds: list[int]) -> list[(str, int)]:
    changes = []

    for csd in changing_sds: 
        ch_type = np.random.default_rng().choice(
            [const.CHANGE['IMPROVING'], const.CHANGE['WORSENING']],
            p = [0.5, 0.5]
        )

        if ch_type == const.CHANGE['IMPROVING']:
            if service[f'sd{csd}'][0] < const.SD_VALUE['GOOD']:
                changes.append((f'sd{csd}', service[f'sd{csd}'][0] + 1))
        else:
            if service[f'sd{csd}'][0] > const.SD_VALUE['BAD']:
                changes.append((f'sd{csd}', service[f'sd{csd}'][0] - 1))

    return changes  # [('sd_n', newval), ....]

def generateService(index: int, sds_num: int, sd_probabilities: list[float], r_val_probabilities: list[float],
                 r_card_probabilities: list[float], r_pol_probabilities: list[float]) -> dict:
    service = {}

    service['name'] = f'service{index}'

    for sd_num in range(sds_num):
        service[f'sd{sd_num}'] = generateTrustData(sd_probabilities)
        service[f'req{sd_num}'] = generateRequirement(r_val_probabilities, r_card_probabilities)

    service['policy'] = generatePolicy(r_pol_probabilities)
    service['change'] = []

    return service

class DatasetGenerator:
    def __init__(self, setting: list[dict]):
        self.setting = setting

    def generate(self, services_num: int, sds_num: int, filename: str):
        # generate services
        services = Parallel(n_jobs=-1)(
            delayed(generateService)(i, sds_num, self.setting['SD_P'], self.setting['REQS_P']['REQUIREMENTS'],
                                  self.setting['REQS_P']['CARDINALITY'], self.setting['REQS_P']['POLICY']) for i in
            range(services_num))

        # generate indexes 
        indexes = np.arange(0, services_num, dtype=int).tolist()

        # create dataframe and export it 
        df = pd.DataFrame(services)
        df.index = indexes
        df.index.name = 'service'
        df.insert(0, 'setting', self.setting['SETTING_NAME'])

        df.to_csv(filename)
