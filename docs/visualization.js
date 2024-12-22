const { useState, useEffect } = React;


const Tooltip = ({ children, content }) => {
    const [show, setShow] = useState(false);
    return (
        <div className="relative inline-block">
            <div 
                onMouseEnter={() => setShow(true)}
                onMouseLeave={() => setShow(false)}
                className="underline cursor-help"
            >
                {children}
            </div>
            {show && (
                <div className="absolute z-10 w-64 px-3 py-2 text-sm font-normal text-left text-gray-700 bg-white border rounded-lg shadow-lg bottom-full left-1/2 transform -translate-x-1/2 mb-2">
                    {content}
                </div>
            )}
        </div>
    );
};


const TableExplanation = ({ isVisible, onClose }) => {
    if (!isVisible) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="bg-white p-6 rounded-lg max-w-2xl">
                <h2 className="text-2xl font-bold mb-4">Understanding the Observation Table</h2>
                
                <div className="space-y-4">
                    <div className="border p-4 rounded">
                        <h3 className="font-bold">Structure:</h3>
                        <div className="flex mt-2">
                            <table className="border-collapse">
                                <tr>
                                    <td className="border p-2 bg-blue-100">S/E</td>
                                    <td className="border p-2 bg-green-100">ε</td>
                                </tr>
                                <tr>
                                    <td className="border p-2 bg-blue-100">ε</td>
                                    <td className="border p-2">T</td>
                                </tr>
                                <tr>
                                    <td className="border p-2 bg-yellow-100">a</td>
                                    <td className="border p-2">F</td>
                                </tr>
                                <tr>
                                    <td className="border p-2 bg-yellow-100">b</td>
                                    <td className="border p-2">T</td>
                                </tr>
                            </table>
                            <div className="ml-4 space-y-2">
                                <div className="flex items-center">
                                    <div className="w-4 h-4 bg-blue-100 mr-2"></div>
                                    <span>S: Prefix strings (starts with empty string ε)</span>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-4 h-4 bg-green-100 mr-2"></div>
                                    <span>E: Suffix strings (experiments)</span>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-4 h-4 bg-yellow-100 mr-2"></div>
                                    <span>S·Σ: Testing each prefix with each alphabet symbol</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="border p-4 rounded">
                        <h3 className="font-bold">How to read it:</h3>
                        <ul className="list-disc ml-4 space-y-2">
                            <li>Each cell shows whether a string is accepted (T) or rejected (F)</li>
                            <li>Each row represents a prefix (from S or S·Σ)</li>
                            <li>Each column represents a suffix (from E)</li>
                            <li>The value in each cell is: prefix + suffix = accepted?</li>
                        </ul>
                    </div>

                    <button 
                        onClick={onClose}
                        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Got it!
                    </button>
                </div>
            </div>
        </div>
    );
};




const ObservationTable = ({ 
    currentStep, 
    onShowExplanation 
}) => {
    return (
        <div className="bg-white p-4 rounded shadow">
            <div className="flex justify-between items-center mb-2">
                <h3 className="font-bold">Observation Table</h3>
                <button 
                    onClick={onShowExplanation}
                    className="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
                >
                    How to read this table?
                </button>
            </div>
            <div className="overflow-x-auto">
                <table className="min-w-full border-collapse">
                    <thead>
                        <tr>
                            <th className="border p-2 bg-blue-50">S/E</th>
                            {currentStep.E.map(e => (
                                <th key={e} className="border p-2 bg-green-50">
                                    {e || 'ε'}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {/* S rows */}
                        {currentStep.S.map(s => (
                            <tr key={s} className="bg-blue-50 bg-opacity-30">
                                <td className="border p-2 font-mono">{s || 'ε'}</td>
                                {currentStep.E.map(e => (
                                    <td key={e} className="border p-2 text-center highlight-cell">
                                        {currentStep.table[s][e] ? '✓' : '✗'}
                                    </td>
                                ))}
                            </tr>
                        ))}
                        {/* S·Σ rows */}
                        {Array.from(currentStep.SigmaRows || []).map(s => (
                            <tr key={s} className="bg-yellow-50 bg-opacity-30">
                                <td className="border p-2 font-mono">{s || 'ε'}</td>
                                {currentStep.E.map(e => (
                                    <td key={e} className="border p-2 text-center highlight-cell">
                                        {currentStep.table[s][e] ? '✓' : '✗'}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};




const DFAVisualization = ({ currentStep }) => {
    return (
        <div className="bg-white p-4 rounded shadow mt-4">
            <h3 className="font-bold mb-2">Current DFA</h3>
            <svg className="w-full h-64" viewBox="0 0 400 200">
                {/* Draw states */}
                {Array.from({ length: currentStep.dfa.states }).map((_, i) => (
                    <g key={i}>
                        <circle 
                            cx={`${100 + i * 100}`}
                            cy="100"
                            r="20"
                            fill="white"
                            stroke={currentStep.dfa.accepting.includes(i) ? '#4CAF50' : '#666'}
                            strokeWidth={currentStep.dfa.accepting.includes(i) ? '3' : '1'}
                        />
                        <text 
                            x={`${100 + i * 100}`}
                            y="100"
                            textAnchor="middle"
                            dominantBaseline="middle"
                        >
                            q{i}
                        </text>
                        {i === currentStep.dfa.initial && (
                            <path
                                d={`M${50 + i * 100} 100 h30`}
                                fill="none"
                                stroke="#666"
                                markerEnd="url(#arrowhead)"
                            />
                        )}
                    </g>
                ))}
                
                {/* Draw transitions */}
                <defs>
                    <marker
                        id="arrowhead"
                        markerWidth="10"
                        markerHeight="7"
                        refX="9"
                        refY="3.5"
                        orient="auto"
                    >
                        <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
                    </marker>
                </defs>
                {Object.entries(currentStep.dfa.transitions).map(([key, target], i) => {
                    const [source, symbol] = key.split(',');
                    return (
                        <g key={key}>
                            <path
                                d={`M${120 + Number(source) * 100} 100 H${80 + target * 100}`}
                                fill="none"
                                stroke="#666"
                                markerEnd="url(#arrowhead)"
                            />
                            <text
                                x={`${100 + (Number(source) * 100 + target * 100) / 2}`}
                                y="90"
                                textAnchor="middle"
                            >
                                {symbol}
                            </text>
                        </g>
                    );
                })}
            </svg>
        </div>
    );
};



const LStarVisualization = () => {
    const [step, setStep] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [speed, setSpeed] = useState(1000);
    const [showExplanation, setShowExplanation] = useState(false);

    useEffect(() => {
        let timer;
        if (isPlaying && step < learningSteps.length - 1) {
            timer = setTimeout(() => setStep(s => s + 1), speed);
        }
        return () => clearTimeout(timer);
    }, [isPlaying, step, speed]);

    return (
        <div className="max-w-4xl mx-auto p-4">
            <div className="bg-gray-100 p-6 rounded-lg">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold">L* Algorithm Visualization</h2>
                    <div className="space-x-2">
                        <button
                            onClick={() => setIsPlaying(!isPlaying)}
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            {isPlaying ? 'Pause' : 'Play'}
                        </button>
                        <button
                            onClick={() => setStep(s => Math.max(0, s - 1))}
                            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                            disabled={step === 0}
                        >
                            Previous
                        </button>
                        <button
                            onClick={() => setStep(s => Math.min(learningSteps.length - 1, s + 1))}
                            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                            disabled={step === learningSteps.length - 1}
                        >
                            Next
                        </button>
                    </div>
                </div>

                <div className="mb-4">
                    <h3 className="font-bold">Step {step + 1}: {learningSteps[step].step}</h3>
                    <p className="text-gray-600">{learningSteps[step].description}</p>
                </div>

                <ObservationTable 
                    currentStep={learningSteps[step]}
                    onShowExplanation={() => setShowExplanation(true)}
                />
                
                <DFAVisualization currentStep={learningSteps[step]} />

                <TableExplanation 
                    isVisible={showExplanation} 
                    onClose={() => setShowExplanation(false)}
                />

                <div className="mt-4 flex items-center space-x-4">
                    <label>Animation Speed:</label>
                    <input
                        type="range"
                        min="100"
                        max="2000"
                        value={speed}
                        onChange={(e) => setSpeed(Number(e.target.value))}
                        className="w-48"
                    />
                    <span>{speed}ms</span>
                </div>
            </div>
        </div>
    );
};

// Render the component
ReactDOM.render(
    <LStarVisualization />,
    document.getElementById('root')
);