import React, { useState } from "react";
import {
  Box,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  SelectChangeEvent,
  Autocomplete,
} from "@mui/material";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { API_URL } from "../config";

const AddNote: React.FC = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category, setCategory] = useState("");
  const [sourceType, setSourceType] = useState("text");
  const [file, setFile] = useState<File | null>(null);
  const { token, refreshNotes, categories } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("category", category);
      formData.append("source_type", sourceType);

      if (sourceType === "file" && file) {
        formData.append("file", file);
      } else {
        formData.append("content", content);
      }

      const response = await fetch(`${API_URL}/api/v1/notes/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        setTitle("");
        setContent("");
        setCategory("");
        setFile(null);
        setSourceType("text");
        if (refreshNotes) refreshNotes();
      } else {
        const errorData = await response.json();
        console.error("Failed to add note:", errorData.detail);
        alert(`노트 추가 실패: ${errorData.detail}`);
      }
    } catch (error) {
      console.error("Error adding note:", error);
      alert("노트 추가 중 에러가 발생했습니다.");
    }
  };

  return (
    <Paper
      elevation={0}
      variant="outlined"
      sx={{ p: { xs: 2, md: 3 }, height: "100%" }}
    >
      <Typography
        variant="h5"
        component="h2"
        sx={{ mb: 2, fontWeight: "bold" }}
      >
        새 노트 추가
      </Typography>

      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <Box sx={{ display: "grid", gap: 2 }}>
          <TextField
            fullWidth
            label="제목"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            variant="outlined"
          />

          <Autocomplete
            freeSolo
            options={categories}
            value={category}
            onChange={(event, newValue) => {
              setCategory(newValue || "");
            }}
            onInputChange={(event, newInputValue) => {
              setCategory(newInputValue);
            }}
            renderInput={(params) => (
              <TextField {...params} label="카테고리" variant="outlined" />
            )}
          />

          <FormControl fullWidth variant="outlined">
            <InputLabel>소스 타입</InputLabel>
            <Select
              value={sourceType}
              label="소스 타입"
              onChange={(e: SelectChangeEvent) => setSourceType(e.target.value)}
            >
              <MenuItem value="text">텍스트</MenuItem>
              <MenuItem value="file">파일</MenuItem>
              <MenuItem value="url">URL</MenuItem>
            </Select>
          </FormControl>

          {sourceType === "file" ? (
            <Button variant="outlined" component="label" fullWidth>
              {file ? file.name : "파일 선택"}
              <input
                type="file"
                hidden
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </Button>
          ) : (
            <TextField
              fullWidth
              multiline
              rows={5}
              label={sourceType === "url" ? "URL" : "내용"}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
              variant="outlined"
            />
          )}

          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            fullWidth
          >
            노트 저장
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default AddNote;
