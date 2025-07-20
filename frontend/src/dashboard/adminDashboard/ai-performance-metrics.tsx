export default function AiPerformanceMetrics() {
    return (
        <div className="flex flex-col items-center justify-center h-screen w-full">
            <h1 className="text-3xl font-bold mb-4">AI Performance Metrics</h1>
            <p className="text-lg text-gray-700">Analyze the performance of AI models here.</p>
            {/* Add more AI performance metrics components here */}
            <iframe
                src="http://localhost:3000/goto/QXjTYJ8NR?orgId=1"
                className="w-full max-w-7xl h-[70vh] border-2 border-gray-200 rounded-lg shadow-md"
                title="Grafana Dashboard"
                allowFullScreen
            />
        </div>
    );
}