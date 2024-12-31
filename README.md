# L* Algorithm Implementation

This package provides a Python implementation of Angluin's L* algorithm for learning deterministic finite automata (DFA) from examples and queries. The implementation is particularly useful for reverse engineering black-box systems, protocol inference, and grammar learning tasks.

## Key Features

- Clean implementation of the L* learning algorithm
- Support for both membership and equivalence queries
- Built-in protocol simulation and testing framework
- Multiple example oracles for different language patterns
- Comprehensive test suite demonstrating various use cases

## When to Use L*

The L* algorithm is particularly valuable when you need to:

1. Reverse engineer black-box systems or protocols
2. Learn and document legacy system behaviors
3. Test protocol implementations for compliance
4. Generate formal models of systems for verification
5. Learn regular grammars from examples

The algorithm requires two key components:
- An oracle that can answer membership queries about the target language
- A finite alphabet of possible tokens/actions

## Installation

```bash
pip install lstar-learner
```

## Quick Start

```python
from lstar_learner import LStarLearner
from oracle import Oracle

# Define your oracle
class MyOracle(Oracle):
    def membership_query(self, string):
        # Implement your logic here
        pass

# Initialize learner
learner = LStarLearner()
oracle = MyOracle()

# Define alphabet and examples
alphabet = {'token1', 'token2', 'token3'}
examples = {
    'positive': {'token1 token2', 'token2 token3'},
    'negative': {'token3 token1'}
}

# Learn the DFA
learner.initialize(alphabet, examples, oracle)
dfa = learner.learn()
```

## Example Use Cases

### 1. Protocol Learning

The package includes a protocol simulation example (`black_box_sim.py`) that demonstrates learning a stateful communication protocol:

```python
from black_box_sim import learn_protocol

# Learn a protocol with states: INIT -> READY -> AUTHENTICATED
dfa = learn_protocol()
```

The protocol example shows how to model a system with:
- State transitions (INIT, READY, AUTHENTICATED)
- Authentication requirements
- Session management
- Error handling

### 2. Pattern Recognition

The test suite (`tests.py`) includes several example oracles that recognize different patterns:

#### Even Number of 'a's
```python
class EvenAsOracle(Oracle):
    def membership_query(self, string):
        return sum(1 for token in string.split() if token == 'a') % 2 == 0
```

## Project Structure

```
.
├── README.md
├── docs
│   ├── lstar.html
│   └── myhill-nerode.html
├── src
│   ├── __init__.py
│   ├── black_box_sim.py
│   ├── lstar_learner.py
│   ├── oracle.py
│   └── utils.py
└── tests
    ├── __init__.py
    ├── test_black_box.py
    └── tests.py

```

## Implementation Details

The L* learner maintains an observation table and systematically:
1. Checks if the table is closed and consistent
2. Handles counterexamples by adding relevant prefixes/suffixes
3. Constructs a DFA hypothesis
4. Verifies the hypothesis against the oracle

The learned DFA includes:
- States and transitions
- Initial and accepting states
- A complete transition function

## Contributing

Contributions are welcome! Some areas for potential improvement:
- Additional oracle implementations
- Performance optimizations
- Extended test coverage
- Documentation improvements

## License

MIT

## Citation

If you use this implementation in your research, please cite:

```bibtex
@misc{your-package-name,
  author = {James Kelly},
  title = {L* Algorithm Implementation},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/yourusername/your-repo}
}
```