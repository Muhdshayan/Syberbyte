import { useState } from "react";
import { useNavigate } from "react-router-dom";  // ✅ Import

export default function useLogin(defaultRole: string) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedRole, setSelectedRole] = useState(defaultRole);
  const navigate = useNavigate();  // ✅ Initialize navigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    console.log("[DEBUG] Submitting login form");
    console.log("[DEBUG] Email entered:", email);
    console.log("[DEBUG] Password entered:", password);
    console.log("[DEBUG] Role selected:", selectedRole);

    try {
      const response = await fetch("http://localhost:8000/api/user/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      console.log("[DEBUG] Server response:", data);

      if (!response.ok) {
        console.log("[DEBUG] Login failed. Server returned:", data.detail);
        setError(data.detail || "Login failed");
      } else {
        console.log("[DEBUG] Login successful for:", data.email);

        // ✅ Redirect based on role/permission/etc.
        navigate("/admin/job-category-management");  // or /admin, /home, etc.
      }
    } catch (err: any) {
      console.log("[DEBUG] Network error:", err);
      setError("Network error");
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
