import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

interface AuthContextType {
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  refreshKey: number;
  refreshNotes: () => void;
  categories: string[];
  setCategories: (categories: string[]) => void;
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  login: () => {},
  logout: () => {},
  refreshKey: 0,
  refreshNotes: () => {},
  categories: [],
  setCategories: () => {},
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token")
  );
  const [refreshKey, setRefreshKey] = useState(0);
  const [categories, setCategories] = useState<string[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common["Authorization"];
    }
  }, [token]);

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem("token", newToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
    navigate("/auth");
  };

  const refreshNotes = useCallback(() => {
    setRefreshKey((oldKey) => oldKey + 1);
  }, []);

  const value = {
    token,
    login,
    logout,
    refreshKey,
    refreshNotes,
    categories,
    setCategories: useCallback((cats: string[]) => {
      setCategories(cats);
    }, []),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
