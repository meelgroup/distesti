
# DistEsti: Distance Estimation for High-Dimensional Discrete Distributions

This repository contains the implementation for the paper "Distance Estimation for High-Dimensional Discrete Distributions", presented at AISTATS 2025.

**Paper:** [https://openreview.net/forum?id=qmZwsWnMi7](https://openreview.net/forum?id=qmZwsWnMi7)

## Abstract

Given two distributions P and Q over a high-dimensional domain $\{0, 1\}^n$, and a parameter $\epsilon$, the goal of distance estimation is to determine the statistical distance between P and Q, up to an additive tolerance $\pm\epsilon$. Since exponential lower bounds (in n) are known for the problem in the standard sampling model, research has focused on richer query models where one can draw conditional samples. This paper presents the first polynomial query distance estimator in the conditional sampling model (COND). We base our algorithm on the relatively weaker \textit{subcube conditional} sampling (SUBCOND) oracle, which draws samples from the distribution conditioned on some of the dimensions. SUBCOND is a promising model for widespread practical use because it captures the natural behavior of discrete samplers. Our algorithm makes $\tilde{\mathcal{O}}(n^{3}/\epsilon^{5})$ queries to SUBCOND.

## Install

1.  **Clone DistEsti:**
    ```bash
    git clone https://github.com/meelgroup/distesti
    cd distesti
    ```
2.  **Requirements:**
    * Python 3.x
    * Python libraries: `numpy`, `gmpy2`
    * External Binaries: The tool relies on several external samplers and solvers. These are expected to be compiled and available in a `samplers/` subdirectory or accessible in the system `PATH`. See the Dependencies section below.
3.  **Install Python Dependencies:**
    ```bash
    pip install numpy gmpy2
    # Or using a virtual environment (recommended)
    # python3 -m venv distesti-venv
    # source distesti-venv/bin/activate
    # pip install numpy gmpy2
    ```
4.  **Build/Configure External Dependencies:**
    * You will need to obtain and compile the external samplers/solvers listed below (e.g., UniGen, QuickSampler, CMSGen, etc.).
    * *(Optional: Create a script similar to Manthan's `configure_dependencies.sh` to automate this process).* Ensure the compiled binaries are placed in a `samplers/` directory or are otherwise accessible.

## Dependencies

DistEsti depends on:

* **Python Libraries:**
    * `numpy`
    * `gmpy2`
* **External Samplers/Solvers:** (Assumed to be placed in `samplers/`)
    * UniGen/AppMC3
    * QuickSampler (and its dependency `z3`)
    * STS
    * CMSGen
    * SPUR
    * (Optionally, for related functionalities or specific configurations mentioned in internal code: `sharpSAT`, `d4`/`Dsharp_PCompile`)

## How to Use

*(Optional: Activate virtual environment if used: `source distesti-venv/bin/activate`)*


**Sampler IDs:**
* 1: UniGen3 
* 2: QuickSampler
* 3: STS
* 4: CMSGen
* 5: AppMC3 
* 6: SPUR 
* 7: WCMS 

**Example Usage:**

* Using `protoclon.py`:
    ```bash
    python protoclon.py --sampler1 <ID> --sampler2 <ID> --epsilon <float> --delta <float> --seed <int> <input1.cnf> [<input2.cnf>]
    ```
    Example:
    ```bash
    python protoclon.py --sampler1 4 --sampler2 4 --epsilon 0.5 --delta 0.4 --seed 123 tests/20_0_0.cnf tests/20_0_1.cnf
    ```


See `python <script_name>.py --help` for more options.

## Benchmarks

Sample benchmarks and generation scripts can be found in the `tests/` directory.
