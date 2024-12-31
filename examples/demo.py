from lstar import LStarLearner, Oracle, CounterexampleStrategy, run_dfa
import time
from itertools import product

class EndsInAOracle(Oracle):
    """Simple language: accepts strings that end in 'a'"""
    def membership_query(self, string):
        if not string:
            return False
        return string.split()[-1] == 'a'
    
    def equivalence_query(self, dfa):
        """Test if the learned DFA is equivalent to our language"""
        # Test strings up to length 3
        test_cases = ['']  # Empty string case
        for length in range(1, 4):
            for combo in product(['a', 'b'], repeat=length):
                test_case = ' '.join(combo)
                if run_dfa(dfa, test_case) != self.membership_query(test_case):
                    return test_case
        return None

class ProtocolOracle(Oracle):
    """Complex language: simulates a protocol with states"""
    def __init__(self):
        self.state = 'INIT'
        
    def membership_query(self, string):
        # Reset state for new query
        self.state = 'INIT'
        
        # Empty string is accepted in INIT state
        if not string:
            return True
            
        # Process each token in sequence
        for token in string.split():
            if token == 'HELLO' and self.state == 'INIT':
                self.state = 'READY'
            elif token == 'AUTH' and self.state == 'READY':
                self.state = 'AUTHENTICATED'
            else:
                return False
                
        return True  # Accept if we processed all tokens successfully
    
    
    def equivalence_query(self, dfa):
        """Test if the learned DFA is equivalent to our protocol"""
        # Test empty string first
        if run_dfa(dfa, "") != self.membership_query(""):
            return ""
            
        # Systematically test all combinations up to length 3
        symbols = ['HELLO', 'AUTH']
        for length in range(1, 4):
            for sequence in product(symbols, repeat=length):
                test = ' '.join(sequence)
                if run_dfa(dfa, test) != self.membership_query(test):
                    return test
                    
        return None  # No counterexample found
    

def benchmark_language(oracle, alphabet, examples, name="Language"):
    print(f"\nTesting {name}:")
    
    # Test with ALL_PREFIXES strategy
    learner = LStarLearner(strategy=CounterexampleStrategy.ALL_PREFIXES)
    start = time.time()
    learner.initialize(alphabet, examples, oracle)
    dfa = learner.learn()
    all_prefixes_time = time.time() - start
    all_prefixes_states = dfa['states']
    
    # Test with BINARY_SEARCH strategy
    learner = LStarLearner(strategy=CounterexampleStrategy.BINARY_SEARCH)
    start = time.time()
    learner.initialize(alphabet, examples, oracle)
    dfa = learner.learn()
    binary_search_time = time.time() - start
    binary_search_states = dfa['states']
    
    print(f"ALL_PREFIXES strategy:")
    print(f"  Time: {all_prefixes_time:.4f} seconds")
    print(f"  States in learned DFA: {all_prefixes_states}")
    print(f"BINARY_SEARCH strategy:")
    print(f"  Time: {binary_search_time:.4f} seconds")
    print(f"  States in learned DFA: {binary_search_states}")

def main():
    # Test simple "ends in a" language
    simple_alphabet = {'a', 'b'}
    simple_examples = {
        'positive': {'a', 'b a', 'a a'},
        'negative': {'b', 'a b', ''}
    }
    benchmark_language(
        EndsInAOracle(),
        simple_alphabet,
        simple_examples,
        "Simple 'ends in a' language"
    )
    
    # Test protocol language
    protocol_alphabet = {'HELLO', 'AUTH'}
    protocol_examples = {
        'positive': {'', 'HELLO', 'HELLO AUTH'},  # Empty string is accepted
        'negative': {
            'AUTH',              # Can't start with AUTH
            'AUTH HELLO',        # Wrong order
            'HELLO HELLO',       # Can't repeat HELLO
            'AUTH AUTH',         # Can't repeat AUTH
            'HELLO AUTH AUTH'    # Can't repeat AUTH after valid sequence
        }
    }
    benchmark_language(
        ProtocolOracle(),
        protocol_alphabet,
        protocol_examples,
        "Protocol with states"
    )

if __name__ == "__main__":
    main()