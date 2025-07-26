import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore} from "@/Login/useAuthStore";

export default function useLogin() {
  const navigate = useNavigate();
  //const setAuthUser = useAuthStore((state) => state.setAuthUser);
  const attemptLogin = useAuthStore((state) => state.attemptLogin);

  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!email || !password) {
      setError("Both fields are required.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/api/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      
      if (!res.ok) {
        setError(data.message || "Login failed.");
        console.log("Login error:", data);
        setLoading(false);
        return;
      }

      // Use attemptLogin instead of setAuthUser for security check
      const loginSuccessful = attemptLogin(data);
      
      if (loginSuccessful) {
        // Only navigate if login was successful
        if (data.permission == 5 || data.permission == 10 || data.permission == 7) {
          navigate("/dashboard/admin");
        } else {
          navigate(`/dashboard/${data.role}`);
        }
      } else {
        // Login was blocked due to existing user session
        // The toast error message is already shown by attemptLogin
        setError("Another user is already logged in. Please logout from the previous session first.");
      }
      
    } catch (err) {
      setError("Network error. Please try again.");
      console.error("Login network error:", err);
    } finally {
      setLoading(false);
    }
  };

  return {
    email,
    setEmail,
    password,
    setPassword,
    loading,
    error,
    handleSubmit,
  };
}