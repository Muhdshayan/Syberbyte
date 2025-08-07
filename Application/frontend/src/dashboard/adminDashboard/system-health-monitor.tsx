
export default function SystemHealthMonitor() {
    return (
        <div className="flex flex-col items-center justify-center h-screen w-full">
            <h1 className="text-3xl font-bold mb-4">System Health Monitor</h1>
            <p className="text-lg text-gray-700 mb-6">Monitor the health of your system here.</p>
            <iframe
                src="http://localhost:3000/goto/MsGRYJ8NR?orgId=1"
                className="w-full max-w-7xl h-[70vh] border-2 border-gray-200 rounded-lg shadow-md"
                title="Grafana Dashboard"
                allowFullScreen
            />
        </div>
    );
}