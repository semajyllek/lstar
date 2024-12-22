const { useState, useEffect } = React;

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