import { Typography, Box } from "@mui/material";
import { useTheme } from "@mui/material/styles";

export default function LogoHeader() {
  const theme = useTheme();
  return (
    <Box textAlign="center" mb={4} userSelect="none">
      <img src="/logo.svg" alt="Table Converse Logo" style={{ height: 80, marginBottom: 16 }} />
      <Typography
        variant="subtitle1"
        sx={{
          color: theme.palette.text.secondary,
          fontStyle: "italic",
          maxWidth: 320,
          margin: "auto",
        }}
      >
        Talk to your database in natural language. Instantly generate SQL queries, explore your
        tables, and visualize data — no coding required.
      </Typography>
    </Box>
  );
}
