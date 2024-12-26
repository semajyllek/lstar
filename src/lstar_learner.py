from collections import defaultdict
from .utils import run_dfa

class LStarLearner:
    def initialize(self, alphabet, examples, teacher):
        """Initialize with alphabet and examples. All inputs are assumed to be space-separated tokens."""
        if not alphabet:
            raise ValueError("Alphabet cannot be empty")
        if not examples['positive'] and not examples['negative']:
            raise ValueError("Must provide at least one example")
            
        self.alphabet = set(alphabet)
        self.S = {''}  # Include empty string
        self.E = {''}  # Include empty string
        self.T = {}    # Observation table
        self.teacher = teacher
        self.positive_examples = set(examples['positive'])
        self.negative_examples = set(examples['negative'])
        self._signature_cache = {}
        self._update_observation_table()


    def _update_observation_table(self):
        """Update the observation table and clear signature cache."""
        self._signature_cache.clear()
        self.T = {}
        
        # Fill table for S
        for s in self.S:
            for e in self.E:
                seq = f"{s} {e}".strip()
                self.T[(s, e)] = self.teacher.membership_query(seq)
                
        # Fill table for S·Σ
        for s in self.S:
            for a in self.alphabet:
                sa = f"{s} {a}".strip()
                for e in self.E:
                    seq = f"{sa} {e}".strip()
                    self.T[(sa, e)] = self.teacher.membership_query(seq)

    def _get_row_signature(self, s: str) -> tuple:
        """Get signature for a row, using cache."""
        if s not in self._signature_cache:
            sig = tuple(self.T[(s, e)] for e in sorted(self.E))
            self._signature_cache[s] = sig
        return self._signature_cache[s]

    def _is_closed(self) -> tuple:
        """Check if table is closed."""
        s_signatures = {self._get_row_signature(s) for s in self.S}
        
        for s in self.S:
            for a in sorted(self.alphabet):
                sa = f"{s} {a}".strip()
                sa_sig = self._get_row_signature(sa)
                if sa_sig not in s_signatures:
                    return False, sa
        return True, None

    def _is_consistent(self) -> tuple:
        """Check if table is consistent."""
        # Group rows by their signatures
        sig_to_strings = defaultdict(list)
        for s in self.S:
            sig = self._get_row_signature(s)
            sig_to_strings[sig].append(s)

        # Check each group with same signature
        for strings_with_same_sig in sig_to_strings.values():
            if len(strings_with_same_sig) < 2:
                continue

            # Check consistency for each alphabet symbol
            for a in sorted(self.alphabet):
                extended_sigs = {}
                for s in strings_with_same_sig:
                    sa = f"{s} {a}".strip()
                    sa_sig = self._get_row_signature(sa)
                    
                    if sa_sig in extended_sigs:
                        s_prev = extended_sigs[sa_sig]
                        for e in sorted(self.E):
                            if self.T[(sa, e)] != self.T[f"{s_prev} {a}".strip(), e]:
                                return s_prev, s, a, e
                    else:
                        extended_sigs[sa_sig] = s
                        
        return None

    def _construct_dfa(self) -> dict:
        """Construct DFA from observation table."""
        # Get unique states from row signatures
        state_sigs = {self._get_row_signature(s) for s in self.S}
        initial_sig = self._get_row_signature('')
        state_map = {sig: i for i, sig in enumerate(state_sigs)}
        
        # Build transitions
        transitions = {}
        for s in self.S:
            current_sig = self._get_row_signature(s)
            for a in self.alphabet:
                sa = f"{s} {a}".strip()
                next_sig = self._get_row_signature(sa)
                transitions[(state_map[current_sig], a)] = state_map[next_sig]

        # Determine accepting states
        accepting = {state_map[sig] for sig in state_sigs if sig[0]}  # Use empty string result
        
        return {
            'states': len(state_sigs),
            'initial': state_map[initial_sig],
            'accepting': accepting,
            'transitions': transitions
        }

    def _add_counterexample_info(self, counterexample: str) -> None:
        """Add information from counterexample to table."""
        if not counterexample:
            return

        # Split into tokens
        tokens = counterexample.split()
        
        # Add all prefixes to S
        prefix = ""
        for token in tokens:
            prefix = f"{prefix} {token}".strip()
            if prefix:  # Don't add empty string, it's already in S
                self.S.add(prefix)
        
        # Add all suffixes to E
        for i in range(len(tokens)):
            suffix = ' '.join(tokens[i:])
            if suffix:
                self.E.add(suffix)
        
        self._update_observation_table()

    def learn(self) -> dict:
        """Main learning loop."""
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Check if table is closed
            closed, unclosed_row = self._is_closed()
            if not closed:
                self.S.add(unclosed_row)
                self._update_observation_table()
                continue
            
            # Check if table is consistent
            inconsistency = self._is_consistent()
            if inconsistency:
                s1, s2, a, e = inconsistency
                new_suffix = f"{a} {e}".strip()
                self.E.add(new_suffix)
                self._update_observation_table()
                continue
            
            # Construct and verify DFA
            dfa = self._construct_dfa()
            
            # Check against examples
            all_correct = True
            counterexample = None
            
            for pos in self.positive_examples:
                if not run_dfa(dfa, pos):
                    counterexample = pos
                    all_correct = False
                    break
                    
            if all_correct:
                for neg in self.negative_examples:
                    if run_dfa(dfa, neg):
                        counterexample = neg
                        all_correct = False
                        break
            
            if all_correct:
                return dfa
            
            # Handle counterexample
            self._add_counterexample_info(counterexample)
            
        raise Exception(f"Learning did not converge after {max_iterations} iterations")