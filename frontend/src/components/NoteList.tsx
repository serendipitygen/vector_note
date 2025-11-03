import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Typography,
  Paper,
  TextField,
  IconButton,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputAdornment,
  useTheme,
  Button,
  Autocomplete,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import SearchIcon from "@mui/icons-material/Search";
import { API_URL } from "../config";
import { useAuth } from "../contexts/AuthContext";

interface Note {
  id: number;
  title: string;
  content: string;
  source_type: string;
  source_path: string;
  category: string;
  created_at: string;
}

const NoteList: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const { token, refreshKey, refreshNotes, categories, setCategories } =
    useAuth();
  const theme = useTheme();

  const NOTES_PER_PAGE = 5;

  const fetchNotes = useCallback(
    async (isNewSearch = false) => {
      setLoading(true);
      setError(null);
      try {
        const skip = isNewSearch ? 0 : (page - 1) * NOTES_PER_PAGE;
        const params = new URLSearchParams({
          skip: String(skip),
          limit: String(NOTES_PER_PAGE),
        });
        if (searchQuery) params.append("search", searchQuery);
        if (categoryFilter) params.append("category", categoryFilter);

        const response = await fetch(
          `${API_URL}/api/v1/notes/?${params.toString()}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (response.ok) {
          const data = await response.json();
          const newNotes = data.notes || [];

          setNotes((prevNotes) =>
            isNewSearch ? newNotes : [...prevNotes, ...newNotes]
          );
          setTotal(data.total || 0);

          const allNotesForCategories = isNewSearch
            ? newNotes
            : [...notes, ...newNotes];
          const uniqueCategories = Array.from(
            new Set(
              allNotesForCategories
                .map((note: Note) => note.category)
                .filter(Boolean) as string[]
            )
          );
          if (setCategories) setCategories(uniqueCategories);
        } else {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Failed to fetch notes");
        }
      } catch (err: any) {
        setError(err.message || "An unknown error occurred");
        setNotes([]);
      } finally {
        setLoading(false);
      }
    },
    [token, page, searchQuery, categoryFilter, setCategories]
  );

  useEffect(() => {
    setNotes([]);
    setPage(1);
    fetchNotes(true);
  }, [searchQuery, categoryFilter, refreshKey]);

  useEffect(() => {
    if (page > 1) {
      fetchNotes();
    }
  }, [page]);

  const handleSearch = () => {
    setNotes([]);
    setPage(1);
    fetchNotes(true);
  };

  const hasMore = notes.length < total;

  const handleDelete = async (id: number) => {
    if (window.confirm("정말로 이 노트를 삭제하시겠습니까?")) {
      try {
        const response = await fetch(`${API_URL}/api/v1/notes/${id}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (response.ok) {
          if (refreshNotes) refreshNotes();
        } else {
          const errorData = await response.json();
          alert(`삭제 실패: ${errorData.detail}`);
        }
      } catch (error) {
        console.error("Failed to delete note:", error);
        alert("노트 삭제 중 에러가 발생했습니다.");
      }
    }
  };

  return (
    <Paper
      elevation={0}
      variant="outlined"
      sx={{ p: { xs: 2, md: 3 }, height: "100%", bgcolor: "transparent" }}
    >
      <Typography
        variant="h5"
        component="h2"
        sx={{ mb: 2, fontWeight: "bold" }}
      >
        내 노트 목록
      </Typography>

      <Box
        component="form"
        sx={{ mb: 3 }}
        onSubmit={(e) => {
          e.preventDefault();
          handleSearch();
        }}
      >
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
          <Box sx={{ flex: "1 1 250px" }}>
            <TextField
              fullWidth
              placeholder="제목 또는 내용으로 검색..."
              variant="outlined"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />
          </Box>
          <Box sx={{ flex: "1 1 200px" }}>
            <Autocomplete
              fullWidth
              options={categories || []}
              value={categoryFilter}
              onChange={(event, newValue) => {
                setCategoryFilter(newValue);
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder="카테고리 필터"
                  variant="outlined"
                  size="small"
                />
              )}
            />
          </Box>
          <Box sx={{ flex: "0 0 100px" }}>
            <Button variant="contained" type="submit" fullWidth>
              검색
            </Button>
          </Box>
        </Box>
      </Box>

      {loading && page === 1 && (
        <Box sx={{ display: "flex", justifyContent: "center", my: 5 }}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {!loading && !error && notes.length === 0 && (
        <Box sx={{ textAlign: "center", py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            아직 작성된 노트가 없습니다.
          </Typography>
          <Typography color="text.secondary">
            첫 노트를 추가해보세요!
          </Typography>
        </Box>
      )}

      {!loading && !error && notes.length > 0 && (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "1fr",
            gap: 2.5,
          }}
        >
          {notes.map((note) => (
            <Card
              key={note.id}
              variant="outlined"
              sx={{
                transition: "box-shadow 0.3s, transform 0.3s",
                "&:hover": {
                  boxShadow: theme.shadows[4],
                  transform: "translateY(-4px)",
                },
              }}
            >
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    mb: 1,
                  }}
                >
                  <Box>
                    <Typography
                      variant="h6"
                      component="div"
                      sx={{ fontWeight: "600" }}
                    >
                      {note.title}
                    </Typography>
                    {note.category && (
                      <Chip
                        label={note.category}
                        size="small"
                        color="primary"
                        variant="outlined"
                        sx={{ mt: 0.5, mb: 1, fontWeight: "500" }}
                      />
                    )}
                  </Box>
                  <IconButton
                    onClick={() => handleDelete(note.id)}
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    display: "-webkit-box",
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    minHeight: "3.8rem",
                  }}
                >
                  {note.content}
                </Typography>
                <Accordion
                  elevation={0}
                  disableGutters
                  sx={{
                    "&:before": { display: "none" },
                    mt: 1,
                    bgcolor: "transparent",
                    ".MuiAccordionSummary-root": { p: 0 },
                    ".MuiAccordionDetails-root": { p: 0, pt: 1 },
                  }}
                >
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="caption" color="text.secondary">
                      더보기
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography
                      variant="body2"
                      component="div"
                      sx={{
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-all",
                      }}
                    >
                      {note.content}
                      {(note.source_type === "url" ||
                        note.source_type === "file") && (
                        <Box
                          sx={{
                            mt: 2,
                            p: 1.5,
                            bgcolor: "action.hover",
                            borderRadius: 1,
                          }}
                        >
                          <Typography variant="caption" display="block">
                            <b>소스 타입:</b> {note.source_type}
                          </Typography>
                          <Typography
                            variant="caption"
                            display="block"
                            sx={{ wordBreak: "break-all" }}
                          >
                            <b>경로:</b>{" "}
                            {note.source_type === "url" ? (
                              <a
                                href={note.source_path}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                {note.source_path}
                              </a>
                            ) : (
                              note.source_path
                            )}
                          </Typography>
                          <Typography variant="caption" display="block">
                            <b>작성일:</b>{" "}
                            {new Date(note.created_at).toLocaleString()}
                          </Typography>
                        </Box>
                      )}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {hasMore && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
          <Button
            variant="outlined"
            onClick={() => setPage((prev) => prev + 1)}
            disabled={loading}
          >
            {loading ? "로딩 중..." : "더보기"}
          </Button>
        </Box>
      )}
    </Paper>
  );
};

export default NoteList;
