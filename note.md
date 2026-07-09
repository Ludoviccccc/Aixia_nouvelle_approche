**Definition**

* Mechanism: Behvarior unit that is described as with a performance counter.
* Behavior: a dynamic during the execution on the platform. It can be made from multiple mechanisms. 
* Interference source: An interference source is a component on the processor that has simultaneous use by several cores or other initiators that may entail interferences. Examples of interference sources are shared caches and interconnect. (Technical Report/FAA)


Empathazing on the fact that a simulator allows to access information that is not available in a real case scenario, one don't fix a threshold for the knowledge to exploit and that is available in a simulator.

# Use the simulator to modify the output values




One aim to identidy which part of the simulator is responsible for interference, by using metrics on regular time windows.


One would appreciate it to be as precise as possible for the location of the studied mechanisms.



* Using the following metrics will help identifying the sources of interference, by comparing the two execution cases, parallel execution and isolated execution.

1. Bus bandwidth

2. DDR bandwidth

3. miss/hit during.

4. Execution time difference. 

**Remarks**:

* The metrics above will be observed on time(cycle) windows. The size of the windows is a pameter.
* The three first metrics are the ones required in "A Survey of Techniques for Reducing Interference in Real-Time Applications on Multicore Platforms (2022)"
* Ongoing implementation is avaiable : [here](https://github.com/Ludoviccccc/Aixia_nouvelle_approche/tree/newtargets)

# Use a LLM that can read the simulator code.
The behavior space is made of pseudo log description, that is, each point in the behavior space is a set of sentences describing what interference phenomena occured.
* **We would like a single parallel exeuction to be sufficient to highlight interference**
This would leverage several avantages
1. Generation of pseudo-log goals could be eased, having access to the simulator.
2. This could help goal achiavement policy.
Remark


