from src.lstar_learner import LStarLearner
from collections import defaultdict


class OptimizedLStarLearner(LStarLearner):
    def __init__(self):
        super().__init__()
        self.row_cache = {}  # Cache for row signatures

    def initialize(self, alphabet, examples, teacher):
        """Initialize with validation"""
        if not alphabet:
            raise ValueError("Alphabet cannot be empty")
        if not examples['positive'] and not examples['negative']:
            raise ValueError("Must provide at least one example")
        super().initialize(alphabet, examples, teacher)
        
    def _get_row_signature(self, s):
        """Get cached row signature or compute and cache it."""
        if s not in self.row_cache:
            self.row_cache[s] = tuple(self.T[(s, e)] for e in sorted(self.E))
        return self.row_cache[s]
    
    def _is_consistent_optimized(self):
        """Optimized consistency check using row signatures and hash tables."""
        # Map from row signature to list of strings with that signature
        signature_map = defaultdict(list)
        
        # First pass: group strings by their row signatures
        for s in self.S:
            signature = self._get_row_signature(s)
            signature_map[signature].append(s)
            
        # For each group of strings with same signature
        for strings_with_same_sig in signature_map.values():
            if len(strings_with_same_sig) < 2:
                continue
                
            # For each symbol in alphabet
            for a in self.alphabet:
                # Map from extended row signature to first string seen
                extended_sigs = {}
                
                # Check extensions of strings in this group
                for s in strings_with_same_sig:
                    sa = s + a
                    sa_sig = tuple(self.T[(sa, e)] for e in sorted(self.E))
                    
                    if sa_sig in extended_sigs:
                        s_prev = extended_sigs[sa_sig]
                        
                        # Find distinguishing suffix
                        for e in sorted(self.E):
                            if self.T[(s_prev + a, e)] != self.T[(s + a, e)]:
                                return (s_prev, s, a, e)
                    else:
                        extended_sigs[sa_sig] = s
                        
        return None

    def _update_observation_table(self):
        """Update observation table and clear row signature cache."""
        super()._update_observation_table()
        self.row_cache.clear()  # Invalidate cache after table update

    def _handle_counterexample(self, counterexample):
        """Process counterexample and update row signature cache."""
        # Add all prefixes of counterexample to S
        for i in range(len(counterexample) + 1):
            prefix = counterexample[:i]
            if prefix not in self.S:
                self.S.add(prefix)
                self.row_cache.clear()  # Invalidate cache when S changes
        self._update_observation_table()

    def _find_distinguishing_suffix(self, s1, s2, a):
        """Binary search for shortest distinguishing suffix."""
        # Start with existing suffixes
        for e in sorted(self.E, key=len):
            if self.T[(s1 + a, e)] != self.T[(s2 + a, e)]:
                return e
                
        # If no existing suffix distinguishes them, construct new one
        # This could involve additional membership queries
        return None  # Implement based on specific requirements