from lstar.oracle import Oracle
from lstar.lstar_learner import LStarLearner
from lstar.utils import run_dfa
import random

class ProtocolOracle(Oracle):
    def __init__(self, test_mode=False):
        self._state = 'INIT'
        self._retries = 0
        self._authenticated = False
        self._sequence = []
        self._test_mode = test_mode

    def membership_query(self, sequence):
 
        if self._state == 'LOCKED':
            return False
        
        self._state = 'INIT'
        self._authenticated = False
        self._sequence = []
        
        if not sequence:
            # empty string should be accepted
            return True
        
        for action in sequence.split():
            if not self._handle_action(action):
                return False
        return True
        
    def _handle_action(self, action):
        """
        logic:
        1. if action is HELLO and state is INIT, change state to READY, return True
        2. if action is AUTH and state is READY, change state to AUTHENTICATED, return True
        3. if action is DATA and state is AUTHENTICATED, return True
        4. if action is CLOSE and state is AUTHENTICATED, change state to INIT, return True
        5. if action is AUTH and state is not READY, return False
        6. if action is DATA and state is not AUTHENTICATED, return False  
        7. if action is CLOSE and state is not AUTHENTICATED, return False
        8. if action is AUTH and retries is greater than 3, change state to LOCKED, return False
        
        """
        self._sequence.append(action)

        if self._state == 'LOCKED':
            return False
        
        if action == 'HELLO':
            if self._state != 'INIT':
                return False
        
            self._state = 'READY'
            return True
            
        elif action == 'AUTH':
           
            if self._state != 'READY':
                return False
            if self._retries >= 3:
                self._state = 'LOCKED'
                return False
            
            if self._test_mode or random.random() < 0.7:
                self._authenticated = True
                self._state = 'AUTHENTICATED'
                return True
            
            self._retries += 1
            return False
            
        elif action == 'DATA':
            if not self._authenticated:
                return False
            return True
            
        elif action == 'CLOSE':
            if not self._authenticated:
                return False
            
            self._state = 'INIT'
            self._authenticated = False
            return True
            
        return False

    def equivalence_query(self, dfa):
        """Test if the learned DFA is equivalent to our protocol"""
        test_sequences = [
            '',
            'HELLO',
            'AUTH',
            'DATA',
            'CLOSE',
            'HELLO AUTH',
            'HELLO DATA',
            'HELLO AUTH DATA',
            'HELLO AUTH CLOSE',
            'HELLO AUTH DATA CLOSE',
            'HELLO AUTH CLOSE HELLO'
        ]
        
        for test in test_sequences:
            if run_dfa(dfa, test) != self.membership_query(test):
                return test
        return None
        
    def generate_training_data(self, max_length=4):
        actions = ['HELLO', 'AUTH', 'DATA', 'CLOSE']
        positive = set()
        negative = set()
        
        for length in range(1, max_length + 1):
            for _ in range(50):
                sequence = ' '.join(random.choices(actions, k=length))
                if self.membership_query(sequence):
                    positive.add(sequence)
                else:
                    negative.add(sequence)
        
        return {'positive': positive, 'negative': negative}
    

def learn_protocol():
    oracle = ProtocolOracle(test_mode=True)
    learner = LStarLearner()
    
    training_data = oracle.generate_training_data()
    alphabet = {'HELLO', 'AUTH', 'DATA', 'CLOSE'}
    
    learner.initialize(alphabet, training_data, oracle)
    return learner.learn()


if __name__ == "__main__":
    ora = ProtocolOracle(test_mode=True)
    print(ora.membership_query("HELLO AUTH"))
