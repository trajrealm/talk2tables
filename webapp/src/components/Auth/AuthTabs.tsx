import { Tabs, Tab } from "@mui/material";

type Props = {
  mode: "login" | "signup";
  onChange: (val: "login" | "signup") => void;
  isMobile: boolean;
};

export default function AuthTabs({ mode, onChange, isMobile }: Props) {
  return (
    <Tabs
      value={mode}
      onChange={(e, val) => onChange(val)}
      textColor="primary"
      indicatorColor="primary"
      variant={isMobile ? "fullWidth" : "standard"}
    >
      <Tab label="Login" value="login" />
      <Tab label="Signup" value="signup" />
    </Tabs>
  );
}
