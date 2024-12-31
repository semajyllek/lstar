import pytest
from lstar.utils import run_dfa
from itertools import product
from lstar.oracle import Oracle
from lstar.lstar_learner import LStarLearner




class EvenAsOracle(Oracle):
    def membership_query(self, string):
        return sum(1 for token in string.split() if token == 'a') % 2 == 0
        
    def equivalence_query(self, dfa):
        # Test strings up to length 3
        test_cases = ['']  # Empty string case
        for length in range(1, 4):
            for combo in product(['a', 'b'], repeat=length):
                test_cases.append(' '.join(combo))
                
        for test in test_cases:
            if run_dfa(dfa, test) != self.membership_query(test):
                return test
        return None

class EndsInABOracle(Oracle):
    def membership_query(self, string):
        tokens = string.split()
        return len(tokens) >= 2 and tokens[-2:] == ['a', 'b']
        
    def equivalence_query(self, dfa):
        # Test key cases with space-separated tokens
        test_cases = [
            '',
            'a',
            'b',
            'a b',
            'b a',
            'b a b',
            'a b a',
            'a a b',
            'b b a b'
        ]
        for test in test_cases:
            if run_dfa(dfa, test) != self.membership_query(test):
                return test
        return None

class NoThreeAsOracle(Oracle):
    def membership_query(self, string):
        tokens = string.split()
        count = 0
        for token in tokens:
            if token == 'a':
                count += 1
                if count >= 3:
                    return False
            else:
                count = 0
        return True
        
    def equivalence_query(self, dfa):
        # Generate strings systematically with space-separated tokens
        test_cases = ['']
        for length in range(1, 4):
            for combo in product(['a', 'b'], repeat=length):
                test_cases.append(' '.join(combo))
                
        for test in test_cases:
            if run_dfa(dfa, test) != self.membership_query(test):
                return test
        return None
    




# Fixtures for our oracles
@pytest.fixture
def even_as_oracle():
    return EvenAsOracle()

@pytest.fixture
def ends_in_ab_oracle():
    return EndsInABOracle()

@pytest.fixture
def no_three_as_oracle():
    return NoThreeAsOracle()

@pytest.fixture
def learner():
    return LStarLearner()

# Test membership queries
@pytest.mark.parametrize("input_string,expected", [
    ("", True),      # Empty string has 0 a's
    ("a", False),    # Single a
    ("a a", True),   # Two a's
    ("b a b", False),  # One a 
    ("a b b a", True),  # Two a's with b's between
])
def test_even_as_membership(even_as_oracle, input_string, expected):
    assert even_as_oracle.membership_query(input_string) == expected

@pytest.mark.parametrize("input_string,expected", [
    ("", False),
    ("a", False),
    ("b", False),
    ("a b", True),
    ("b a", False),
    ("b a b", True),
    ("a b a", False),
])
def test_ends_in_ab_membership(ends_in_ab_oracle, input_string, expected):
    assert ends_in_ab_oracle.membership_query(input_string) == expected

@pytest.mark.parametrize("input_string,expected", [
    ("", True),
    ("a a", True),
    ("a a a", False),
    ("b a b a", True),
    ("b a a a b", False),
])
def test_no_three_as_membership(no_three_as_oracle, input_string, expected):
    assert no_three_as_oracle.membership_query(input_string) == expected

# Test full learning process
def test_learn_even_as(learner, even_as_oracle):
    alphabet = {'a', 'b'}
    examples = {
        'positive': {'', 'a a', 'a b b a'},
        'negative': {'a', 'a a a'}
    }
    
    learner.initialize(alphabet, examples, even_as_oracle)
    dfa = learner.learn()
    
    test_cases = [
        ('', True),
        ('a', False),
        ('a a', True),
        ('a a a', False),
        ('a a a a', True),
        ('b', True),
        ('a b', False),
        ('a b a', True),
        ('a b a a', False)
    ]
    
    for string, expected in test_cases:
        assert run_dfa(dfa, string) == expected, f"Failed for input: {string}"

# Test DFA properties
def test_dfa_structure(learner, even_as_oracle):
    alphabet = {'a', 'b'}
    examples = {
        'positive': {'', 'a a'},
        'negative': {'a'}
    }
    
    learner.initialize(alphabet, examples, even_as_oracle)
    dfa = learner.learn()
    
    # Check DFA has required components
    assert all(key in dfa for key in ['states', 'initial', 'accepting', 'transitions'])
    assert dfa['initial'] < dfa['states']
    
    # Check transitions
    for (state, symbol), next_state in dfa['transitions'].items():
        assert state < dfa['states']
        assert next_state < dfa['states']
        assert symbol in alphabet

# Test oracle consistency
def test_oracle_consistency(even_as_oracle, ends_in_ab_oracle, no_three_as_oracle):
    oracles = [
        (even_as_oracle, "even as"),
        (ends_in_ab_oracle, "ends in ab"),
        (no_three_as_oracle, "no three as")
    ]
    
    # Generate test strings with space-separated tokens
    test_strings = ['']  # Empty string
    for length in range(1, 4):  # Test strings of length 1-3
        for tokens in product(['a', 'b'], repeat=length):
            test_strings.append(' '.join(tokens))
    
    for oracle, name in oracles:
        for test_string in test_strings:
            result1 = oracle.membership_query(test_string)
            result2 = oracle.membership_query(test_string)
            assert result1 == result2, f"{name} inconsistent for '{test_string}'"

# Error cases
def test_invalid_alphabet(learner, even_as_oracle):
    with pytest.raises(ValueError):
        learner.initialize({}, {'positive': {'a a'}, 'negative': {'a'}}, even_as_oracle)

def test_invalid_examples(learner, even_as_oracle):
    with pytest.raises(ValueError):
        learner.initialize({'a', 'b'}, {'positive': set(), 'negative': set()}, even_as_oracle)

