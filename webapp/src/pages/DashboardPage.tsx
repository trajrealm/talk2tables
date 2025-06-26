import React, { useState, useEffect } from "react";
import {
  Container,
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { BACKEND_URL } from "../utils/constants";

export default function DashboardPage() {
  const navigate = useNavigate();
  const userEmail = localStorage.getItem("user_email") || "User";

  const [connectedDatabases, setConnectedDatabases] = useState<any[]>([]);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [dbForm, setDbForm] = useState({
    name: "",
    host: "",
    port: 5432,
    username: "",
    password: "",
    database: "",
    schema: "",
    type: "PostgreSQL",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setDbForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleDbSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage(null);

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/connect_database`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(dbForm),
      });

      const data = await res.json();

      if (!res.ok) {
        console.error("Error:", data);
        return;
      }

      setSuccessMessage("Database connected and schema extracted successfully!");
      setDbForm({
        name: "",
        host: "",
        port: 5432,
        username: "",
        password: "",
        database: "",
        schema: "",
        type: "PostgreSQL",
      });
      fetchDatabases();
    } catch (err) {
      console.error("Network error:", err);
    }
  };

  const fetchDatabases = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/get_user_databases`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();
      setConnectedDatabases(data);
    } catch (err) {
      console.error("Failed to fetch databases", err);
    }
  };

  useEffect(() => {
    fetchDatabases();
  }, []);

  return (
    <>
      <Header userEmail={userEmail} />

      <Container maxWidth="lg" sx={{ mt: 6, mb: 6 }}>
        <Typography variant="h4" gutterBottom>
          Welcome to Your Dashboard
        </Typography>
        <Typography variant="subtitle1" sx={{ mb: 4 }}>
          Here you’ll be able to connect to your own database, view connections, and manage your schemas.
        </Typography>

        {successMessage && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {successMessage}
          </Alert>
        )}

        <Box display="flex" gap={4} flexDirection={{ xs: "column", md: "row" }}>
          {/* Form - Connect DB */}
          <Box flex={2}>
            <Paper sx={{ p: 3 }} elevation={3}>
              <Typography variant="h6" gutterBottom>
                Connect Your Database
              </Typography>
              <Box component="form" onSubmit={handleDbSubmit} noValidate autoComplete="off">
                {["name", "host", "port", "username", "password", "database", "schema"].map((field) => (
                  <TextField
                    key={field}
                    fullWidth
                    label={field === "schema" ? "Schema *" : field[0].toUpperCase() + field.slice(1)}
                    name={field}
                    type={field === "password" ? "password" : field === "port" ? "number" : "text"}
                    value={dbForm[field as keyof typeof dbForm]}
                    onChange={handleChange}
                    margin="normal"
                    required={field !== "schema"}
                  />
                ))}
                <TextField
                  fullWidth
                  label="Database Type"
                  name="type"
                  value={dbForm.type}
                  margin="normal"
                  disabled
                />
                <Box mt={2}>
                  <Button type="submit" variant="contained">
                    Connect & Extract Schema
                  </Button>
                </Box>
              </Box>
            </Paper>
          </Box>

          {/* Connected Databases */}
          <Box flex={1}>
            <Typography variant="h6" gutterBottom>
              Your Databases
            </Typography>
            {connectedDatabases.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No databases connected yet.
              </Typography>
            ) : (
              connectedDatabases.map((db: any) => (
                <Paper key={db.id} sx={{ p: 2, mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography variant="subtitle1">{db.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {db.db_type} – {db.host}
                      </Typography>
                    </Box>
                    <Box textAlign="right">
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => navigate(`/converse/${db.id}`)}
                      >
                        Converse
                      </Button>
                    </Box>
                  </Box>
                </Paper>
              ))
            )}
          </Box>
        </Box>
      </Container>

      <Footer />
    </>
  );
}
