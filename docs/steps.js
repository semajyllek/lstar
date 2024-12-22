// Example learning steps for "even number of a's" language
const learning_steps = [
	{
        step: "Initial State",
        description: "Start with empty sets S and E, then make initial membership queries.",
        membershipQueries: [
            { input: "", result: true, explanation: "Empty string has 0 a's (even)" },
            { input: "a", result: false, explanation: "Single 'a' (odd)" },
            { input: "b", result: true, explanation: "No a's (even)" }
        ],
        S: [''],
        E: [''],
        table: {
            '': { '': true },
            'a': { '': false },
            'b': { '': true }
        },
        dfa: {
            states: 1,
            initial: 0,
            accepting: [0],
            transitions: {}
        }
    },
    {
        step: "Table Not Closed",
        description: "Row for 'a' is different from all rows in S, add 'a' to S",
        S: ['', 'a'],
        E: [''],
        table: {
            '': { '': true },
            'a': { '': false },
            'b': { '': true },
            'aa': { '': true },
            'ab': { '': false }
        },
        dfa: {
            states: 2,
            initial: 0,
            accepting: [0],
            transitions: {
                '0,a': 1,
                '0,b': 0
            }
        }
    },
    {
        step: "Building DFA",
        description: "Table is closed and consistent. Construct DFA with two states.",
        S: ['', 'a'],
        E: [''],
        table: {
            '': { '': true },
            'a': { '': false },
            'b': { '': true },
            'aa': { '': true },
            'ab': { '': false }
        },
        dfa: {
            states: 2,
            initial: 0,
            accepting: [0],
            transitions: {
                '0,a': 1,
                '0,b': 0,
                '1,a': 0,
                '1,b': 1
            }
        }
    },
	{
        step: "Testing Hypothesis DFA",
        description: "Testing our DFA with string 'aba'. The teacher provides this as a counterexample.",
        membershipQueries: [
            { input: "aba", result: false, explanation: "Has odd number of a's but DFA accepts it" }
        ],
        counterexample: "aba",
        S: ['', 'a'],
        E: ['a'],  // Added 'a' as distinguishing suffix
        table: {
            '': { '': true, 'a': false },
            'a': { '': false, 'a': true },
            'b': { '': true, 'a': false },
            'aa': { '': true, 'a': false },
            'ab': { '': false, 'a': false }
        },
        dfa: {
            states: 2,
            initial: 0,
            accepting: [0],
            transitions: {
                '0,a': 1,
                '0,b': 0,
                '1,a': 0,
                '1,b': 1
            }
        }
    }
];

export default learning_steps;