import React from "react";

import { Box, Container, Divider, Typography, Link as MuiLink } from "@mui/material";

export default function Footer() {
  return (
    <Box component="footer" sx={{ py: 3, px: 2, mt: "auto", backgroundColor: (theme) => theme.palette.grey[200] }}>
      <Container maxWidth="md">
        <Divider sx={{ mb: 2 }} />
        <Box display="flex" justifyContent="space-between" flexWrap="wrap">
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} Table Converse. All rights reserved.
          </Typography>
          <Box>
            <MuiLink href="#" underline="hover" sx={{ ml: 2 }}>Privacy</MuiLink>
            <MuiLink href="#" underline="hover" sx={{ ml: 2 }}>Terms</MuiLink>
            <MuiLink href="#" underline="hover" sx={{ ml: 2 }}>Support</MuiLink>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
