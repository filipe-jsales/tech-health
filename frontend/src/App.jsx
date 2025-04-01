import React from "react";
import { ChakraProvider, Box, Flex } from "@chakra-ui/react";
import { Routes, Route, useNavigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Reports from "./pages/Reports.jsx";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import { AuthProvider } from "./context/AuthContext";
import Header from "./components/Header/Header.jsx";
import RepositoryAnalysis from "./pages/ReportAnalysis.jsx";
import Sidebar from "./components/Sidebar/Sidebar.jsx";


function App() {
  return (
    <ChakraProvider>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<MainLayout />} />
        </Routes>
      </AuthProvider>
    </ChakraProvider>
  );
}

function MainLayout() {
  return (
    <Box minH="100vh">
      <Header />
      <Flex>
        <Sidebar />
        <Box flexGrow={1} p={6} bg="gray.50">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<RepositoryAnalysis />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Box>
      </Flex>
    </Box>
  );
}

export default App;