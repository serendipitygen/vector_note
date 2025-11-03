import React, { useState } from "react";
import {
  Box,
  Paper,
  TextField,
  Button,
  Tab,
  Tabs,
  Alert,
  InputAdornment,
  IconButton,
  CircularProgress,
  Typography,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { API_URL } from "../config";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Auth: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [tab, setTab] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
    // 입력 시 에러 메시지 초기화
    setError(null);
  };

  const validateForm = () => {
    if (tab === 0) {
      // 로그인 유효성 검사
      if (!formData.username || !formData.password) {
        setError("사용자명과 비밀번호를 입력해주세요.");
        return false;
      }
    } else {
      // 회원가입 유효성 검사
      if (!formData.username || !formData.email || !formData.password) {
        setError("모든 필드를 입력해주세요.");
        return false;
      }
      if (formData.password.length < 8) {
        setError("비밀번호는 최소 8자 이상이어야 합니다.");
        return false;
      }
      if (!/[A-Za-z]/.test(formData.password)) {
        setError("비밀번호는 최소 하나의 문자를 포함해야 합니다.");
        return false;
      }
      if (!/[0-9]/.test(formData.password)) {
        setError("비밀번호는 최소 하나의 숫자를 포함해야 합니다.");
        return false;
      }
      if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
        setError("사용자명은 영문자, 숫자, 언더스코어만 사용할 수 있습니다.");
        return false;
      }
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const endpoint =
        tab === 0
          ? `${API_URL}/api/v1/auth/login`
          : `${API_URL}/api/v1/auth/register`;

      const requestData =
        tab === 0
          ? new URLSearchParams({
              username: formData.username,
              password: formData.password,
            })
          : {
              username: formData.username,
              email: formData.email,
              password: formData.password,
            };

      const response = await axios.post(endpoint, requestData, {
        headers: {
          "Content-Type":
            tab === 0
              ? "application/x-www-form-urlencoded"
              : "application/json",
        },
      });

      if (tab === 0) {
        // 로그인 성공
        if (login) {
          login(response.data.access_token);
        }
        setSuccess("로그인 성공!");
        navigate("/");
      } else {
        // 회원가입 성공
        setSuccess("회원가입이 완료되었습니다! 로그인해주세요.");
        setTab(0);
        setFormData({
          username: "",
          email: "",
          password: "",
        });
      }
    } catch (error: any) {
      console.error("Auth error:", error);

      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // 유효성 검사 에러
          const validationErrors = error.response.data.detail
            .map((err: any) => err.msg)
            .join(", ");
          setError(validationErrors);
        } else {
          setError(error.response.data.detail);
        }
      } else if (error.response?.status === 500) {
        setError("서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
      } else if (error.code === "ECONNABORTED") {
        setError("요청 시간이 초과되었습니다. 네트워크 연결을 확인해주세요.");
      } else {
        setError("네트워크 오류가 발생했습니다. 연결을 확인해주세요.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "80vh",
      }}
    >
      <Paper elevation={3} sx={{ width: "100%", maxWidth: 400 }}>
        <Tabs value={tab} onChange={(_, newValue) => setTab(newValue)} centered>
          <Tab label="로그인" />
          <Tab label="회원가입" />
        </Tabs>

        {error && (
          <Alert severity="error" sx={{ m: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ m: 2 }}>
            {success}
          </Alert>
        )}

        <TabPanel value={tab} index={0}>
          <Typography variant="h6" sx={{ mb: 2, textAlign: "center" }}>
            로그인
          </Typography>
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="사용자 이름"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
              disabled={loading}
            />
            <TextField
              fullWidth
              label="비밀번호"
              name="password"
              type={showPassword ? "text" : "password"}
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
              disabled={loading}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      onMouseDown={(e) => e.preventDefault()}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : "로그인"}
            </Button>
          </Box>
        </TabPanel>

        <TabPanel value={tab} index={1}>
          <Typography variant="h6" sx={{ mb: 2, textAlign: "center" }}>
            회원가입
          </Typography>
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="사용자 이름"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
              disabled={loading}
              helperText="영문자, 숫자, 언더스코어만 사용 가능"
            />
            <TextField
              fullWidth
              label="이메일"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              margin="normal"
              required
              disabled={loading}
            />
            <TextField
              fullWidth
              label="비밀번호"
              name="password"
              type={showPassword ? "text" : "password"}
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
              disabled={loading}
              helperText="최소 8자, 문자와 숫자 포함"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      onMouseDown={(e) => e.preventDefault()}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : "회원가입"}
            </Button>
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default Auth;
