import { BACKEND_URL } from "./constants";

export async function authRequest(
  mode: "login" | "signup",
  email: string,
  password: string
): Promise<{ success: boolean; data?: any; error?: string }> {
  const endpoint = mode === "login" ? "/login" : "/signup";
  try {
    const res = await fetch(`${BACKEND_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (!res.ok) {
      return { success: false, error: data.detail || data.message || "Something went wrong" };
    }
    return { success: true, data };
  } catch {
    return { success: false, error: "Network error, please try again." };
  }
}
