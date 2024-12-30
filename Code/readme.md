# Technical Details

## Building Blocks Structure

### Trust attributes

Trust attribute are integer value in [0, 1, 2], from worst to best.

``` python
sd = 1
```

### Requirements

Requirements are a tuple of the form: (*range*, *cardinality*), where:

- *range* is a list of int: 
  - the first (min) in a range of [0, 1, 2]
  - the second (max) is always 2, to define an open range `[x, +inf)`
- *cardinality* is an int in the range [0, 1]

``` python
req = ([0, 2], 1)
```

### Policy

Policies are list of floats: [*min_0*, *min_1*], where:

- *min_0* is the minimum value to accept the collaboration
- *min_1* is the best value to perform a better action

``` python
policy = [0.3, 0.6]
```

### Changes

A change is defined as a tuple of the form: (*service data*, *new value*), where:

- *service data* is the "name" of the service data that change
- *new value* is the new service data value

``` python
ch = ('sd0', 2)
```

### Service

Each service is represented as a dict that contains:

- *service data*: 
  - for each service data there is a key of the form 'sdX', for instance: 'sd0', 'sd1', etc, and the associated value
- *requirements*:
  - for each requirement there is a key of the form 'reqX', for instance: 'req0', 'req1', etc, and the associated value
- *policy*:
  - the dictionary has a 'policy' key with the associated value
- *changes*:
  - the dictionary has a 'change' key with an array of changes

``` python
service = {
    'sd0': 0
    'req0': ([1, 2], 1)
    'sd1': 2
    'req1': ([0, 2], 0)
    'sd2': 1
    'req2': ([2, 2], 1)
    'policy': [0.3, 0.6]
    'change': [('sd0', 1), ('sd1', 0), ('sd2', 2)]
}
```

### System

After the first negotiation, the system is represented as a list of tuple of the form: (*service X*, *satisfaction X*), where:

- *service X* is a dict
- *satisfaction X* is a float

```python
system = [
    (
        {
            'sd0': 2
            'req0': ([1, 2], 1)
            'policy': [0.3, 0.6]
            'change': [('sd0', 1)]
        },
        0.7
    ),
    (
        {
            'sd0': 2
            'req0': ([1, 2], 1)
            'policy': [0.3, 0.6]
            'change': [('sd0', 1)]
        },
        0.9
    )
]
```

To access values after the handshake you can follow this:

1. access to a service: ```system[i][0]``` &rarr; get the service at position *i* 
2. access to a satisfaction: ```system[i][1]``` &rarr; get the satisfaction of the service at position *i* 
3. access to the value of *'sd0'*: ```system[i][0]['sd0']``` &rarr; get the value of the service data *'sd0'* of the service  at position *i*
4. perform a change: ```system[i][0][system[i][0]['change'][0][0]] = system[i][0]['change'][0][1]``` &rarr; change the value of the service data indicated in the first change

Explanation:

1. ```system = [(service0, sd0), ...]```
    - &rarr; ```system[0] = (service0, sd0)```
    - &rarr; ```system[0][0] = service0```
2. ```system = [(service0, sd0), ...]```
    - &rarr; ```system[0] = (service0, sd0)```
    - &rarr; ```system[0][1] = sd0```
3. ```system = [(service0, sd0), ...]```
    - &rarr; ```system[0] = (service0, sd0)```
    - &rarr; ```system[0][0] = service0 == {'sd0': 1, ...}```
    - &rarr; ```system[0][0]['sd0'] = 1```
4. ```system = [(service0, sd0), ...]```
    - &rarr; ```system[0] = (service0, sd0)```
    - &rarr; ```system[0][0] = service0 == {..., 'change': [('sd0', 2)]}```
    - &rarr; ```system[0][0]['change'] = [('sd0', 2)]```
    - &rarr; ```system[0][0]['change'][0] = ('sd0', 2)```
    - &rarr; ```system[0][0]['change'][0][0] = 'sd0'```
    - &rarr; ```system[0][0]['change'][0][1] = 2```
    - &rarr; ```system[0][0][system[0][0]['change'][0][0]] = service0['sd0']```
    - &rarr; ```system[0][0][system[0][0]['change'][0][0]] = system[0][0]['change'][0][1] == service0['sd0'] = 2```

In a loop:

``` python
for service in system: 
    print(service[0]['change'])

>>> [('sd0', 1), ('sd1', 0)]
```

### Datasets

Each setting in Section 6.1 corresponds to an individual *dataset*, containing the services described in terms of trust attributes, requirements, policies, and so on. Each dataset is a CSV file containing the following columns:

- `service`: represents the index of the service, i.e., `0`, `1`, `2`, ...
- `setting`: represents the name of the setting, i.e., `G0.0.0`, `G0.0.1`, ...
- `sdnX`: represents the value of the X-th trust attribute, i.e., `0`, `1`, `2`
- `reqX`: represents the requirements on trust X-th attribute, i.e., `([0, 2], 0), ([1, 2], 1),` ...
- `policy`: represents the service policy, i.e., `[0.3, 0.6]`, `[0.6, 0.9]`, ...
- `change`: represents the changes of a service, i.e., `[('sd0', 0), ('sd2', 1)], [], [('sd3', 0)]`, ...

An example:

|`service`|`setting`|`sd0`|`req0`|`sd1`|`req1`|`policy`|`change`|
|----|-------|---|----|---|----|------|------|
|`0`|`G0.0.0`|`1`|`([0, 2], 1)`|`2`|`([1, 2], 0)`|`[0.3, 0.6]`|`[('sd0', 2)]`|
|`1`|`G0.0.0`|`2`|`([2, 2], 0)`|`1`|`([0, 2], 0)`|`[0.6, 0.9]`|`[('sd0', 1)]`|
|`2`|`G0.0.0`|`0`|`([1, 2], 1)`|`2`|`([0, 2], 1)`|`[0.3, 0.6]`|`[('sd0', 1), ('sd1', 1)]`|
