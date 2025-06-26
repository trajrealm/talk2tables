import { Snackbar, Alert, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

type Props = {
  successMsg: string | null;
  errorMsg: string | null;
  onClearSuccess: () => void;
  onClearError: () => void;
};

export default function SnackbarAlerts({
  successMsg,
  errorMsg,
  onClearSuccess,
  onClearError,
}: Props) {
  return (
    <>
      <Snackbar
        open={!!successMsg}
        autoHideDuration={6000}
        onClose={onClearSuccess}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert onClose={onClearSuccess} severity="success" sx={{ width: "100%" }}>
          {successMsg}
        </Alert>
      </Snackbar>
      <Snackbar
        open={!!errorMsg}
        autoHideDuration={6000}
        onClose={onClearError}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={onClearError}
          severity="error"
          sx={{ width: "100%" }}
          action={
            <IconButton aria-label="close" color="inherit" size="small" onClick={onClearError}>
              <CloseIcon fontSize="small" />
            </IconButton>
          }
        >
          {errorMsg}
        </Alert>
      </Snackbar>
    </>
  );
}
