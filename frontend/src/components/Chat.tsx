import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Typography,
  Divider,
  CircularProgress,
  ListItemButton,
} from "@mui/material";
import AddCommentIcon from "@mui/icons-material/AddComment";
import { useAuth } from "../contexts/AuthContext";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Session {
  id: number;
  title: string;
}

const Chat: React.FC = () => {
  const { token } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const apiBaseUrl = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchSessions = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/chat/sessions`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setSessions(data);
        if (data.length > 0 && !activeSessionId) {
          setActiveSessionId(data[0].id);
        }
      }
    } catch (error) {
      console.error("Failed to fetch sessions:", error);
    }
  };

  const fetchMessages = async (sessionId: number) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${apiBaseUrl}/api/v1/chat/sessions/${sessionId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error("Failed to fetch messages:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [token]);

  useEffect(() => {
    if (activeSessionId) {
      fetchMessages(activeSessionId);
    }
  }, [activeSessionId]);

  const handleNewSession = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/chat/sessions`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const newSession = await response.json();
        setSessions((prev) => [newSession, ...prev]);
        setActiveSessionId(newSession.id);
        setMessages([]);
      }
    } catch (error) {
      console.error("Failed to create new session:", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !activeSessionId || loading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(
        `${apiBaseUrl}/api/v1/chat/sessions/${activeSessionId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ message: currentInput }),
        }
      );

      if (!response.ok || !response.body) {
        throw new Error("Network response was not ok.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantResponse = "";

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        assistantResponse += chunk;

        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            role: "assistant",
            content: assistantResponse,
          };
          return newMessages;
        });
      }
    } catch (error) {
      console.error("Failed to get chat response:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "AI 응답을 가져오는데 실패했습니다." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: "flex", gap: 2, height: "calc(100vh - 120px)" }}>
      {/* Left Panel: Sessions */}
      <Box sx={{ width: "25%" }}>
        <Paper
          elevation={2}
          sx={{ height: "100%", display: "flex", flexDirection: "column" }}
        >
          <Box sx={{ p: 1, borderBottom: 1, borderColor: "divider" }}>
            <Button
              fullWidth
              variant="outlined"
              onClick={handleNewSession}
              startIcon={<AddCommentIcon />}
            >
              새로운 챗
            </Button>
          </Box>
          <List sx={{ flex: 1, overflow: "auto" }}>
            {sessions.map((session) => (
              <ListItemButton
                key={session.id}
                selected={activeSessionId === session.id}
                onClick={() => setActiveSessionId(session.id)}
              >
                <ListItemText primary={session.title} />
              </ListItemButton>
            ))}
          </List>
        </Paper>
      </Box>

      {/* Right Panel: Chat */}
      <Box sx={{ width: "75%" }}>
        <Paper
          elevation={2}
          sx={{ height: "100%", display: "flex", flexDirection: "column" }}
        >
          {!activeSessionId ? (
            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                height: "100%",
              }}
            >
              <Typography variant="h6" color="text.secondary">
                새로운 챗을 시작하거나 기존 챗을 선택하세요.
              </Typography>
            </Box>
          ) : (
            <>
              <Box sx={{ flex: 1, overflow: "auto", p: 2 }}>
                {loading && messages.length === 0 ? (
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                      height: "100%",
                    }}
                  >
                    <CircularProgress />
                  </Box>
                ) : (
                  <List>
                    {messages.map((message, index) => (
                      <React.Fragment key={index}>
                        <ListItem alignItems="flex-start">
                          <ListItemText
                            primary={
                              message.role === "user"
                                ? "사용자"
                                : "AI 어시스턴트"
                            }
                            secondary={
                              <Typography
                                component="span"
                                variant="body2"
                                color="text.primary"
                                sx={{ whiteSpace: "pre-wrap" }}
                              >
                                {message.content}
                              </Typography>
                            }
                          />
                        </ListItem>
                        {index < messages.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                    <div ref={messagesEndRef} />
                  </List>
                )}
              </Box>

              <Box
                component="form"
                onSubmit={handleSubmit}
                sx={{ p: 2, borderTop: 1, borderColor: "divider" }}
              >
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="질문을 입력하세요..."
                  disabled={loading || !activeSessionId}
                  onKeyPress={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }}
                />
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  fullWidth
                  sx={{ mt: 1 }}
                  disabled={loading || !activeSessionId}
                >
                  {loading ? "처리 중..." : "전송"}
                </Button>
              </Box>
            </>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default Chat;
