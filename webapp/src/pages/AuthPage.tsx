import React, { useState } from "react";
import {
  Box,
  Container,
  CssBaseline,
  Paper,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

import LogoHeader from "../components/Auth/LogoHeader";
import ThemeToggle from "../components/Auth/ThemeToggle";
import AuthTabs from "../components/Auth/AuthTabs";
import AuthForm from "../components/Auth/AuthForm";
import SnackbarAlerts from "../components/Auth/SnackbarAlerts";
import { authRequest } from "../utils/api";

type AuthMode = "login" | "signup";

export default function AuthPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const navigate = useNavigate();

  const [mode, setMode] = useState<AuthMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    const res = await authRequest(mode, email, password);
    if (!res.success) {
      setErrorMsg(res.error || "Something went wrong");
    } else {
      if (mode === "login") {
        localStorage.setItem("access_token", res.data.access_token);
        setSuccessMsg("Logged in successfully!");
        navigate("/dashboard");
      } else {
        setSuccessMsg("Signup successful! Please login.");
        setMode("login");
        setEmail("");
        setPassword("");
      }
    }

    setLoading(false);
  };

  return (
    <Container maxWidth="xs" sx={{ mt: 8, mb: 4 }}>
      <LogoHeader />
      <CssBaseline />
      <Paper elevation={3} sx={{ mt: 8, p: 4, borderRadius: 2, position: "relative" }}>
        <ThemeToggle />
        <AuthTabs mode={mode} onChange={(val) => {
          setErrorMsg(null);
          setSuccessMsg(null);
          setMode(val);
        }} isMobile={isMobile} />
        <AuthForm
          mode={mode}
          email={email}
          password={password}
          loading={loading}
          onEmailChange={setEmail}
          onPasswordChange={setPassword}
          onSubmit={handleSubmit}
        />
        <SnackbarAlerts
          successMsg={successMsg}
          errorMsg={errorMsg}
          onClearSuccess={() => setSuccessMsg(null)}
          onClearError={() => setErrorMsg(null)}
        />
      </Paper>
    </Container>
  );
}
