def run_dfa(dfa, input_string):
    current_state = dfa['initial']
    for symbol in input_string:
        if (current_state, symbol) not in dfa['transitions']:
            return False
        current_state = dfa['transitions'][(current_state, symbol)]
    return current_state in dfa['accepting']