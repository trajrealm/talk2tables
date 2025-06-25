import React, { useState } from "react";
import {
  Box,
  Button,
  Container,
  CssBaseline,
  Paper,
  Tab,
  Tabs,
  TextField,
  Typography,
  useMediaQuery,
  useTheme,
  Alert,
  Snackbar,
  IconButton,
} from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';
import { useColorMode } from "../theme/ThemeProvider";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import { useNavigate } from "react-router-dom";


type AuthMode = "login" | "signup";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";


export default function AuthPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const { toggleColorMode } = useColorMode(); // <-- Correctly inside component

  const [mode, setMode] = useState<AuthMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    const endpoint = mode === "login" ? "/login" : "/signup";

    try {
      const res = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrorMsg(data.detail || data.message || "Something went wrong");
      } else {
        if (mode === "login") {
          localStorage.setItem("access_token", data.access_token);
          setSuccessMsg("Logged in successfully!");
          // Redirect to MainPage
          navigate("/dashboard");

        } else {
          setSuccessMsg("Signup successful! Please login.");
          setMode("login");
          setEmail("");
          setPassword("");
        }
      }
    } catch {
      setErrorMsg("Network error, please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xs" sx={{ mt: 8, mb: 4 }}>
      {/* Logo and Header */}
      <Box
        sx={{
          textAlign: "center",
          mb: 4,
          userSelect: "none",
        }}
      >
        {/* Replace with your logo path or SVG */}
        <img
          src="/logo.svg"
          alt="Table Converse Logo"
          style={{ height: 80, marginBottom: 16 }}
        />
        {/* <Typography
          variant="h4"
          component="h1"
          sx={{ fontWeight: "bold", mb: 1, color: theme.palette.text.primary }}
        >
          Table Converse
        </Typography> */}

        <Typography
          variant="subtitle1"
          sx={{
            color: theme.palette.text.secondary,
            fontStyle: "italic",
            maxWidth: 320,
            margin: "auto",
          }}
        >
          Talk to your database in natural language. Instantly generate SQL queries, explore your tables, and visualize data — no coding required.
        </Typography>
      </Box>


      <CssBaseline />
      
      <Paper
        elevation={3}
        sx={{
          marginTop: 8,
          padding: 4,
          borderRadius: 2,
          bgcolor: theme.palette.background.paper,
          position: "relative",
        }}
      >
        {/* Theme toggle button */}
        <Button
          onClick={toggleColorMode}
          startIcon={theme.palette.mode === "dark" ? <Brightness7Icon /> : <Brightness4Icon />}
          sx={{ position: "absolute", top: 16, right: 16 }}
        >
          {theme.palette.mode === "dark" ? "Light Mode" : "Dark Mode"}
        </Button>

        <Tabs
          value={mode}
          onChange={(e, val) => {
            setErrorMsg(null);
            setSuccessMsg(null);
            setMode(val);
          }}
          textColor="primary"
          indicatorColor="primary"
          variant={isMobile ? "fullWidth" : "standard"}
          aria-label="authentication tabs"
        >
          <Tab label="Login" value="login" />
          <Tab label="Signup" value="signup" />
        </Tabs>

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
          <TextField
            fullWidth
            required
            label="Email Address"
            type="email"
            margin="normal"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            autoFocus
          />

          <TextField
            fullWidth
            required
            label="Password"
            type="password"
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3 }}
            disabled={loading}
          >
            {loading ? "Please wait..." : mode === "login" ? "Login" : "Sign Up"}
          </Button>
        </Box>

        {/* Success Snackbar */}
        <Snackbar
          open={!!successMsg}
          autoHideDuration={6000}
          onClose={() => setSuccessMsg(null)}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert
            onClose={() => setSuccessMsg(null)}
            severity="success"
            sx={{ width: "100%" }}
          >
            {successMsg}
          </Alert>
        </Snackbar>

        {/* Error Snackbar */}
        <Snackbar
          open={!!errorMsg}
          autoHideDuration={6000}
          onClose={() => setErrorMsg(null)}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert
            onClose={() => setErrorMsg(null)}
            severity="error"
            sx={{ width: "100%" }}
            action={
              <IconButton
                aria-label="close"
                color="inherit"
                size="small"
                onClick={() => setErrorMsg(null)}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            }
          >
            {errorMsg}
          </Alert>
        </Snackbar>
      </Paper>
    </Container>
  );
}
