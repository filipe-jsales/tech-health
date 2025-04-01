import React, { createContext, useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [githubToken, setGithubToken] = useState(
    localStorage.getItem("github_token") || null
  );
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const validateToken = async () => {
      if (githubToken) {
        try {
          const response = await axios.post("/api/github/connect", {
            access_token: githubToken,
          });

          if (response.data && response.data.status === "connected") {
            setUser({
              username: response.data.username,
              avatar: `https://github.com/${response.data.username}.png`,
            });
          } else {
            logout();
          }
        } catch (error) {
          console.error("Error validating token:", error);
          logout();
        }
      }
      setLoading(false);
    };

    validateToken();
  }, [githubToken]);

  const login = async (token) => {
    setLoading(true);
    try {
      const response = await axios.post("/api/github/connect", {
        access_token: token,
      });

      if (response.data && response.data.status === "connected") {
        localStorage.setItem("github_token", token);
        setGithubToken(token);
        setUser({
          username: response.data.username,
          avatar: `https://github.com/${response.data.username}.png`,
        });
        navigate("/");
        return { success: true };
      }

      return {
        success: false,
        message: "Failed to connect to GitHub",
      };
    } catch (error) {
      console.error("Login error:", error);
      return {
        success: false,
        message: error.response?.data?.detail || "Invalid GitHub token",
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("github_token");
    setGithubToken(null);
    setUser(null);
    navigate("/login");
  };

  const getToken = () => {
    return githubToken;
  };

  const value = {
    user,
    loading,
    login,
    logout,
    getToken,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
