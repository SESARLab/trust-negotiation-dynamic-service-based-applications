# A Trust Management System for Collaborative, Federated Service-Based Applications

[![CC BY 4.0][cc-by-shield]][cc-by]

[**Nicola Bena**](https://homes.di.unimi.it/bena), [**Genoveva Vargas-Solar**](http://vargas-solar.com/), [**Nadia Bennani**](https://liris.cnrs.fr/en/member-page/nadia-bennani), [**Nicolò Grecchi**](https://www.linkedin.com/in/nicol%C3%B2-grecchi-6b094123b/) [**Chirine Ghedira-Guegan**](https://liris.cnrs.fr/en/member-page/chirine-ghedira-guega), [**Claudio A. Ardagna**](https://homes.di.unimi.it/ardagna)

> In the last two decades, the long-standing promise of service-based software has been realized, transitioning from traditional client-server architecture to distributed, service-based systems. Applications built upon these systems dynamically compose services from multiple, often unknown, parties to share and process vast amounts of data and collaboratively define and optimize new business processes. More recently, these applications have been evolving toward collaborative, federated architectures, where each component service delivers the same core functionality but differs in the data it contributes and in the supported non-functional behavior (e.g., security, privacy). As these applications become increasingly complex and new regulations emerge, participating services must understand each other's non-functional behavior before joining the application, ensuring that their trust requirements are met. This scenario is reviving the trust issue that emerged with the advent of the commercial Internet in the 90s. Contrary to the past, trust must now empower dynamic, open applications rather than static, client-server operations, and must be used by each service to determine whether to participate in the application. This paper proposes a Trust Management System (TMS) that addresses the specific needs of collaborative, federated service-based applications. It implements a trust negotiation protocol that supports partial negotiation to maximize negotiation success and ensures trust establishment over time and across service changes. The proposed approach is demonstrated through a Federated Learning (FL) collaborative application that studies the long-term effects of COVID-19 and is experimentally evaluated in a comprehensive simulated environment.

## Overview

This repository contains:

- the code used to run the experiments (directory [`Code`](Code)), described [here](#code-details)
- the result shown in the paper (directory [`Data`](Data)), described [here](#result-details)
- the instruction to exactly replicate the results shown in the paper (this file), described [here](#experimental-process)
- the instruction to exactly replicate the described shown in the paper (this file), described [here](#walkthrough).

## Experimental Process

The following steps reproduce the experimental process. We assume they are executed within the directory [`Code`](Code).

### 1. Environment Setup

Install the requirements using `conda`. The file [`Code/environment.yaml`](Code/environment.yaml) lists the requirements needed to execute the code.

```bash
conda env create -n <env-name> -f environment.yml
```

### 2. Execution

First, activate the *conda environment* in the same directory as before:

```bash
conda activate <env-name>
```

The file [`execute.sh`](execute.sh) contains the exact sequence of steps to be followed. 

We need to define a directory where you want to store the data.

```bash
DEST_DIR=Out

mkdir $DEST_DIR
```

Next, we execute the actual experiments.

```bash
python main.py --output-dir $DEST_DIR
```

It takes around 40 minutes on a MacOS M1 Pro. The option `-J` specifies the number of parallel jobs (equal to the number of cores by default).

### 3. Post-Processing

Some post-processing is involved to get the data in the shape used in the paper. We work on post-processed files in the directory `$DEST_DIR/03_post`.

```bash
mkdir $DEST_DIR/03_post
```

Data for plotting the quality of trust negotiation over settings `G2.3.*`:

```bash
python utils.py filter-pivot \
  --input-file $DEST_DIR/01_quality/02_agg1_results.csv \
  --output-file $DEST_DIR/03_post/sensitivity_G2.3.X \
  --filter setting_name=G2.3.1,G2.3.2,G2.3.3 \
  --target-col avg_negotiation_success_rate
```

Data to compare success rate against SOTA (we export SOTA and SOTA with policy all-or-nothing):

```bash
python utils.py aggregate-setting-level \
  --input-file $DEST_DIR/01_quality/01_agg2_results.csv \
  --output-file $DEST_DIR/03_post/quality_neg_comparison.csv \
  --levels 0 1 \
  --output-cols \
    avg_avg_negotiation_success_rate \
    avg_avg_trust_value \
    avg_avg_sota1_success_rate \
    avg_avg_sota2_success_rate \
    avg_avg_sota2_trust_value \
    avg_avg_sota2_unsupported_service_rate \
    avg_avg_sota2_requirement_violation_rate \
    avg_avg_sota3_success_rate
```

Data to measure the quality of dynamic trust:

```bash
python utils2.py aggregate-setting-level \
  --input-file $DEST_DIR/01_quality/01_agg2_results.csv \
  --output-file $DEST_DIR/03_post/quality_dyn_comparison.csv \
  --levels 2 \
  --output-cols \
    avg_avg_global_application_stability \
    avg_avg_global_service_stability
```

Performance of negotiation:

```bash
python utils2.py filter-pivot \
  --input-file $DEST_DIR/02_performance/performance.csv \
  --output-file $DEST_DIR/03_post/performance_01neg_G2.3.X_G.4.2.X \
  --filter setting_name=G2.3.1,G2.3.2,G2.3.3,G4.2.1,G4.2.2,G4.2.3 \
  --target-col negotiation_avg
```

Performance of dynamic negotiation:

```bash
python utils2.py filter-pivot \
  --input-file $DEST_DIR/02_performance/performance.csv \
  --output-file $DEST_DIR/03_post/performance_02dyn_G2.3.X_G.4.2.X \
  --filter setting_name=G2.3.1,G2.3.2,G2.3.3,G4.2.1,G4.2.2,G4.2.3 \
  --target-col dynamic_trust_avg
```

## Result Details

Results are organized as follows.

- [`Data/01_quality/`](Data/01_quality): results of the quality evaluation
  - [`Data/01_quality/01_agg2_results.csv`](Data/01_quality/01_agg2_results.csv): avg results aggregated over the number of services and trust attributes (i.e., one row per setting)
  - [`Data/01_quality/02_agg1_results.csv`](Data/01_quality/02_agg1_results.csv): avg results aggregated over the 5 executions (i.e., one row for each combination of setting, number of services, number of trust attributes)
  - [`Data/01_quality/03_raw_results.csv`](Data/01_quality/03_raw_results.csv): raw results (one row for each setting, execution, number of services, number of trust attributes)
  - Subdirectories `snaposhots/GA.B.C/services_X_attributes_Y/run_Z` contains the raw data for settings `GA.B.C` with number of services=`X` and number of trust attributes=`Y` for execution number=`Z`. For instance, assuming `G1.1.1`, `X=10`, `Y=10` and `Z=0`, we have:
    - [`Data/01_quality/snapshots/G1.1.1/services_10_attributes_10/run_0/services.json`](Data/01_quality/snapshots/G1.1.1/services_10_attributes_10/run_0/services.json): the set of services randomly generated
    - [`Data/01_quality/snapshots/G1.1.1/services_10_attributes_10/run_0/negotiation.json`](Data/01_quality/snapshots/G1.1.1/services_10_attributes_10/run_0/negotiation.json): the result of the initial negotiation
    - [`Data/01_quality/snapshots/G1.1.1/services_10_attributes_10/run_0/dynamic_trust_snapshot.json`](Data/01_quality/snapshots/G1.1.1/services_10_attributes_10/run_0/dynamic_trust_snapshot.json): dynamic trust across the different iterations
- [`Data/02_performance`](Data/02_performance): results of the performance evaluation
  - [](Data/02_performance/performance.csv): aggregated results of the performance evaluation
  - Subdirectories `G2.3.*` and `G4.2.*` contains the raw measurements of `pytest-benchmark`. For instance, file [`Data/02_performance/G2.3.1/services_10_attributes_10.json`](Data/02_performance/G2.3.1/services_10_attributes_10.json) contains the raw performance measurements when using 10 services and 10 trust attributes.
- [`Data/03_post`](Data/03_post): post-processing results
  - [`Data/03_post/quality_neg_comparison.csv`](Data/03_post/quality_neg_comparison.csv): quality of the (initial) negotiation
  - [`Data/03_post/quality_dyn_comparison.csv`](Data/03_post/quality_dyn_comparison.csv): quality of dynamic trust
  - [`Data/03_post/sensitivity_G2.3.X_na.csv`](Data/03_post/sensitivity_G2.3.X_na.csv): sub-results for ablation, varying the number of trust attributes (used for plotting)
  - [`Data/03_post/sensitivity_G2.3.X_ns.csv`](Data/03_post/sensitivity_G2.3.X_ns.csv): sub-results for ablation, varying the number of services (used for plotting)
  - [`Data/03_post/performance_01neg_G2.3.X_G.4.2.X_na.csv`](Data/03_post/performance_01neg_G2.3.X_G.4.2.X_na.csv): sub-results for performance of the initial negotiation, varying the number of trust attributes (used for plotting)
  - [`Data/03_post/performance_01neg_G2.3.X_G.4.2.X_ns.csv`](Data/03_post/performance_01neg_G2.3.X_G.4.2.X_na.csv): sub-results for performance of the initial negotiation, varying the number of services (used for plotting)
  - [`Data/03_post/performance_02dyn_G2.3.X_G.4.2.X_na.csv`](Data/03_post/performance_02dyn_G2.3.X_G.4.2.X_na.csv): sub-results for performance of dynamic trust, varying the number of trust attributes (used for plotting)
  - [`Data/03_post/performance_02dyn_G2.3.X_G.4.2.X_ns.csv`](Data/03_post/performance_02dyn_G2.3.X_G.4.2.X_na.csv): sub-results for performance of dynamic trust, varying the number of services (used for plotting)

### A Note on SOTA

In the experiment data and code we use the following terminology:

- `SOTA1`: ablation study
- `SOTA2`: pairwise trust (just *SOTA* in the paper)
- `SOTA3`: pairwise trust with all-or-nothing policy (briefly mentioned in the paper)

## Code Details

The code is written in Python and consists of the following files.

- [`Code/benchmarks.py`](Code/benchmarks.py): low-level performance
- [`Code/conftest.py`](Code/conftest.py): utils for `pytest`
- [`Code/dataset_generator.py`](Code/dataset_generator.py): generate services
- [`Code/environment.yaml`](Code/environment.yaml): `conda` env
- [`Code/model.py`](Code/model.py): main data classes
- [`Code/performance.py`](Code/performance.py): orchestrate performance
- [`Code/settings_data.py`](Code/settings_data.py): value of the settings
- [`Code/settings_model.py`](Code/settings_model.py): data classes for the settings
- [`Code/simulation_export.py`](Code/simulation_export.py): utils to export simulation data
- [`Code/simulation_model.py`](Code/simulation_model.py): data classes for the simulations
- [`Code/simulation_sota.py`](Code/simulation_sota.py): simulate the executions of SOTA using [`Code/trust_sota.py`](Code/trust_sota.py)
- [`Code/trust_core.py`](Code/trust_core.py): core trust functions 
- [`Code/trust_dynamic.py`](Code/trust_dynamic.py): implement dynamic trust 
- [`Code/trust_negotiation.py`](Code/trust_negotiation.py): negotiation in our approach
- [`Code/trust_sota.py`](Code/trust_sota.py): implement SOTA functionalities
- [`Code/utils.py`](Code/utils.py): used for post-processing 
- [`Code/walkthrough.py`](Code/walkthrough.py): entrypoint/data for the walkthrough
- [`Code/walkthrough_base.py`](Code/walkthrough_base.py): utils for the walkthrough

## Walkthrough

The code can simulate the walkthrough as discussed in the paper. The file [`Code/walkthrough.py`](Code/walkthrough.py) contains the definitions of services and the changes that occur, and execute the (dynamic) trust negotiation protocol, showing the results as JSON.

First, you need to activate the environment as shown [here](#experimental-process).

Then, just execute the file [`Code/walkthrough.py`](Code/walkthrough.py).

```bash
python walkthrough.py
```

The output, corresponding to Section 6, is the following.

```json
{
  "included": [
    {
      "name": "s_brazil",
      "trust_value": 0.6666666666666666,
      "action": 1
    },
    {
      "name": "s_chile",
      "trust_value": 0.6666666666666666,
      "action": 0
    },
    {
      "name": "s_france",
      "trust_value": 0.6666666666666666,
      "action": 0
    },
    {
      "name": "s_mexico",
      "trust_value": 0.6666666666666666,
      "action": 1
    },
    {
      "name": "s_poland",
      "trust_value": 0.6666666666666666,
      "action": 1
    },
    {
      "name": "s_romania",
      "trust_value": 1.0,
      "action": 1
    }
  ],
  "excluded": [
    {
      "name": "s_italy",
      "trust_value": 0.3333333333333333,
      "action": -1
    }
  ],
  "changes": [
    {
      "index": 0,
      "changed": {
        "service_name": "s_chile",
        "trust_attributes": [
          {
            "attribute_index": 2,
            "new_value": "EEU"
          }
        ]
      },
      "relevant": true,
      "metrics": {
        "application_stability": 1.0,
        "service_stability": 0.8333333333333334,
        "action_stability": 0.8333333333333334
      },
      "planning": {
        "decision": "KEEP",
        "scenario_keep": {
          "services_to_remove": [],
          "services_to_update": [
            {
              "name": "s_mexico",
              "trust_value": 0.3333333333333333,
              "action": 0
            }
          ]
        },
        "scenario_evict": {
          "services_to_remove": [],
          "services_to_update": [
            {
              "name": "s_mexico",
              "trust_value": 0.3333333333333333,
              "action": 0
            }
          ]
        }
      },
      "after_change": {
        "included": [
          {
            "name": "s_brazil",
            "trust_value": 0.6666666666666666,
            "action": 1
          },
          {
            "name": "s_chile",
            "trust_value": 0.6666666666666666,
            "action": 0
          },
          {
            "name": "s_france",
            "trust_value": 0.6666666666666666,
            "action": 0
          },
          {
            "name": "s_mexico",
            "trust_value": 0.3333333333333333,
            "action": 0
          },
          {
            "name": "s_poland",
            "trust_value": 0.6666666666666666,
            "action": 1
          },
          {
            "name": "s_romania",
            "trust_value": 1.0,
            "action": 1
          }
        ],
        "excluded": []
      }
    },
    {
      "index": 1,
      "changed": {
        "service_name": "s_romania",
        "trust_attributes": [
          {
            "attribute_index": 1,
            "new_value": 15
          }
        ]
      },
      "relevant": true,
      "metrics": {
        "application_stability": 0.8333333333333334,
        "service_stability": 1.0,
        "action_stability": 0.8333333333333334
      },
      "planning": {
        "decision": "EVICT",
        "scenario_keep": {
          "services_to_remove": [
            {
              "name": "s_brazil",
              "trust_value": 0.3333333333333333,
              "action": -1
            },
            {
              "name": "s_mexico",
              "trust_value": 0,
              "action": -1
            }
          ],
          "services_to_update": []
        },
        "scenario_evict": {
          "services_to_remove": [],
          "services_to_update": []
        }
      },
      "after_change": {
        "included": [
          {
            "name": "s_brazil",
            "trust_value": 0.6666666666666666,
            "action": 1
          },
          {
            "name": "s_chile",
            "trust_value": 0.6666666666666666,
            "action": 0
          },
          {
            "name": "s_france",
            "trust_value": 0.6666666666666666,
            "action": 0
          },
          {
            "name": "s_mexico",
            "trust_value": 0.3333333333333333,
            "action": 0
          },
          {
            "name": "s_poland",
            "trust_value": 0.6666666666666666,
            "action": 1
          }
        ],
        "excluded": []
      }
    },
    {
      "index": 2,
      "changed": {
        "service_name": "s_poland",
        "trust_attributes": [
          {
            "attribute_index": 0,
            "new_value": "urban"
          }
        ]
      },
      "relevant": true,
      "metrics": {
        "application_stability": 0.8,
        "service_stability": 1.0,
        "action_stability": 0.8
      },
      "planning": {
        "decision": "KEEP",
        "scenario_keep": {
          "services_to_remove": [
            {
              "name": "s_france",
              "trust_value": 0.3333333333333333,
              "action": -1
            }
          ],
          "services_to_update": []
        },
        "scenario_evict": {
          "services_to_remove": [
            {
              "name": "s_france",
              "trust_value": 0.3333333333333333,
              "action": -1
            }
          ],
          "services_to_update": []
        }
      },
      "after_change": {
        "included": [
          {
            "name": "s_brazil",
            "trust_value": 0.6666666666666666,
            "action": 1
          },
          {
            "name": "s_chile",
            "trust_value": 0.6666666666666666,
            "action": 0
          },
          {
            "name": "s_mexico",
            "trust_value": 0.3333333333333333,
            "action": 0
          },
          {
            "name": "s_poland",
            "trust_value": 0.6666666666666666,
            "action": 1
          }
        ],
        "excluded": [
          {
            "name": "s_france",
            "trust_value": 0.3333333333333333,
            "action": -1
          }
        ]
      }
    }
  ]
}
```

This output is also [here](walkthrough.json5).

## Citation

Coming soon.

## Acknowledgements

This work was supported by:

- Piano di sostegno alla ricerca, Università degli Studi di Milano
- PSR 2025 -- Linea 8 -- Sottomisura A, Università degli Studi di Milano
- FRIENDLY of the LIRIS lab and INFILTRATE projects funded by the AT program -- LIRI

## License

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
