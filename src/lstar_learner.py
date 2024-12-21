from src.utils import run_dfa

# Description: Implementation of the L* algorithm for learning DFAs.
class LStarLearner:
    def __init__(self):
        self.alphabet = set()
        self.S = set()  # Prefix-closed set of access strings
        self.E = set()  # Suffix-closed set of distinguishing strings
        self.T = {}    # Observation table
        
    def initialize(self, alphabet, examples, teacher):  # Add teacher parameter
        self.alphabet = set(alphabet)
        self.S = {''}
        self.E = {''}
        self.teacher = teacher  # Store the teacher
        self.positive_examples = set(examples['positive'])
        self.negative_examples = set(examples['negative'])
        self._update_observation_table()

    def _membership_query(self, word):
        """Use the teacher's membership query"""
        result = self.teacher.membership_query(word)
        return result
        
    def _update_observation_table(self):
        """Update the observation table T with membership queries."""
        self.T = {}
        # Fill table for S
        for s in self.S:
            for e in self.E:
                self.T[(s, e)] = self._membership_query(s + e)
                
        # Fill table for S·Σ
        for s in self.S:
            for a in self.alphabet:
                sa = s + a
                for e in self.E:
                    self.T[(sa, e)] = self._membership_query(sa + e)

    def _is_closed(self):
        """Check if the observation table is closed."""
        for s in self.S:
            for a in self.alphabet:
                sa = s + a
                sa_row = tuple(self.T[(sa, e)] for e in sorted(self.E))
                found_match = False
                for s_prime in self.S:
                    s_prime_row = tuple(self.T[(s_prime, e)] for e in sorted(self.E))
                    if sa_row == s_prime_row:
                        found_match = True
                        break
                if not found_match:
                    return False, sa
        return True, None
    
    def _is_consistent(self):
        """Check if the observation table is consistent."""
        for s1 in self.S:
            for s2 in self.S:
                if all(self.T[(s1, e)] == self.T[(s2, e)] for e in self.E):
                    for a in self.alphabet:
                        for e in self.E:
                            if self.T[(s1 + a, e)] != self.T[(s2 + a, e)]:
                                return (s1, s2, a, e)
        return None

    def learn(self):
        """Main learning loop of the L* algorithm."""
        while True:
            #self._print_observation_table()
            
            # Check if table is closed
            closed, unclosed_string = self._is_closed()
            if not closed:
                self.S.add(unclosed_string)
                self._update_observation_table()
                continue
            
            # Check if table is consistent
            inconsistency = self._is_consistent()
            if inconsistency:
                s1, s2, a, e = inconsistency
                self.E.add(a + e)
                self._update_observation_table()
                continue
            
            # Construct and return hypothesis DFA
            dfa = self._construct_dfa()
            if self._is_correct(dfa):
                return dfa
        
    
                
            
    def _construct_dfa(self):
        """Construct a DFA from the observation table."""
        states = {tuple(self.T[(s, e)] for e in sorted(self.E)) for s in self.S}
        initial_state = tuple(self.T[('', e)] for e in sorted(self.E))
        state_map = {state: i for i, state in enumerate(states)}
        
        transitions = {}
        # Build transitions with more debug info
        for s in self.S:
            current_state = tuple(self.T[(s, e)] for e in sorted(self.E))
            for a in self.alphabet:
                next_state = tuple(self.T[(s + a, e)] for e in sorted(self.E))
                transitions[(state_map[current_state], a)] = state_map[next_state]
              
        accepting = set()
        # Determine accepting states
        for state in states:
            if state[0]:  # Use empty string from E set to determine acceptance
                accepting.add(state_map[state])
        
        return {
            'states': len(states),
            'initial': state_map[initial_state],
            'accepting': accepting,
            'transitions': transitions
        }
    
    def _is_correct(self, dfa):
        """Check if the constructed DFA is correct for all examples."""
        for pos in self.positive_examples:
            if not run_dfa(dfa, pos):
                return False
        for neg in self.negative_examples:
            if run_dfa(dfa, neg):
                return False
        return True
    

    def _print_observation_table(self):
        """Print the observation table in a readable format"""
        print("\nObservation Table:")
        print("E =", sorted(self.E))
        print("S:", sorted(self.S))
        print("S·Σ:", sorted(s + a for s in self.S for a in self.alphabet))
        
        # Header
        print("\n   ", end="")
        for e in sorted(self.E):
            print(f"{e or 'ε':4}", end="")
        print()
        
        # Rows for S
        for s in sorted(self.S):
            print(f"{s or 'ε':3}", end="")
            for e in sorted(self.E):
                print(f"{str(self.T[(s, e)]):4}", end="")
            print()
            
        # Rows for S·Σ
        for s in sorted(self.S):
            for a in sorted(self.alphabet):
                print(f"{s+a:3}", end="")
                for e in sorted(self.E):
                    print(f"{str(self.T[(s+a, e)]):4}", end="")
                print()
        
