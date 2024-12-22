
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

export default TableExplanation;