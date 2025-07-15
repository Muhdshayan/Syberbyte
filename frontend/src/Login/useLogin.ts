import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore} from "@/Login/useAuthStore";


type Role = "HR" | "Recruiter" | "Admin";
export default function useLogin(initialRole: Role = "HR") {
  const navigate = useNavigate();
  const setAuthUser = useAuthStore((state) => state.setAuthUser);


  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [selectedRole, setSelectedRole] = useState<Role>(initialRole);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!email || !password) {
      setError("Both fields are required.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch("https://e6f8137658d1.ngrok-free.app/api/user/login/", {
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
      console.log("Login success:", data);
      setAuthUser(data);
      if (data.permission == 5 || data.permission == 10 || data.permission == 7){
        navigate("/dashboard/admin");
      } else {
        navigate(`/dashboard/${data.role}`);
      } 
    } catch (err) {
      setError("Network error. Please try again.");
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
    selectedRole,
    setSelectedRole,
    handleSubmit,
  };
}