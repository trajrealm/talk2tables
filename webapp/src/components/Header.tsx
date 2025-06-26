// webapp/src/components/Header.tsx

import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Button,
  Tooltip,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

interface HeaderProps {
  userEmail?: string;
  centerButton?: React.ReactNode; // NEW prop for custom center element
}

const Header: React.FC<HeaderProps> = ({ userEmail, centerButton }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleAvatarClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => setAnchorEl(null);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/auth");
  };

  return (
    <AppBar position="static">
      <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
        {/* Left: Logo */}
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <img src="/logo.svg" alt="Logo" style={{ height: 40, marginRight: 10 }} />
          <Typography variant="h6" sx={{ fontWeight: "bold" }} />
        </Box>

        {/* Center: Optional button */}
        <Box>{centerButton}</Box>

        {/* Right: Nav buttons + Avatar */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Button color="inherit" onClick={() => navigate("/")}>Home</Button>
          <Button color="inherit" onClick={() => navigate("/about")}>About</Button>
          <Button color="inherit" onClick={() => navigate("/contact")}>Contact</Button>

          <Tooltip title="Account">
            <IconButton onClick={handleAvatarClick}>
              <Avatar sx={{ bgcolor: "#00bfa5" }}>
                {userEmail?.charAt(0).toUpperCase() || "U"}
              </Avatar>
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "right" }}
          >
            <MenuItem disabled>{userEmail}</MenuItem>
            <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
            <MenuItem onClick={handleLogout}>Logout</MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
