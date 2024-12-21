import pytest
from src.utils import run_dfa
from itertools import product
from src.teachers import EvenAsTeacher, EndsInABTeacher, NoThreeAsTeacher
from src.opt_lstar_learner import OptimizedLStarLearner

# Fixtures for our teachers
@pytest.fixture
def even_as_teacher():
   return EvenAsTeacher()

@pytest.fixture
def ends_in_ab_teacher():
   return EndsInABTeacher()

@pytest.fixture
def no_three_as_teacher():
   return NoThreeAsTeacher()

@pytest.fixture
def learner():
   return OptimizedLStarLearner()

# Test membership queries
@pytest.mark.parametrize("input_string,expected", [
   ("", True),      # Empty string has 0 a's
   ("a", False),    # Single a
   ("aa", True),    # Two a's
   ("bab", False),  # One a 
   ("abba", True),  # Two a's with b's between
])
def test_even_as_membership(even_as_teacher, input_string, expected):
   assert even_as_teacher.membership_query(input_string) == expected

@pytest.mark.parametrize("input_string,expected", [
   ("", False),
   ("a", False),
   ("b", False),
   ("ab", True),
   ("ba", False),
   ("bab", True),
   ("aba", False),
])
def test_ends_in_ab_membership(ends_in_ab_teacher, input_string, expected):
   assert ends_in_ab_teacher.membership_query(input_string) == expected

@pytest.mark.parametrize("input_string,expected", [
   ("", True),
   ("aa", True),
   ("aaa", False),
   ("baba", True),
   ("baaab", False),
])
def test_no_three_as_membership(no_three_as_teacher, input_string, expected):
   assert no_three_as_teacher.membership_query(input_string) == expected

# Test full learning process
def test_learn_even_as(learner, even_as_teacher):
   alphabet = {'a', 'b'}
   examples = {
       'positive': {'', 'aa', 'abba'},
       'negative': {'a', 'aaa'}
   }
   
   learner.initialize(alphabet, examples, even_as_teacher)
   dfa = learner.learn()
   
   test_cases = [
       ('', True),
       ('a', False),
       ('aa', True),
       ('aaa', False),
       ('aaaa', True),
       ('b', True),
       ('ab', False),
       ('aba', True),
       ('abaa', False)
   ]
   
   for string, expected in test_cases:
       assert run_dfa(dfa, string) == expected, f"Failed for input: {string}"

# Test DFA properties
def test_dfa_structure(learner, even_as_teacher):
   alphabet = {'a', 'b'}
   examples = {
       'positive': {'', 'aa'},
       'negative': {'a'}
   }
   
   learner.initialize(alphabet, examples, even_as_teacher)
   dfa = learner.learn()
   
   # Check DFA has required components
   assert all(key in dfa for key in ['states', 'initial', 'accepting', 'transitions'])
   assert dfa['initial'] < dfa['states']
   
   # Check transitions
   for (state, symbol), next_state in dfa['transitions'].items():
       assert state < dfa['states']
       assert next_state < dfa['states']
       assert symbol in alphabet

# Test teacher consistency
def test_teacher_consistency(even_as_teacher, ends_in_ab_teacher, no_three_as_teacher):
   teachers = [
       (even_as_teacher, "even as"),
       (ends_in_ab_teacher, "ends in ab"),
       (no_three_as_teacher, "no three as")
   ]
   
   # Generate test strings up to length 3
   test_strings = [''.join(p) for l in range(4) 
                  for p in product('ab', repeat=l)]
   
   for teacher, name in teachers:
       for test_string in test_strings:
           result1 = teacher.membership_query(test_string)
           result2 = teacher.membership_query(test_string)
           assert result1 == result2, f"{name} inconsistent for '{test_string}'"

# Error cases
def test_invalid_alphabet(learner, even_as_teacher):
   with pytest.raises(ValueError):
       learner.initialize({}, {'positive': {'aa'}, 'negative': {'a'}}, even_as_teacher)

def test_invalid_examples(learner, even_as_teacher):
   with pytest.raises(ValueError):
       learner.initialize({'a', 'b'}, {'positive': set(), 'negative': set()}, even_as_teacher)

# Performance test
@pytest.mark.timeout(2.0)
def test_learning_performance(learner, even_as_teacher):
   alphabet = {'a', 'b'}
   examples = {
       'positive': {'', 'aa', 'abba'},
       'negative': {'a', 'aaa'}
   }
   
   learner.initialize(alphabet, examples, even_as_teacher)
   dfa = learner.learn()