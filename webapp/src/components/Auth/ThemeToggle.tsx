import { Button } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import { useColorMode } from "../../theme/ThemeProvider";

export default function ThemeToggle() {
  const theme = useTheme();
  const { toggleColorMode } = useColorMode();

  return (
    <Button
      onClick={toggleColorMode}
      startIcon={theme.palette.mode === "dark" ? <Brightness7Icon /> : <Brightness4Icon />}
      sx={{ position: "absolute", top: 16, right: 16 }}
    >
      {theme.palette.mode === "dark" ? "Light Mode" : "Dark Mode"}
    </Button>
  );
}
