# L* Algorithm Visualization

An interactive visualization of Angluin's L* algorithm for learning regular languages through membership and equivalence queries.

## Web Visualization

Visit the live visualization here: https://semajyllek.github.io/lstar/

## About

The L* algorithm, developed by Dana Angluin, is a method for learning a regular language through experimentation. The algorithm works by:
1. Building an observation table through membership queries
2. Checking if the table is closed and consistent
3. Constructing a hypothesis DFA
4. Using counterexamples to refine the hypothesis

## Repository Structure
- `src/`: source code for L* algorithm implementation
- `docs/`: contains some theoretical documentation
- `tests/`: test suite showing algorithm correctness

## Running Locally
```bash
# Clone the repository
git clone https://github.com/semajyllek/lstar.git
cd lstar

# Install dependencies (if any)
pip install -r requirements.txt

# Run tests
pytest tests.py