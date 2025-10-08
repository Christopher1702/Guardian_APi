import React, { createContext, useContext, useState } from 'react';

const ThemeContext = createContext<any>(null);

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [darkMode, setDarkMode] = useState(true);

  const theme = {
    darkMode,
    toggle: () => setDarkMode((prev) => !prev),
    colors: {
      background: darkMode ? '#1F1F1F' : '#F8FAFC',
      text: darkMode ? '#FFFFFF' : '#1F1F1F',
      cardText: darkMode ? '#1F1F1F' : '#1F1F1F',
      navbar: darkMode ? '#111111' : '#E2E8F0',
      icon: darkMode ? '#FFFFFF' : '#1F1F1F',
      accent: '#A78BFA',
    },
  };

  return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => useContext(ThemeContext);