
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

export default ObservationTable;

