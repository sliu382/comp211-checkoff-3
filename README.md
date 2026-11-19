# Performance Benchmarking

### What is performance benchmarking?
Performance benchmarking is a way to measure and evaluate program performance, allowing programmers to compare the efficiency of different languages or algorithms.

Using benchmark results, developers can then optimize their code and make informed decisions about the  tradeoffs between development time and execution efficiency.

### What did I explore?
This benchmark compares integer summation in Python and C. Specifically, the C program was compiled using four different optimization levels: '-O0', '-O1', '-O2', and 'O3'.

The goal was to investigate how programming language, optimization levels, and input size affected the execution time.
## Summary of Discoveries
**Time Complexity:** As input size increased, the runtime also grew linearly. This showcases that the algorithm has O(N) time complexity.

**C vs Python:** Even without optimization (-O0), the C program was still about 21-22x faster than the Python program for all input sizes.

**Compiler Optimizations:** The C program was about the same for -O2 and -O3. When looking at only the C optimization levels, the biggest execution jump was going from -O1 to -O2.

**Measurement Limitations:** For the smaller sample fo 10,000 integers, some of the trials for -O2 and -O3 recorded zero elapsed time. This causes an unclear comparison.


## Steps to Run Code
### 1. Run the benchmark
Run this in the terminal:
```
bash python3 run_tests.py
```

### 2. Set up Matplotlib
```bash
python3 -m venv .venv
.venv/bin/python -m pip install matplotlib
```
### 3. Generate the graphs
```bash
.venv/bin/python plot_results.py
```
## Additional Resources
ChatGPT Permalink
https://chatgpt.com/share/6afe7603-46dc-83ea-af1b-ff12072aa5d0

Presentation Slides
https://canva.link/6bltf12h2p7wnqn 