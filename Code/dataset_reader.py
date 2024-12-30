#!/bin/python3

import pandas as pd
import json

def getServicesFromDataset(filename: str) -> list[dict]:
    """
        Function that read services from a csv file and return a list of dict (i.e., a list of services) containing all the services' information 
        List and tuples are saved in csv as string, so to convert it we need to parse the string and convert into object 
    """

    df = pd.read_csv(filename) 
    services = df.to_dict('records')  

    for n in services: # replace string with list or tuple
        n['policy'] = json.loads(n['policy'])

        n['change'].replace('[', '').replace(']', '')

        n['change'] = list(eval(n['change']))

        for k in list(n.keys()): 
            if 'req' in k:
                n[k] = (
                    json.loads(f"{n[k].replace('(', '').split(']')[0]}]"), # return the range of accepted value
                    int(n[k].replace(')', '').split(',')[2]), # return the cardinality
                    eval(n[k].replace(')', '').split(',')[3]) # return the certificate requirement
                )
            if 'sd' in k: 
                n[k] = (
                    int(n[k].split(',')[0].replace('(', '')), 
                    eval(n[k].split(',')[1].replace(')', ''))
                )


    return services

def getSdsFromService(service: dict) -> list[tuple[int, bool]]:
    """
        Function that return a list containing all the service data of a service
    """

    sds = []

    for k in list(service.keys()):
        if k is not None and 'sd' in k:
            sds.append(service[k])

    return sds

def getReqsFromService(service: dict) -> list[tuple[list[int], int, bool]]:
    """
        Function that return a list containing all the service data request of a service
    """

    reqs = []

    for k in list(service.keys()):
        if 'req' in k:
            reqs.append(service[k])

    return reqs

def countChanges(services: list[list[dict, float]]) -> int:
    """ 
        Function to count the effective change number
    """

    count = 0
    
    for n in services: 
        if len(n[0]['change']) > 0:
            count += 1 

    return count