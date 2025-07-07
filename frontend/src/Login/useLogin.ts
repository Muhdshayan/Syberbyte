// hooks/useLogin.js
import { useState } from "react";
import { useNavigate } from "react-router-dom";


/**
 * @param {string} initialRole - The default selected role ("HR", "Recruiter", "Admin")
 */4

type Role = "HR" | "Recruiter" | "Admin";
export default function useLogin(initialRole: Role = "HR") {
  const navigate = useNavigate();

 const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [selectedRole, setSelectedRole] = useState<Role>(initialRole);

  /* Replace this with your real backend endpoint
  const API_BASE = "https://your-api.com";*/

   const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!email || !password) {
      setError("Both fields are required.");
      return;
    }

    setLoading(true);
    setError("");

    setTimeout(() => {
      const role = selectedRole.toLowerCase();
      navigate(`/dashboard/${role}`);
      setLoading(false);
    }, 800);
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
