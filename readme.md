# Trust Negotiation in Dynamic Service-Based Applications

[![CC BY 4.0][cc-by-shield]][cc-by]

[**Nicola Bena**](https://homes.di.unimi.it/bena), [**Genoveva Vargas-Solar**](http://vargas-solar.com/), [**Nadia Bennani**](https://liris.cnrs.fr/en/member-page/nadia-bennani), [**Nicolò Grecchi**](https://www.linkedin.com/in/nicol%C3%B2-grecchi-6b094123b/) [**Chirine Ghedira-Guegan**](https://liris.cnrs.fr/en/member-page/chirine-ghedira-guega), [**Claudio A. Ardagna**](https://homes.di.unimi.it/ardagna)

> In the last two decades, the long-standing promise of service-based software has been realized, transitioning from traditional client-server architecture to distributed, service-based systems. Applications built upon these systems dynamically compose services from multiple, often unknown, parties to exchange vast amounts of data and collaboratively define and optimize new business processes (e.g., federated learning in the medical field). As these applications become increasingly complex and new regulations emerge, participating services must understand each other's functional and non-functional behavior before joining the application, ensuring that their requirements are met. This scenario is reviving the trust issue that emerged with the advent of the commercial Internet in the 90s. Contrary to the past, trust must now empower collaborative, dynamic, open distributed applications rather than static, client-server transactions. This paper proposes a Trust Management System (TMS) that addresses the specific needs of distributed service-based applications. It implements a trust negotiation protocol that supports partial negotiation to maximize negotiation success and ensures trust establishment over time and across service changes. The proposed approach is applied in the context of a Federated Learning (FL) composite application that studies the long-term effects of COVID-19 and is experimentally evaluated in a comprehensive simulated environment.

## Overview

This repository contains:

- the code used to run the simulations in the experiments (directory [`Code`](Code)), described [here](#code)
- the result shown in the paper (directory [`Data`](Data)), described [here](#data). They are in the format `csv` for the highest compatibility
- the instruction to exactly replicate the results shown in the paper (this file), described [here](#reproducibility)
- the instruction to exactly replicate the described shown in the paper (this file), described [here](#walkthrough).

## Code

The code is written in Python and consists of few files. Technical details on data structures and their representation are described in the file [`Code/readme.md`](Code/readme.md).

The purpose of the files is the following.

- [`Code/benchmarks.py`](Code/benchmarks.py): execute performance experiments
- [`Code/conftest.py`](Code/conftest.py): wrapper for the performance experiments
- [`Code/const.py`](Code/const.py): experimental settings and other constants
- [`Code/dataset_generator.py`](Code/dataset_generator.py): generate experimental data
- [`Code/dataset_generator_test.py`](Code/dataset_generator_test.py): test [`Code/dataset_generator.py`](Code/dataset_generator.py)
- [`Code/dataset_reader.py`](Code/dataset_reader.py): read an exported dataset from file
- [`Code/dataset_reader_test.py`](Code/dataset_reader_test.py): test [`Code/dataset_reader.py`](Code/dataset_reader.py)
- [`Code/environment.yml`](Code/environment.yml): configuration of the *`conda` environment*
- [`Code/experiments.py`](Code/experiments.py): entrypoint of the experiments
- [`Code/negotiation.py`](Code/negotiation.py): implement negotiation and dynamic trust management
- [`Code/negotiation_test.py`](Code/negotiation_test.py) test [`Code/negotiation.py`](Code/negotiation.py)
- [`Code/negotiation_debug.py`](Code/negotiation_debug.py) mirrors [`Code/negotiation.py`](Code/negotiation.py) with additional output to be used in [`Code/walkthrough.py`](Code/walkthrough.py)
- [`Code/performance.py`](Code/performance.py): utility code used in (parsing) performance experiments
- [`Code/quality.py`](Code/quality.py): low-level code executing quality experiments
- [`Code/quality_test.py`](Code/quality_test.py): test [`Code/quality.py`](Code/quality.py)
- [`Code/readme.md`](Code/readme.md): provide technical details on internal structure
- [`Code/results_structure.py`](Code/results_structure.py): export experimental results
- [`Code/utils.py`](Code/utils.py): generic utilities
- [`Code/walkthrough.py`](Code/walkthrough.py): walkthrough for Section 5, based on [`Code/walkthrough_base.py`](Code/walkthrough_base.py)
- [`Code/walkthrough_base.py`](Code/walkthrough_base.py): common walkthrough code
- [`Code/walkthrough_simple.py`](Code/walkthrough_simple.py) simple walkthrough used in the examples, based on [`Code/walkthrough_base.py`](Code/walkthrough_base.py)

## Data

The directory [`Data`](Data) contains the results of the experiments discussed in the paper.

### A Note on the Terminology

The terminology used in the code/results slightly differ from that used in the paper. The main difference is that **trust attributes** are referred to as *service data* in the code/data.

### At a Glance

Data are structured as follows. To learn more on how to reproduce them, see [Reproducibility](#reproducibility).

- datasets used to simulate the composite application (directory [`Data/datasets`](Data/datasets)). We create one sub-directory for each execution. In our case we chose 5 executions, hence we have [`Data/datasets/execution1`](Data/datasets/execution1)--[`Data/datasets/execution5`](Data/datasets/execution5). Each file in each execution directory contain the entire set of services, with their data, requirements, policies, supposed changes, and so on. They are named following this pattern: `dataset_SettingName_NumberOfServices_NumberOfServiceData_PercOfServicesThatChanges_PercOfSerServiceDataThatChange.csv` and described in details [here](Code/readme.md#datasets)
- results of the performance evaluation (directory [`Data/performance`](Data/performance))
  - related to the trust negotiation protocol ([`Data/performance/negotiation/results.csv`](Data/performance/negotiation/results.csv))
  - related to the dynamic trust negotiation protocol ([`Data/performance/dynamic_trust/results.csv`](Data/performance/dynamic_trust/results.csv))
- results of the quality evaluation (directory [`Data/quality`](Data/quality))
  - results with the highest aggregation level (one row for each setting, aggregated varying the number of services and service data) (directory [`Data/quality/elaborated_results`](Data/quality/elaborated_results))
    - trust negotiation protocol [`Data/quality/elaborated_results/negotiation_results.csv`](Data/quality/elaborated_results/negotiation_results.csv)
    - dynamic trust negotiation protocol [`Data/quality/elaborated_results/dynamic_trust_results.csv`](Data/quality/elaborated_results/dynamic_trust_results.csv)
  - results aggregated at a medium aggregation level (one table for each setting, one row for each number of services, service data) (directory [`Data/quality/group_results`](Data/quality/group_results))
    - trust negotiation protocol (directory [`Data/quality/group_results/negotiation`](Data/quality/group_results/negotiation))
    - dynamic trust negotiation protocol (directory [`Data/quality/group_results/dynamic_trust`](Data/quality/group_results/dynamic_trust))
  - results without any aggregations but over the different executions (one table for each setting, one row for each combination of services and service data) (directory [`Data/quality/raw_results`](Data/quality/raw_results))
    - trust negotiation protocol (directory [`Data/quality/raw_results/negotiation`](Data/quality/raw_results/negotiation))
    - dynamic trust negotiation protocol (directory [`Data/quality/raw_results/dynamic_trust`](Data/quality/raw_results/dynamic_trust))
- results for figures/tables shown in the paper: directory [`Data/post`](Data/post)
  - Figure 2: [`Data/post/performance_negotiation_service_first.csv`](Data/post/performance_negotiation_service_first.csv) and [`Data/post/performance_negotiation_servicedata_first.csv`](Data/post/performance_negotiation_servicedata_first.csv)
  - Figure 3: [`Data/post/quality_negotiation_G2.3.X__service_first.csv`](Data/post/quality_negotiation_G2.3.X__service_first.csv) and [`Data/post/quality_negotiation_G2.3.X__servicedata_first.csv`](Data/post/quality_negotiation_G2.3.X__servicedata_first.csv)
  - Figure 4: [`Data/post/performance_dynamic_service_first.csv`](Data/post/performance_dynamic_service_first.csv) and [`Data/post/performance_dynamic_servicedata_first.csv`](Data/post/performance_dynamic_servicedata_first.csv)
  - Figure 5: [`Data/post/quality_dynamic_GX.X.3__service_first.csv`](Data/post/quality_dynamic_GX.X.3__service_first.csv) and [`Data/post/quality_dynamic_GX.X.3__servicedata_first.csv`](Data/post/quality_dynamic_GX.X.3__servicedata_first.csv)

### Details

Despite the different aggregations, the content of the files is roughly the same. Exceptions apply for files under directory [`Data/post`](Data/post), because they are designed to be easily plotted/shown in tables.

Results are generated in the following structure:

```txt
myDir
├─ datasets
│  ├─ execution1
│  ├─ execution2
│  ...    
│  └─ executionN
├─ performance
│  ├─ change_management 
│  └─ handshake
└─ quality
    ├─ elaborated results
    ├─ group_results
    │  ├─ change_management
    │  └─ handshake
    └─ raw_results
    ├─ change_management
    └─ handshake
```

#### Quality: Trust Negotiation Protocol

The following columns are contained in the results.

- Index: the setting name
- `SERVICES`: number of services in the experiment
- `SERVICE_DATA`: number of service data of each service
- `SUCC_RATE`: ratio of services that enter the application according to our approach (`SUCC_RATE_OUR`) and the state of the art (`SUCC_RATE_SOA`)
- `SATISFACTION`: average satisfaction degree of all services (this value is the same according to our approach and the state of the art).

For each of the above metrics except `SERVICES` and `SERVICE_DATA`, we report both the average (denoted by the prefix `AVG`) and the standard deviation (denoted by the prefix `STD`). Indexes represent the name of the used setting.

**Note**: values in top-aggregated files (i.e., [`Data/quality/elaborated_results`](Data/quality/elaborated_results)) have the same values for `SERVICES` and `SERVICE_DATA`. This is not an error. The reason is that the number of services and service data is averaged as well.

#### Quality: Dynamic Trust Negotiation Protocol

The following columns are contained in the results.

- Index: the setting name
- `SERVICES`: number of services in the experiment
- `SERVICE_DATA`: number of service data of each service
- `RELEVANT_CHANGES_OUR`: ratio of changes that are relevant according to Step Analysis in the paper
- `APPLICATION_STABILITY_OUR`: ratio of services part of the application after executing the dynamic trust negotiation protocol
- `SERVICE_STABILITY_OUR`: ratio of services whose action changes after executing the dynamic trust negotiation protocol

For each of the above metrics except `SERVICES` and `SERVICE_DATA`, we report both the average (denoted by the prefix `AVG`) and the standard deviation (denoted by the prefix `STD`).

**Note**: values in top-aggregated files (i.e., [`Data/quality/elaborated_results`](Data/quality/elaborated_results)) have the same values for `SERVICES` and `SERVICE_DATA`. This is not an error. The reason is that the number of services and service data is averaged as well.

#### Performance

The following columns are contained in the results.

- Index: the setting name
- `SERVICES`: number of services in the experiment
- `SERVICE_DATA`: number of service data of each service
- `MIN`: minimum execution time retrieved by [`pytest-benchmark`](https://pytest-benchmark.readthedocs.io/en/latest/)
- `MAX`: maximum execution time retrieved by [`pytest-benchmark`](https://pytest-benchmark.readthedocs.io/en/latest/)
- `AVG`: average execution time retrieved by [`pytest-benchmark`](https://pytest-benchmark.readthedocs.io/en/latest/)
- `STD`: standard deviation of the execution time retrieved by [`pytest-benchmark`](https://pytest-benchmark.readthedocs.io/en/latest/)

**Note**: the figures in the paper consider `AVG`.

## Reproducibility

Follow the steps below to replicate the results shown in the paper.

1. Prepare the environment installing all the dependencies
2. Run the simulation
3. Compute some aggregations (as in the paper).

**Note**: the file [`execute.sh`](execute.sh) is a convenience, all-in-one script executing steps 2-3 (please read step 3 prerequisites).

### 1) Environment Preparation

The first to do is to prepare the environment.

1. Install `conda` (e.g., [https://github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge))
2. create a directory where you put all the Python files in the directory [`Code`](Code), and `cd` into it
3. create the *conda environment* with all the necessary dependencies:

```bash
conda env create --file=environment.yaml
```

It may take some time.

**Note**: this step shall be executed only once.

### 2) Experiments Execution

First, activate the *conda environment* in the same directory as before:

```bash
conda activate TrustNegotiation
```

Make sure that this command succeeds. The prompt should change.

The settings (e.g., number of services, number of trust attributes, policies, percentages) can be modified by editing the file [`Code/const.py`](Code/const.py). The file follows the same settings used in the paper for full reproducibility.

Next, execute the experiments. The entire simulation is executed in just one command. It is only necessary to specify the directory where results will be put. In the example below, we use `Out`.

```bash
python experiments.py --output-dir Out
```

On a Mac M1 Pro, experiments take slightly less than 1 hour.

### 3) Data Aggregation

The data shown in the paper are computed after some additional aggregations over the data retrieved at the previous step.

As preparatory step, make sure to position in the directory where the code is and activate the environment.

First, create a directory to put these aggregated results. For instance, `Out/post`.

Second, we need to give a value to `BASE_OUTPUT_DIRECTORY`. It is a variable holding the  *main* output directory. For instance, in a Bash shell, we do the following.

```bash
# variable holding the *main* output directory
BASE_OUTPUT_DIRECTORY=Out
```

**Note**: this variable has only been defined to shorten the commands we describe below.

First, we perform a first aggregation for the quality of the trust negotiation protocol, focusing on the worst case setting `G2.3.X` (Figure 3 in the paper).

```bash
python utils.py \
    compress-quality \
    --base-output-directory $BASE_OUTPUT_DIR/post \
    --input-files $BASE_OUTPUT_DIR/quality/raw_results/negotiation/raw_results_G2.3.1.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/negotiation/raw_results_G2.3.2.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/negotiation/raw_results_G2.3.3.csv \
    --prefix quality_negotiation_G2.3.X_ \
    --drop-std true
```

Then, we retrieve aggregated data for the dynamic trust negotiation protocol, focusing on the worst case setting `GX.X.3` (Figure 5 in the paper).

```bash
python utils.py \
    compress-quality \
    --base-output-directory $BASE_OUTPUT_DIR/post \
    --input-files \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G1.1.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G1.2.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G1.3.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G2.1.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G2.2.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G2.3.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G3.1.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G3.2.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G3.3.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G4.1.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G4.2.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G4.3.3.csv \
    --prefix quality_dynamic_GX.X.3_ \
    --drop-std true
```

Then, we retrieve aggregated data for the performance evaluation.

First, regarding the trust negotiation protocol (Figure 2 in the paper).

```bash
python utils.py compress-performance \
    --mode negotiation \
    --base-output-directory $BASE_OUTPUT_DIR/post \
    --input-file $BASE_OUTPUT_DIR/performance/negotiation/results.csv

```

Next, regarding the dynamic trust negotiation protocol (Figure 4 in the paper).

```bash
python utils.py compress-performance \
    --mode dynamic \
    --base-output-directory $BASE_OUTPUT_DIR/post \
    --input-file $BASE_OUTPUT_DIR/performance/dynamic_trust/results.csv
```

Finally, we perform two aggregations to retrieve the exact data shown in Tables 8 and 9.

First, regarding the trust negotiation protocol (Table 9 in the paper).

```bash
python utils.py \
    compress-average \
    --input-file $BASE_OUTPUT_DIR/quality/elaborated_results/negotiation_results.csv \
    --output-file $BASE_OUTPUT_DIR/post/negotiation_results.csv \
    --mode negotiation \
    --drop-std true
```

Next, regarding the dynamic trust negotiation protocol (Table 9 in the paper).

```bash
python utils.py \
    compress-average \
    --input-file $BASE_OUTPUT_DIR/quality/elaborated_results/dynamic_trust_results.csv \
    --output-file $BASE_OUTPUT_DIR/post/dynamic_trust_results.csv \
    --mode dynamic \
    --drop-std true
```

The correspondence between the aggregated results created following the above commands and the figures in the paper is summarized in the following table.

| **Figure/Table** | **Files** |
| :--: | -- |
| Figure 3 | [`Data/post/performance_negotiation_service_first.csv`](Data/post/performance_negotiation_service_first.csv) and [`Data/post/performance_negotiation_servicedata_first.csv`](Data/post/performance_negotiation_servicedata_first.csv) |
| Figure 4 | [`Data/post/quality_negotiation_G2.3.X__service_first.csv`](Data/post/quality_negotiation_G2.3.X__service_first.csv) and [`Data/post/quality_negotiation_G2.3.X__servicedata_first.csv`](Data/post/quality_negotiation_G2.3.X__servicedata_first.csv) |
| Figure 5 | [`Data/post/performance_dynamic_service_first.csv`](Data/post/performance_dynamic_service_first.csv) and [`Data/post/performance_dynamic_servicedata_first.csv`](Data/post/performance_dynamic_servicedata_first.csv) |
| Figure 6 | [`Data/post/quality_dynamic_GX.X.3__service_first.csv`](Data/post/quality_dynamic_GX.X.3__service_first.csv) and [`Data/post/quality_dynamic_GX.X.3__servicedata_first.csv`](Data/post/quality_dynamic_GX.X.3__servicedata_first.csv) |

## Walkthrough

The code can simulate the walkthrough as discussed in the paper. The file [`Code/walkthrough.py`](Code/walkthrough.py) contains the definitions of services and the changes that occur, and execute the (dynamic) trust negotiation protocol, showing the results as JSON.

First, it is necessary to follow the same preparatory steps indicated [here](#1-environment-preparation).

Then, just execute the file [`Code/walkthrough.py`](Code/walkthrough.py).

```bash
python walkthrough.py
```

The output, corresponding to Section 5, is the following.

```json
{
    "in system": [
        {
            "name": "s_brazil",
            "satisfaction": 0.6666666666666666
        },
        {
            "name": "s_chile",
            "satisfaction": 0.6666666666666666
        },
        {
            "name": "s_france",
            "satisfaction": 0.6666666666666666
        },
        {
            "name": "s_mexico",
            "satisfaction": 0.6666666666666666
        },
        {
            "name": "s_poland",
            "satisfaction": 0.6666666666666666
        },
        {
            "name": "s_romania",
            "satisfaction": 1.0
        }
    ],
    "not in system": [
        {
            "name": "s_italy",
            "satisfaction": 0.3333333333333333
        }
    ],
    "number of services in system": 6,
    "number of services not in system": 1,
    "changes": [
        {
            "index": 0,
            "change": {
                "changed service": "s_chile",
                "changed service data": [
                    {
                        "sd2": "EEU"
                    }
                ],
                "reason_analysis": {
                    "affected_services": [
                        "s_mexico"
                    ]
                },
                "reason_planning": {
                    "decision": "KEEP",
                    "evict_service_to_remove": [],
                    "evict_service_to_update": [
                        "s_mexico"
                    ],
                    "keep_service_to_remove": [],
                    "keep_service_to_update": [
                        "s_mexico"
                    ]
                },
                "in system after change": [
                    {
                        "name": "s_brazil",
                        "satisfaction": 0.6666666666666666
                    },
                    {
                        "name": "s_chile",
                        "satisfaction": 0.6666666666666666
                    },
                    {
                        "name": "s_france",
                        "satisfaction": 0.6666666666666666
                    },
                    {
                        "name": "s_mexico",
                        "satisfaction": 0.3333333333333333
                    },
                    {
                        "name": "s_poland",
                        "satisfaction": 0.6666666666666666
                    },
                    {
                        "name": "s_romania",
                        "satisfaction": 1.0
                    }
                ]
            }
        },
        {
            "index": 1,
            "change": {
                "changed service": "s_romania",
                "changed service data": [
                    {
                        "sd1": 15
                    }
                ],
                "reason_analysis": {
                    "affected_services": [
                        "s_brazil",
                        "s_mexico"
                    ]
                },
                "reason_planning": {
                    "decision": "EVICT",
                    "evict_service_to_remove": [],
                    "evict_service_to_update": [],
                    "keep_service_to_remove": [
                        "s_brazil",
                        "s_mexico"
                    ],
                    "keep_service_to_update": []
                },
                "in system after change": [
                    {
                        "name": "s_brazil",
                        "satisfaction": 0.6666666666666666
                    },
                    {
                        "name": "s_chile",
                        "satisfaction": 0.6666666666666666
                    },
                    {
                        "name": "s_france",
                        "satisfaction": 0.6666666666666666
                    },
                    {
                        "name": "s_mexico",
                        "satisfaction": 0.3333333333333333
                    },
                    {
                        "name": "s_poland",
                        "satisfaction": 0.6666666666666666
                    }
                ]
            }
        },
        {
            "index": 2,
            "change": {
                "changed service": "s_poland",
                "changed service data": [
                    {
                        "sd0": "urban"
                    }
                ],
                "reason_analysis": {
                    "affected_services": [
                        "s_france"
                    ]
                },
                "reason_planning": {
                    "decision": "KEEP",
                    "evict_service_to_remove": [
                        "s_france"
                    ],
                    "evict_service_to_update": [],
                    "keep_service_to_remove": [
                        "s_france"
                    ],
                    "keep_service_to_update": []
                },
                "in system after change": [
                    {
                        "name": "s_brazil",
                        "satisfaction": 0.6666666666666666
                    },
                    {
                        "name": "s_chile",
                        "satisfaction": 0.6666666666666666
                    },
                    {
                        "name": "s_mexico",
                        "satisfaction": 0.3333333333333333
                    },
                    {
                        "name": "s_poland",
                        "satisfaction": 0.6666666666666666
                    }
                ]
            }
        }
    ]
}
```

Services and changes can be modified to simulate different walkthroughs.

File [`Code/walkthrough_simple.py`](Code/walkthrough_simple.py) describes a simpler scenario used in the first sections of the paper.

## Citation

Coming soon.

## Acknowledgements

This work was supported by:

- project BA-PHERD, funded by the European Union -- NextGenerationEU, under the National Recovery and Resilience Plan (NRRP) Mission 4 Component 2 Investment Line 1.1: "Fondo Bando PRIN 2022" (CUP G53D23002910006)
- MUSA -- Multilayered Urban Sustainability Action -- project, funded by the European Union -- NextGenerationEU, under the National Recovery and Resilience Plan (NRRP) Mission 4 Component 2 Investment Line 1.5: Strengthening of research structures and creation of R&D "innovation ecosystems", set up of "territorial leaders in R&D" (CUP G43C22001370007, Code ECS00000037)
- project SERICS (PE00000014) under the NRRP MUR program funded by the EU - NGEU
- project SOV-EDGE-HUB funded by Università degli Studi di Milano -- PSR 2021/2022 -- GSA -- Linea 6
- Università degli Studi di Milano under the program ``Piano di Sostegno alla Ricerca''
- SUMMIT program Pack Ambition of the Auvergne Rhône Alpes region
- FRIENDLY of the LIRIS lab

Views and opinions expressed are however those of the authors only and do not necessarily reflect those of the European Union or the Italian MUR. Neither the European Union nor the Italian MUR can be held responsible for them.

## License

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
