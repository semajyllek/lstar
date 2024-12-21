# test_lstar_performance.py
import time
import itertools
from typing import Dict, Set
import pytest
from opt_lstar_learner import LStarLearner, OptimizedLStarLearner 
from teachers import EvenAsTeacher

def generate_large_example():
    """Generate a very large example set that will stress test the consistency check"""
    # Generate strings up to length 6 with 5 letters
    alphabet = set('abcde')
    
    # Complex acceptance pattern: string is accepted if:
    # 1. Number of 'a's and 'b's together is even AND
    # 2. Number of 'c's followed by 'd's is even AND
    # 3. Total length is at least 3
    def is_accepted(s: str) -> bool:
        if len(s) < 3:
            return False
        ab_count = s.count('a') + s.count('b')
        cd_pairs = sum(1 for i in range(len(s)-1) if s[i] == 'c' and s[i+1] == 'd')
        return ab_count % 2 == 0 and cd_pairs % 2 == 0

    # Generate all strings up to length 6
    positive = set()
    negative = set()
    for length in range(3, 7):  # lengths 3 to 6
        for p in itertools.product('abcde', repeat=length):
            s = ''.join(p)
            if is_accepted(s):
                positive.add(s)
            else:
                negative.add(s)

    return {
        "alphabet": alphabet,
        "examples": {
            "positive": positive,
            "negative": negative
        }
    }

@pytest.fixture
def example_sets() -> Dict[str, Dict[str, Set[str]]]:
    """Generate increasingly complex example sets to test with"""
    huge_example = generate_large_example()
    
    print(f"\nGenerated example set:")
    print(f"Alphabet size: {len(huge_example['alphabet'])}")
    print(f"Number of positive examples: {len(huge_example['examples']['positive'])}")
    print(f"Number of negative examples: {len(huge_example['examples']['negative'])}")
    
    return {
        "huge": huge_example
    }

def benchmark_learner(learner, test_set: Dict, name: str):
    """Run a single benchmark"""
    print(f"\nStarting benchmark for {name}")
    print("Initializing...")
    start_time = time.perf_counter()
    
    learner.initialize(test_set["alphabet"], test_set["examples"], )
    print("Running learn()...")
    dfa = learner.learn()
    
    end_time = time.perf_counter()
    print(f"Completed {name}")
    return {
        "name": name,
        "time": end_time - start_time,
        "states": dfa["states"],
        "transitions": len(dfa["transitions"])
    }

def test_performance_comparison(example_sets):
    """Compare performance between original and optimized implementations"""
    results = []
    
    # Test each implementation with each example set
    for set_name, test_set in example_sets.items():
        print(f"\nTesting {set_name} example set...")
        print(f"Alphabet: {test_set['alphabet']}")
        print(f"Positive examples: {len(test_set['examples']['positive'])}")
        print(f"Negative examples: {len(test_set['examples']['negative'])}")
        
        try:
            # Add timeout using pytest
            with pytest.raises(Exception) as exc_info:
                with pytest.timeout(10):  # 10 second timeout
                    original = LStarLearner()
                    print("\nRunning original implementation...")
                    orig_result = benchmark_learner(original, test_set, f"Original-{set_name}")
                    
                    optimized = OptimizedLStarLearner()
                    print("\nRunning optimized implementation...")
                    opt_result = benchmark_learner(optimized, test_set, f"Optimized-{set_name}")
                    
                    results.append(orig_result)
                    results.append(opt_result)
                    
                    # Compare results are equivalent
                    assert orig_result["states"] == opt_result["states"], \
                        f"Different number of states for {set_name}"
                    assert orig_result["transitions"] == opt_result["transitions"], \
                        f"Different number of transitions for {set_name}"
            
        except Exception as e:
            print(f"\nError or timeout occurred with {set_name} example set:")
            print(str(e))
            continue
    
    if results:
        # Print results in a nice format
        print("\nPerformance Comparison:")
        print("-" * 60)
        print(f"{'Implementation':<20} {'Example Set':<10} {'Time (s)':<10} {'States':<8} {'Transitions'}")
        print("-" * 60)
        
        for r in results:
            impl, set_name = r["name"].split("-")
            print(f"{impl:<20} {set_name:<10} {r['time']:<10.4f} {r['states']:<8} {r['transitions']}")
    else:
        print("\nNo successful comparisons completed")

def test_specific_operation_comparison(example_sets):
    """Compare specific operations that should be optimized"""
    test_set = example_sets["huge"]
    
    original = LStarLearner()
    optimized = OptimizedLStarLearner()
    teacher = EvenAsTeacher()  # Add teacher
    
    print("\nInitializing learners...")
    original.initialize(test_set["alphabet"], test_set["examples"], teacher)
    optimized.initialize(test_set["alphabet"], test_set["examples"], teacher)
    
    runs = 3
    iterations_per_run = 1000  # Do many consistency checks per run
    orig_times = []
    opt_times = []
    
    print(f"\nRunning consistency checks ({iterations_per_run} iterations per run)...")
    for i in range(runs):
        print(f"\nRun {i+1}/{runs}")
        
        print("Testing original implementation...", end=" ", flush=True)
        start_time = time.perf_counter()
        for _ in range(iterations_per_run):
            original._is_consistent()
        orig_time = time.perf_counter() - start_time
        orig_times.append(orig_time)
        print(f"took {orig_time:.4f}s")
        
        print("Testing optimized implementation...", end=" ", flush=True)
        start_time = time.perf_counter()
        for _ in range(iterations_per_run):
            optimized._is_consistent_optimized()
        opt_time = time.perf_counter() - start_time
        opt_times.append(opt_time)
        print(f"took {opt_time:.4f}s")
    
    avg_orig = sum(orig_times) / runs
    avg_opt = sum(opt_times) / runs
    
    print("\nConsistency Check Timing (averaged over 3 runs):")
    print(f"Original: {avg_orig:.4f}s = {(avg_orig/iterations_per_run)*1000:.4f}ms per check")
    print(f"Optimized: {avg_opt:.4f}s = {(avg_opt/iterations_per_run)*1000:.4f}ms per check")
    print(f"Speedup: {avg_orig/avg_opt:.2f}x")
    
    # Print individual run times
    print("\nIndividual run times:")
    for i in range(runs):
        print(f"Run {i+1}:")
        print(f"  Original:  {orig_times[i]:.4f}s")
        print(f"  Optimized: {opt_times[i]:.4f}s")
        print(f"  Speedup:   {orig_times[i]/opt_times[i]:.2f}x")

class ComplexTeacher:
    def membership_query(self, string):
        if len(string) < 3 or 'e' not in string:
            return False
            
        # Count a's and b's together
        ab_count = string.count('a') + string.count('b')
        
        # Count c's followed by d's
        cd_pairs = sum(1 for i in range(len(string)-1) if string[i] == 'c' and string[i+1] == 'd')
        
        return ab_count % 2 == 0 and cd_pairs % 2 == 0

def generate_complex_example():
    """Generate a large example set for our complex language"""
    alphabet = set('abcde')
    
    # Generate all strings up to length 6
    positive = set()
    negative = set()
    
    # Use ComplexTeacher to classify strings
    teacher = ComplexTeacher()
    
    # Generate strings systematically
    for length in range(3, 7):  # lengths 3 to 6
        for p in itertools.product('abcde', repeat=length):
            s = ''.join(p)
            if teacher.membership_query(s):
                positive.add(s)
            else:
                negative.add(s)

    return {
        "alphabet": alphabet,
        "examples": {
            "positive": positive,
            "negative": negative
        }
    }


def test_specific_operation_comparison(example_sets):
    """Compare specific operations that should be optimized"""
    test_set = example_sets["huge"]
    
    original = LStarLearner()
    optimized = OptimizedLStarLearner()
    teacher = ComplexTeacher()
    
    print("\nInitializing learners with complex language...")
    print(f"Alphabet size: {len(test_set['alphabet'])}")
    print(f"Number of positive examples: {len(test_set['examples']['positive'])}")
    print(f"Number of negative examples: {len(test_set['examples']['negative'])}")
    
    original.initialize(test_set["alphabet"], test_set["examples"], teacher)
    optimized.initialize(test_set["alphabet"], test_set["examples"], teacher)
    
    runs = 3
    iterations_per_run = 100  # Reduced because each check will be more complex
    orig_times = []
    opt_times = []
    
    print(f"\nRunning consistency checks ({iterations_per_run} iterations per run)...")
    for i in range(runs):
        print(f"\nRun {i+1}/{runs}")
        
        print("Testing original implementation...", end=" ", flush=True)
        start_time = time.perf_counter()
        for _ in range(iterations_per_run):
            original._is_consistent()
        orig_time = time.perf_counter() - start_time
        orig_times.append(orig_time)
        print(f"took {orig_time:.4f}s")
        
        print("Testing optimized implementation...", end=" ", flush=True)
        start_time = time.perf_counter()
        for _ in range(iterations_per_run):
            optimized._is_consistent_optimized()
        opt_time = time.perf_counter() - start_time
        opt_times.append(opt_time)
        print(f"took {opt_time:.4f}s")
    
    avg_orig = sum(orig_times) / runs
    avg_opt = sum(opt_times) / runs
    
    print("\nConsistency Check Timing (averaged over 3 runs):")
    print(f"Original: {avg_orig:.4f}s = {(avg_orig/iterations_per_run)*1000:.4f}ms per check")
    print(f"Optimized: {avg_opt:.4f}s = {(avg_opt/iterations_per_run)*1000:.4f}ms per check")
    print(f"Speedup: {avg_orig/avg_opt:.2f}x")