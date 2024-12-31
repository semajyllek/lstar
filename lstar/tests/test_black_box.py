import pytest
from examples.black_box_sim import ProtocolOracle
from lstar.lstar_learner import LStarLearner
from lstar.utils import run_dfa


# oracle tests

@pytest.fixture
def oracle():
    """Create a fresh ProtocolOracle instance in test mode for each test"""
    return ProtocolOracle(test_mode=True)

@pytest.mark.parametrize("sequence,expected", [
    # Basic protocol operations
    ("", True),                              # Empty sequence should be accepted
    ("HELLO", True),                         # Basic HELLO command works
    ("AUTH", False),                         # Can't AUTH without HELLO
    ("DATA", False),                         # Can't DATA without HELLO and AUTH
    ("CLOSE", False),                        # Can't CLOSE without HELLO and AUTH
    
    # Invalid sequences from incorrect ordering
    ("HELLO HELLO", False),                  # Can't say HELLO twice
    ("HELLO DATA", False),                   # Can't DATA right after HELLO
    ("HELLO CLOSE", False),                  # Can't CLOSE right after HELLO
    
    # Valid sequences following protocol
    ("HELLO AUTH", True),                    # Basic authentication sequence
    ("HELLO AUTH DATA", True),               # Can send DATA after auth
    ("HELLO AUTH CLOSE", True),              # Can CLOSE after auth
    
    # Session management
    ("HELLO AUTH CLOSE HELLO", True),        # Can start new session after CLOSE
    ("HELLO AUTH CLOSE HELLO AUTH", True),   # Can re-authenticate in new session
    
    # Multiple operations in authenticated state
    ("HELLO AUTH DATA DATA", True),          # Multiple DATA commands allowed
    ("HELLO AUTH DATA CLOSE", True),         # Can CLOSE after DATA
])
def test_sequences(oracle, sequence, expected):
    """
    Test various protocol sequences to verify:
    1. Basic command validation
    2. Proper state transitions
    3. Session management
    4. Multiple operations in authenticated state
    """
    assert oracle.membership_query(sequence) == expected

@pytest.mark.parametrize("sequence", [
    "AUTH HELLO",                # Can't HELLO after AUTH
    "HELLO DATA AUTH",          # Can't AUTH after DATA without new session
    "HELLO CLOSE AUTH",         # Can't AUTH after CLOSE without new HELLO
    "DATA HELLO",               # Can't HELLO after DATA
    "HELLO AUTH CLOSE DATA"     # Can't DATA after CLOSE without new session
])
def test_invalid_sequences(oracle, sequence):
    """
    Test sequences that should be rejected due to:
    1. Invalid state transitions
    2. Commands in wrong order
    3. Commands after session closure
    """
    assert oracle.membership_query(sequence) == False


def test_auth_retry_limit_exact(oracle):
    """
    Test that authentication is locked exactly after 3 failed attempts:
    1. Try auth attempts until we get 3 failures
    2. After 3 failures, system should be locked
    3. Verify locked state persists with new attempts
    """
    oracle = ProtocolOracle(test_mode=False)  # Don't use test mode to test real AUTH behavior
    
    failures = 0
    while failures < 3:
        if oracle.membership_query("HELLO AUTH") == False:
            failures += 1
    
    # After 3 failures, system should be locked
    # Next attempt should fail because we're locked
    assert oracle.membership_query("HELLO AUTH") == False
    
    # Verify we're still locked
    assert oracle.membership_query("HELLO AUTH") == False





# learning tests

@pytest.fixture
def oracle():
    """Create a test mode oracle"""
    return ProtocolOracle(test_mode=True)

@pytest.fixture
def alphabet():
    """Define protocol alphabet"""
    return {'HELLO', 'AUTH', 'DATA', 'CLOSE'}

@pytest.fixture
def learner():
    """Create L* learner"""
    return LStarLearner()

@pytest.fixture
def learned_dfa(oracle, learner, alphabet):
    """Create and return learned DFA"""
    training_data = oracle.generate_training_data()
    learner.initialize(alphabet, training_data, oracle)
    return learner.learn()

def test_protocol_learning(learned_dfa, oracle):
    """
    Test that the L* algorithm correctly learns the protocol behavior.
    """
    # Verify DFA structure
    assert 'states' in learned_dfa
    assert 'initial' in learned_dfa
    assert 'accepting' in learned_dfa
    assert 'transitions' in learned_dfa
    
    # Test DFA against critical protocol sequences
    test_sequences = [
        # Basic sequences
        ("", True),
        ("HELLO", True),
        ("AUTH", False),
        ("DATA", False),
        ("CLOSE", False),
        
        # Valid authentication flow
        ("HELLO AUTH", True),
        ("HELLO AUTH DATA", True),
        ("HELLO AUTH CLOSE", True),
        
        # Invalid sequences
        ("HELLO HELLO", False),
        ("HELLO DATA", False),
        ("DATA HELLO", False),
        ("AUTH HELLO", False),
        
        # Complex valid sequences
        ("HELLO AUTH DATA DATA", True),
        ("HELLO AUTH DATA CLOSE", True),
        ("HELLO AUTH CLOSE HELLO AUTH", True),
        ("HELLO AUTH CLOSE HELLO AUTH DATA", True),
    ]
    
    # Verify each sequence produces expected result
    for sequence, expected in test_sequences:
        dfa_result = run_dfa(learned_dfa, sequence)
        oracle_result = oracle.membership_query(sequence)
        assert dfa_result == oracle_result == expected, \
            f"Sequence '{sequence}' gave DFA:{dfa_result}, Oracle:{oracle_result}, Expected:{expected}"
    
    assert learned_dfa['states'] == 4, "DFA should have exactly 4 states for the protocol"

def test_dfa_state_count(learned_dfa):
    """Test that learned DFA has the expected number of states."""
    assert learned_dfa['states'] == 4, "DFA should have exactly 4 states for the protocol"

def test_dfa_transitions(learned_dfa):
    """Test that learned DFA has correct transitions between states."""
    initial_state = learned_dfa['initial']
    
    # From initial state
    assert ('HELLO' in [sym for (state, sym) in learned_dfa['transitions'].keys() if state == initial_state]), \
        "Initial state should have HELLO transition"
    
    # Find state after HELLO
    ready_state = learned_dfa['transitions'].get((initial_state, 'HELLO'))
    assert ready_state is not None, "Should have transition for HELLO from initial state"
    
    # From ready state
    assert ('AUTH' in [sym for (state, sym) in learned_dfa['transitions'].keys() if state == ready_state]), \
        "Ready state should have AUTH transition"