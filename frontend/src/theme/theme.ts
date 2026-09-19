import { createTheme, Theme } from "@mui/material/styles";

let cachedTheme: Theme | null = null;

export const getTheme = (): Theme => {
  if (!cachedTheme) {
    cachedTheme = createTheme({
      palette: {
        primary: {
          main: "#1976d2",
        },
        secondary: {
          main: "#dc004e",
        },
      },
      typography: {
        fontFamily: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ].join(","),
      },
      shape: {
        borderRadius: 8,
      },
      components: {
        MuiButton: {
          styleOverrides: {
            root: {
              textTransform: "none",
            },
          },
        },
        MuiCard: {
          styleOverrides: {
            root: {
              borderRadius: 12,
            },
          },
        },
      },
    });
  }
  return cachedTheme;
};

export default getTheme;