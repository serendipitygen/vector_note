import React from "react";
import { Routes, Route, Navigate, Link as RouterLink } from "react-router-dom";
import {
  AppBar,
  Box,
  Button,
  Container,
  CssBaseline,
  Toolbar,
  Typography,
} from "@mui/material";
import Auth from "./components/Auth";
import AddNote from "./components/AddNote";
import NoteList from "./components/NoteList";
import Chat from "./components/Chat";
import { useAuth } from "./contexts/AuthContext";

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { token } = useAuth();
  return token ? <>{children}</> : <Navigate to="/auth" />;
};

const AppContent: React.FC = () => {
  return (
    <Routes>
      <Route path="/auth" element={<Auth />} />
      <Route path="/login" element={<Auth />} />

      <Route
        path="/notes"
        element={
          <PrivateRoute>
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", md: "1fr 2fr" },
                gap: 3,
              }}
            >
              <Box>
                <AddNote />
              </Box>
              <Box>
                <NoteList />
              </Box>
            </Box>
          </PrivateRoute>
        }
      />

      <Route
        path="/chat"
        element={
          <PrivateRoute>
            <Chat />
          </PrivateRoute>
        }
      />

      <Route path="/" element={<Navigate to="/notes" />} />
    </Routes>
  );
};

const App: React.FC = () => {
  const { token, logout } = useAuth();

  return (
    <Box sx={{ bgcolor: "#f4f6f8", minHeight: "100vh" }}>
      <CssBaseline />
      <AppBar
        position="sticky"
        color="default"
        elevation={0}
        sx={{ bgcolor: "white" }}
      >
        <Toolbar>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              flexGrow: 1,
              textDecoration: "none",
              color: "inherit",
              fontWeight: "bold",
            }}
          >
            Vector Note
          </Typography>
          {token && (
            <>
              <Button color="inherit" component={RouterLink} to="/notes">
                노트
              </Button>
              <Button color="inherit" component={RouterLink} to="/chat">
                채팅
              </Button>
              <Button color="inherit" onClick={logout}>
                로그아웃
              </Button>
            </>
          )}
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <AppContent />
      </Container>
    </Box>
  );
};

export default App;
