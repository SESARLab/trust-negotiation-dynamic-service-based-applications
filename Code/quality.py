#!/bin/python3

from dataset_generator import DatasetGenerator, generateChangingServices, generateChange, \
    generateNumberOfChangingServices, generateChangingSds, generateNumberOfChangingSds
from negotiation import negotiation, dynamicTrust
from dataset_reader import getServicesFromDataset, countChanges
from joblib import delayed, Parallel
import const
import copy
import pandas as pd
import numpy as np


def exportExecVal(destDir: str, services_num: int, sds_num: int, setting: dict, exec_num: int, quality: bool) -> dict:
    execution_val = {
        # contains the value of each execution to perform the average
        'avg_succ_rate_our': [],
        'avg_succ_rate_soa': [],
        'application_stability_our': [],
        'service_stability_our': [],
        'relevant_change_our': [], 
        'avg_satisfaction': [],
    } 

    filename = f"{destDir}/datasets/execution{exec_num + 1}/dataset_{setting['SETTING_NAME']}_{services_num}_{sds_num}.csv"

    DatasetGenerator(setting).generate(services_num, sds_num, filename)  # generate dataset

    services = getServicesFromDataset(filename)  # read dataset

    system_our = negotiation(services)  # negotiation with our approach

    if quality:
        system_soa = negotiation(services, SoA=True)  # negotiation with state of art approximation

        our_s_len = len(system_our)
        services_len = len(services)

        execution_val['avg_succ_rate_our'].append(our_s_len / services_len)  # success rate of our
        execution_val['avg_succ_rate_soa'].append(len(system_soa) / services_len)  # success rate of state of art

        sats = []  # list of satisfaction degrees

        for n in system_our:
            sats.append(n[1]) 

        execution_val['avg_satisfaction'].append(np.mean(sats) if len(sats) > 0 else 0)  # retrieve satisfaction avg

        # generate changes on systems services
        changing_services = generateChangingServices(  # get the changing service
            len(system_our),
            generateNumberOfChangingServices(  # get the number of changing services
                len(system_our),
                setting['CH_P']['SERVICE']
            )
        )

        changes = Parallel(  # parallelize changes generation
            n_jobs=-1  # threads num = max available
        )(
            delayed(
                generateChange  # function to parallelize
            )(  # arguments
                system_our[cn][0],  # list of services
                generateChangingSds(  # get the changing sds
                    sds_num,
                    generateNumberOfChangingSds(  # get the number of changing sd
                        sds_num,
                        setting['CH_P']['DATA']
                    )
                )
            )
            for cn in changing_services  # for each service in changing services
        )

        tmp_df = pd.read_csv(filename)

        for i, cn in enumerate(changing_services):
            system_our[cn][0]['change'] = changes[i]

            if len(changes[i]) > 0:
                tmp_df.at[system_our[cn][0]['service'], 'change'] = changes[i]

        tmp_df.to_csv(filename, index=False)

        # different dynamic trust
        dynamic_trust_our = dynamicTrust(copy.deepcopy(system_our))
        system_after_changes_our = dynamic_trust_our[1]  # our approach

        # check how many services remain in the system with different approaches                  
        execution_val['application_stability_our'].append(
            (len(system_after_changes_our) / our_s_len) if our_s_len > 0 else 0)

        change_number = countChanges(system_our)  # number of changes

        if change_number == 0:
            execution_val['relevant_change_our'].append(0) 
        else:   
            # execution_val['relevant_change_our'].append(1 - (dynamic_trust_our[0] / change_number))
            execution_val['relevant_change_our'].append(dynamic_trust_our[0] / change_number)

        changeActionCount = 0

        execution_val['service_stability_our'].append(dynamic_trust_our[2])

    return execution_val


def exportQualityResult(quality: bool, destDir: str):
    """
        Function to run the negotiation and dynamic trust for each settings n times and export some results:
        (For each value we consider average and standard deviation) 
         - success rate == number of accepted service during the negotiation / number of total services
         - average satisfaction degree
         - number of services after changes 
         - number of application stability

        Each value is retrieved using our approach and some approximation of the state-of-the-art
        Export in different ways: 
         - raw: a file for each setting containing average of n executions
         - grouped: group the results on number of services and number of service data
         - elaborated: a single file containing an average of every setting 

        All in CSV format
    """

    negotiation_elaborated_results = []
    dynamic_elaborated_results = []
    elaborated_results_indexes = []

    for setting in const.getSettings():  # for each setting
        negotiation_row = []
        negotiation_indexes = []
        dynamic_row = []
        dynamic_indexes = []

        for services_num in const.SERVICES_NUM:  # for each service number
            for sds_num in const.SDS_NUM:  # for each service data number
                execution_val = {  # contains the value of each execution to perform the average
                    'avg_succ_rate_our': [],
                    'avg_succ_rate_soa': [],
                    'application_stability_our': [],
                    'relevant_change_our': [],
                    'avg_satisfaction': [],
                    'service_stability_our': [],
                }

                executionsVals = Parallel(n_jobs=-1)(
                    delayed(exportExecVal)(destDir, services_num, sds_num, setting, i, quality) for i in
                    range(const.EXECUTION))

                for vals in executionsVals:
                    for k in vals.keys():
                        execution_val[k] += vals[k]

                # store datas
                negotiation_row.append({
                    'SERVICES': services_num,
                    'SERVICE_DATA': sds_num,
                    'AVG_SUCC_RATE_OUR': np.mean(execution_val['avg_succ_rate_our']) if quality else 0,
                    'AVG_SUCC_RATE_SOA': np.mean(execution_val['avg_succ_rate_soa']) if quality else 0,
                    'AVG_SATISFACTION': np.mean(execution_val['avg_satisfaction']) if quality else 0,
                    'STD_SUCC_RATE_OUR': np.std(execution_val['avg_succ_rate_our']) if quality else 0,
                    'STD_SUCC_RATE_SOA': np.std(execution_val['avg_succ_rate_soa']) if quality else 0,
                    'STD_SATISFACTION': np.std(execution_val['avg_satisfaction']) if quality else 0
                })

                dynamic_row.append({
                    'SERVICES': services_num,
                    'SERVICE_DATA': sds_num,
                    'AVG_RELEVANT_CHANGES_OUR': np.mean(
                        execution_val['relevant_change_our']) if quality else 0,
                    'AVG_APPLICATION_STABILITY_OUR': np.mean(
                        execution_val['application_stability_our']) if quality else 0,
                    'AVG_SERVICE_STABILITY_OUR': np.mean(execution_val['service_stability_our']) if quality else 0,
                    'STD_RELEVANT_CHANGE_OUR': np.std(
                        execution_val['relevant_change_our']) if quality else 0,
                    'STD_APPLICATION_STABILITY_OUR': np.std(
                        execution_val['application_stability_our']) if quality else 0,
                    'STD_SERVICE_STABILITY_OUR': np.std(execution_val['service_stability_our']) if quality else 0,
                })

                negotiation_indexes.append(f'{services_num}_{sds_num}')
                dynamic_indexes.append(f'{services_num}_{sds_num}')

        # HANDSHAKE 
        # RAW RESULTS 
        negotiation_df = pd.DataFrame(negotiation_row)
        negotiation_df.index = negotiation_indexes

        negotiation_df.to_csv(f"{destDir}/quality/raw_results/negotiation/raw_results_{setting['SETTING_NAME']}.csv")

        # GROUPED RESULTS 
        tmp_ind = []
        tmp = negotiation_df.groupby('SERVICES').mean()

        for ind in tmp.index:
            tmp_ind.append(f'{ind}_*')

        tmp.index = tmp_ind

        tmp2 = negotiation_df.groupby('SERVICE_DATA').mean()

        tmp_ind = []

        for ind in tmp2.index:
            tmp_ind.append(f'*_{ind}')

        tmp2.index = tmp_ind

        tmp = pd.concat([tmp, tmp2]).drop(columns=['SERVICE_DATA', 'SERVICES'])
        tmp.index.name = 'SERVICES_SDS'
        tmp.to_csv(f"{destDir}/quality/group_results/negotiation/group_results_{setting['SETTING_NAME']}.csv")

        # ELABORATED RESULTS

        negotiation_elaborated_results.append(negotiation_df.mean())
        elaborated_results_indexes.append(setting['SETTING_NAME'])

        # DYNAMIC TRUST 
        # RAW RESULTS
        change_df = pd.DataFrame(dynamic_row)
        change_df.index = dynamic_indexes

        change_df.to_csv(f"{destDir}/quality/raw_results/dynamic_trust/raw_results_{setting['SETTING_NAME']}.csv")

        # GROUPED RESULTS
        tmp_ind = []
        tmp = change_df.groupby('SERVICES').mean()

        for ind in tmp.index:
            tmp_ind.append(f'{ind}_*')

        tmp.index = tmp_ind

        tmp2 = change_df.groupby('SERVICE_DATA').mean()

        tmp_ind = []

        for ind in tmp2.index:
            tmp_ind.append(f'*_{ind}')

        tmp2.index = tmp_ind

        tmp = pd.concat([tmp, tmp2]).drop(columns=['SERVICE_DATA', 'SERVICES'])
        tmp.index.name = 'SERVICES_SDS'
        tmp.to_csv(f"{destDir}/quality/group_results/dynamic_trust/group_results_{setting['SETTING_NAME']}.csv")

        # ELABORATED RESULTS
        dynamic_elaborated_results.append(change_df.mean())

    negotiation_elaborated_df = pd.DataFrame(negotiation_elaborated_results)
    negotiation_elaborated_df.index = elaborated_results_indexes

    change_elaborated_df = pd.DataFrame(dynamic_elaborated_results)
    change_elaborated_df.index = elaborated_results_indexes

    negotiation_elaborated_df.to_csv(f'{destDir}/quality/elaborated_results/negotiation_results.csv')
    change_elaborated_df.to_csv(f'{destDir}/quality/elaborated_results/dynamic_trust_results.csv')
