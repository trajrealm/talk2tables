import React from "react";
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
} from "@mui/material";
import StorageIcon from "@mui/icons-material/Storage";
import DnsIcon from "@mui/icons-material/Dns";
import PublicIcon from "@mui/icons-material/Public";
import LanIcon from "@mui/icons-material/Lan";
import PermIdentityIcon from "@mui/icons-material/PermIdentity";
import AccountTreeIcon from "@mui/icons-material/AccountTree";

interface ConnectedDbInfoProps {
  dbInfo: any;
  loading: boolean;
}

const ConnectedDbInfo: React.FC<ConnectedDbInfoProps> = ({ dbInfo, loading }) => {
  if (loading) {
    return (
      <Box display="flex" alignItems="center" gap={2}>
        <CircularProgress size={20} />
        <Typography>Loading database info...</Typography>
      </Box>
    );
  }

  if (!dbInfo) {
    return <Alert severity="error">Failed to load database info.</Alert>;
  }

  return (
    <Box
      sx={{
        position: "relative",
        border: "1px solid #ccc",
        borderRadius: 2,
        backgroundColor: "#fafafa",
        px: 2,
        py: 1.5,
        mb: 3,
      }}
    >
      <Box
        sx={{
          position: "absolute",
          top: "-10px",
          left: 16,
          backgroundColor: "#fafafa",
          px: 1,
          fontSize: "0.8rem",
          fontWeight: "bold",
          color: "text.secondary",
        }}
      >
        Connected DB
      </Box>

      <Box
        sx={{
          display: "flex",
          flexWrap: "wrap",
          gap: 2,
          alignItems: "center",
          fontSize: "0.85rem",
          color: "text.secondary",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
          <StorageIcon fontSize="small" sx={{ color: "#1976d2" }} />
          <span><strong>Name:</strong> {dbInfo.name}</span>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
          <DnsIcon fontSize="small" sx={{ color: "#388e3c" }} />
          <span><strong>Type:</strong> {dbInfo.db_type}</span>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
          <PublicIcon fontSize="small" sx={{ color: "#f57c00" }} />
          <span><strong>Host:</strong> {dbInfo.host}</span>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
          <LanIcon fontSize="small" sx={{ color: "#d32f2f" }} />
          <span><strong>Port:</strong> {dbInfo.port}</span>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
          <PermIdentityIcon fontSize="small" sx={{ color: "#7b1fa2" }} />
          <span><strong>User:</strong> {dbInfo.username}</span>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
          <AccountTreeIcon fontSize="small" sx={{ color: "#00796f" }} />
          <span><strong>Schema:</strong> {dbInfo.schema}</span>
        </Box>
      </Box>
    </Box>
  );
};

export default ConnectedDbInfo;
