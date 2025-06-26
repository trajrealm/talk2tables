import { Box, Button, TextField } from "@mui/material";
import React from "react";

type Props = {
  mode: "login" | "signup";
  email: string;
  password: string;
  loading: boolean;
  onEmailChange: (val: string) => void;
  onPasswordChange: (val: string) => void;
  onSubmit: (e: React.FormEvent) => void;
};

export default function AuthForm({
  mode,
  email,
  password,
  loading,
  onEmailChange,
  onPasswordChange,
  onSubmit,
}: Props) {
  return (
    <Box component="form" onSubmit={onSubmit} sx={{ mt: 3 }}>
      <TextField
        fullWidth
        required
        label="Email Address"
        type="email"
        margin="normal"
        value={email}
        onChange={(e) => onEmailChange(e.target.value)}
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
        onChange={(e) => onPasswordChange(e.target.value)}
        autoComplete={mode === "login" ? "current-password" : "new-password"}
      />
      <Button type="submit" fullWidth variant="contained" sx={{ mt: 3 }} disabled={loading}>
        {loading ? "Please wait..." : mode === "login" ? "Login" : "Sign Up"}
      </Button>
    </Box>
  );
}
