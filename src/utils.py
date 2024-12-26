def run_dfa(dfa, input_string):
    """Run DFA on input treating it as a sequence of tokens."""
    # Start at initial state
    current_state = dfa['initial']
    
    # Handle empty string case
    if not input_string:
        return current_state in dfa['accepting']
        
    # Split input into tokens if it contains spaces
    tokens = input_string.split() if ' ' in input_string else [input_string]
    
    # Process each token
    for token in tokens:
        if (current_state, token) not in dfa['transitions']:
            return False
        current_state = dfa['transitions'][(current_state, token)]
        
    return current_state in dfa['accepting']