
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

export default DFAVisualization;