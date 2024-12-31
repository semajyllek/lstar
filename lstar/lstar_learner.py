from typing import Optional, Tuple, Set, Dict
import logging
from .utils import run_dfa
from collections import defaultdict

logger = logging.getLogger(__name__)


MAX_ITERATIONS = 5
class LStarLearner:
    def __init__(self):
        self.S: Set[str] = set()
        self.E: Set[str] = set()
        self.T: Dict[Tuple[str, str], bool] = {}
        self.alphabet: Set[str] = set()
        self.teacher = None
        self.positive_examples: Set[str] = set()
        self.negative_examples: Set[str] = set()
        self._signature_cache: Dict[str, tuple] = {}

        
    def _get_sa_rows(self):
        """Get all rows that are in S·Σ but not in S."""
        sa_rows = set()
        for s in sorted(self.S):
            for a in sorted(self.alphabet):
                sa = f"{s} {a}".strip()
                if sa not in self.S:
                    sa_rows.add(sa)
        return sorted(sa_rows)


    def debug_step(self, iteration):
        """Log debug information for current learning step."""
        logger.debug(f"Iteration {iteration}:")
        logger.debug(f"S = {sorted(self.S)}")
        logger.debug(f"E = {sorted(self.E)}")
        logger.debug(f"Alphabet = {sorted(self.alphabet)}")
        self.print_observation_table()


    def print_observation_table(self):
        """Log observation table in a formatted way."""
        # Get all prefixes and experiments
        s_rows = sorted(self.S)
        sa_rows = self._get_sa_rows()
        sorted_experiments = sorted(self.E)
        
        # Calculate column widths
        prefix_width = max(
            max((len(s) for s in s_rows + sa_rows), default=2),
            len("Prefix")
        )
        col_widths = {}
        for e in sorted_experiments:
            e_display = e if e else "ε"
            col_widths[e] = max(len(e_display), 5)
        
        # Build table as string
        table = []
        
        # Header
        header = f"{'Prefix':<{prefix_width}}│"
        header += "│".join(f"{e if e else 'ε':^{col_widths[e]}}" for e in sorted_experiments)
        table.append("┌" + "─" * prefix_width + "┬" + "┬".join("─" * width for width in col_widths.values()) + "┐")
        table.append(header)
        table.append("├" + "─" * prefix_width + "┼" + "┼".join("─" * width for width in col_widths.values()) + "┤")
        
        # S rows
        for s in s_rows:
            row = f"{s if s else 'ε':<{prefix_width}}│"
            row_sig = self._get_row_signature(s)
            row += "│".join(f"{str(row_sig[i]):^{col_widths[e]}}" for i, e in enumerate(sorted_experiments))
            table.append(row)
            
        # Separator before S·Σ rows
        if sa_rows:
            table.append("├" + "─" * prefix_width + "┼" + "┼".join("─" * width for width in col_widths.values()) + "┤")
            
        # S·Σ rows
        for sa in sa_rows:
            row = f"{sa:<{prefix_width}}│"
            row_sig = self._get_row_signature(sa)
            row += "│".join(f"{str(row_sig[i]):^{col_widths[e]}}" for i, e in enumerate(sorted_experiments))
            table.append(row)
            
        # Bottom border
        table.append("└" + "─" * prefix_width + "┴" + "┴".join("─" * width for width in col_widths.values()) + "┘")
        
        # Log the entire table
        logger.debug("\nObservation Table:\n" + "\n".join(table))

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
    

    def _get_row_signature(self, s: str) -> tuple:
        """Get signature for a row, using cache."""
        if s not in self._signature_cache:
            sig = tuple(self.T[(s, e)] for e in sorted(self.E))
            self._signature_cache[s] = sig
        return self._signature_cache[s]
    

    def _verify_hypothesis(self, dfa: dict) -> Optional[str]:
        """Verify DFA hypothesis against examples and teacher."""
        # First check examples
        for pos in self.positive_examples:
            if not run_dfa(dfa, pos):
                return pos
        
        for neg in self.negative_examples:
            if run_dfa(dfa, neg):
                return neg
                
        # Then do equivalence query
        counterexample = self.teacher.equivalence_query(dfa)
        if counterexample is not None:
            # Verify counterexample is actually distinguishing
            oracle_result = self.teacher.membership_query(counterexample)
            dfa_result = run_dfa(dfa, counterexample)
            if oracle_result == dfa_result:
                raise Exception(f"Invalid counterexample {counterexample}: DFA and oracle agree")
        
        return counterexample
    

    def _add_all_prefixes(self, tokens: list) -> None:
        """Add all prefixes from a list of tokens to S."""
        prefix = ""
        for token in tokens:
            prefix = f"{prefix} {token}".strip()
            if prefix:  # Don't add empty string
                self.S.add(prefix)


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


    def _check_table_properties(self) -> Optional[str]:
        """
        Check if observation table is closed and consistent.
        Returns None if table is good, otherwise returns the counterexample.
        """
        # Check if table is closed
        closed, unclosed_row = self._is_closed()
        if not closed:
            if isinstance(unclosed_row, str):  # Make sure we only add strings to S
                self.S.add(unclosed_row)
                self._update_observation_table()
                logger.info(f"Table not closed, adding {unclosed_row}")
                return unclosed_row
        
        # Check if table is consistent
        inconsistency = self._is_consistent()
        if inconsistency:
            s1, s2, a, e = inconsistency
            new_suffix = f"{a} {e}".strip()
            self.E.add(new_suffix)
            self._update_observation_table()
            logger.info(f"Table not consistent, adding {new_suffix} to E")
            return new_suffix
            
        return None


    def _is_closed(self) -> tuple:
        """Check if table is closed.
        Returns (True, None) if closed, (False, sa) if sa is in S·Σ but its signature doesn't appear in S"""
        # Get signatures of S rows
        s_signatures = {self._get_row_signature(s) for s in self.S}
        
        # Check each row in S·Σ
        for s in self.S:
            for a in sorted(self.alphabet):
                sa = f"{s} {a}".strip()
                if sa in self.S:
                    continue
                sa_sig = self._get_row_signature(sa)
                if sa_sig not in s_signatures:
                    return False, sa
        return True, None


    def _add_counterexample_info(self, counterexample: str) -> None:
        """Process counterexample by adding all prefixes to S and all suffixes to E."""
        if not counterexample:
            return
            
        tokens = counterexample.split()
        
        # Add all prefixes to S
        prefix = ""
        for token in tokens:
            prefix = f"{prefix} {token}".strip()
            self.S.add(prefix)
            
        # Add all suffixes to E
        for i in range(len(tokens)):
            suffix = ' '.join(tokens[i:])
            if suffix:
                self.E.add(suffix)
        
        self._update_observation_table()
        self._signature_cache.clear()


    def learn(self) -> dict:
        """Main learning loop."""
        max_iterations = 100
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Debug output
            self.debug_step(iteration)
            
            # Update table properties if needed
            table_counterexample = self._check_table_properties()
            if table_counterexample:
                logger.info(f"Table property violation found: {table_counterexample}")
                continue
            
            # Construct and verify hypothesis
            dfa = self._construct_dfa()
            counterexample = self._verify_hypothesis(dfa)
            
            if counterexample is None:
                logger.info("Learning completed successfully!")
                self.debug_step(iteration)
                return dfa
                
            logger.info(f"Counterexample found: {counterexample}")
            self._add_counterexample_info(counterexample)
            
        raise Exception(f"Learning did not converge after {max_iterations} iterations")
            
    
    def initialize(self, alphabet: Set[str], examples: Dict[str, Set[str]], teacher) -> None:
        """
        Initialize the learner.
        
        Args:
            alphabet: Set of symbols in the language
            examples: Dictionary with 'positive' and 'negative' example sets
            teacher: Oracle that can answer membership queries
            strategy: Optional counterexample processing strategy
        """

   
        if not alphabet:
            raise ValueError("Alphabet cannot be empty")
        if not examples['positive'] and not examples['negative']:
            raise ValueError("Must provide at least one example")
            
        self.alphabet = set(alphabet)
        self.S = {''}
        self.E = {''}
        self.T = {}
        self.teacher = teacher
        self.positive_examples = set(examples['positive'])
        self.negative_examples = set(examples['negative'])
        self._signature_cache = {}
        self._update_observation_table()