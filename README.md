# Implementing Consensus Protocol

## Project Overview

This project originates from my study of the classic paper *Impossibility of Distributed Consensus with One Faulty Process* (FLP Theorem).

While reading the early sections of the paper, I encountered difficulty understanding the structure and concepts of the proposed consensus protocol. Abstract notions such as "configurations," "steps," and "indecisive runs" were challenging to grasp without an intuitive or experimental perspective. 

To address this, I decided to implement a **simple asynchronous consensus protocol** that captures the essence of the FLP model. This simulator aims to experimentally reproduce key concepts from the FLP proof - including decsion states, bivalence, and event-driven execution - and to serve as a **visual tool** for learners and researchers alike.

## Key Features 

- Simulate asynchronous message delivery with random delays
- Models consensus based on each process's input register
- Allows for experimental setups that demonstrate **bialent/univalent configuration**
- Logs and visualizes decision-making over time
- Supports **animated visualization** of message passing and internal state transitions (via matplotlib)

## How to Run

```bash
# Install dependencies
pip install matplotlib pillow

#Run simulation
python partial_correct_protocol.py
```

- Execution logs will be save to ```output_log.txt```
- The animated consensus run will be saved as ```flp_simulation.gif```

## References
- Fischer, Lynch, Paterson (1985). *Impossibility of Distributed Consensus with one Faulty Process*.


## Current Situation
- The current simulator uses a majority-based decision logic, which is already in univalent states from the beginning
- It's difficult to visually demonstrate FLP's key concept: the existence of bivalent configurations and indecisive runs
- However, the simulator has strong educational and modeling value in terms of process design, event scheduling, and state transitions


## Future Plans

- Implement **randomized consensus** (Ben-Or protocol) for comparison
- Extend the simulator to support **partial synchrony models** (e.g., timeouts, bounded delays)
- Experimentally compare with practical consensus protocols like **PBFT, RAFT**
- Explore implications for **blockchain and Web3 consensus**