// This controls screen-based navigation like a page stack
import { Stack } from 'expo-router';
import { ThemeProvider } from '../theme/ThemeContext'; // ✅ Added global theme context

// This is the main layout component for all routes under /app
export default function RootLayout() {
  return (
    <ThemeProvider>
      {/* The <Stack /> component defines the navigation structure */}
      {/* screenOptions hides the default top header bar */}
      <Stack screenOptions={{ headerShown: false }} />
    </ThemeProvider>
  );
}






