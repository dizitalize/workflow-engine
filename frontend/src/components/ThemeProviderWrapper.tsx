"use client";

import { ThemeProvider } from "@mui/material/styles";
import { CssBaseline } from "@mui/material";
import { getTheme } from "@/theme/theme";
import "@/app/globals.css";

export default function ThemeProviderWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const theme = getTheme();
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}