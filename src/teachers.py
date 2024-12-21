from src.utils import run_dfa
import itertools

class EvenAsTeacher:
    def membership_query(self, string):
        return string.count('a') % 2 == 0
        
    def equivalence_query(self, dfa):
        test_cases = ['', 'a', 'aa', 'aaa', 'aaaa', 'b', 'ab', 'ba', 'baa']
        for test in test_cases:
            if run_dfa(dfa, test) != self.membership_query(test):
                return test
        return None
    


class EndsInABTeacher:
    def membership_query(self, string):
        return string.endswith('ab')
        
    def equivalence_query(self, dfa):
        # Test key cases
        test_cases = ['', 'a', 'b', 'ab', 'ba', 'bab', 'aba', 'aab']
        for test in test_cases:
            if run_dfa(dfa, test) != self.membership_query(test):
                return test
        return None
    

class NoThreeAsTeacher:
    def membership_query(self, string):
        return 'aaa' not in string
        
    def equivalence_query(self, dfa):
        # Generate strings systematically
        for length in range(4):
            for combo in itertools.product('ab', repeat=length):
                test = ''.join(combo)
                if run_dfa(dfa, test) != self.membership_query(test):
                    return test
        return None