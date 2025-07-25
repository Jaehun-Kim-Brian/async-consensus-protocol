# Implementing Consensus Protocol

## Project Overview

This project originates from my study of the classic paper *Impossibility of Distributed Consensus with One Faulty Process* (FLP Theorem).

While reading the early sections of the paper, I encountered difficulty understanding the structure and concepts of the proposed consensus protocol. Abstract notions such as "configurations," "steps," and "indecisive runs" were challenging to grasp without an intuitive or experimental perspective. 

To address this, I decided to implement a **simple asynchronous consensus protocol** that captures the essence of the FLP model. This simulator aims to experimentally reproduce key concepts from the FLP proof - including decsion states, bivalence, and event-driven execution - and to serve as a **visual tool** for learners and researchers alike.

## Key Features 

- Modular simulation of asynchronous systems (message buffers, process steps, event handlers)
- Implementation of **Ben-Or's consensus protocol** using randomized decisions
- Fine-grained logging and internal state tracking per process
- Message delays and out-of-order delivery supported
- Future-message buffer (for round-mismatched events)
- Export of simulation logs in structured JSON format
- Visualization of protocol runs as **animated `.gif` and `.mp4` files**

## How to Run

```bash
# Install dependencies
pip install matplotlib pillow
sudo apt install ffmpeg  # Required for mp4 rendering

#Run simulation
python main.py

#Visualize the Output
python utils/visualizer.py
```

- Execution logs will be save to ```output_log.txt```
- The animated consensus run will be saved as ```flp_simulation.gif```

## References
- Fischer, Lynch, Paterson (1985). *Impossibility of Distributed Consensus with one Faulty Process*.
- Michael Ben-Or (1983). *Another Advantage of Free Choice: Completely Asynchronous Agreement Protocols*


## Observation & Limitations
- The simulator focuses on educational clarity rather than completeness of adversarial models.
- Some setups converge too quickly to a decision, limiting visual demonstration of bivalence.
- Indecisive configurations and Lemma 2/3 scenarios can be explored further through customized process failures or scheduling.


## Future Plans

Add support for:
- Partial synchrony models (timeouts, bounded delays)
- Other consensus protocols: PBFT, RAFT, DLS
- Fault injection and crash simulations

Enhance visualization:
- Differentiate message types by color
- Highlight faulty or crashed nodes