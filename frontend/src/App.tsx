import { Button } from "@/components/ui/button";
import { useState } from "react";

function App() {
  const [response, setResponse] = useState("");

  const updateResponse = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/hello-world/");
      const data = await res.json();
      setResponse(data["message"]);
    } catch (error) {
      console.error("Error fetching time:", error);
      setResponse("Failed to fetch time");
    }
  };

  return (
    <div className="flex min-h-svh flex-col items-center justify-center space-y-4">
      <Button onClick={updateResponse}>Click me to see Time</Button>
      <div className="text-lg font-medium text-center text-primary">{response}</div>
    </div>
  );
}

export default App;
