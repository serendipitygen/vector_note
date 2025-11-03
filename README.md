# Vector Note

AI 기반 노트 작성 및 벡터 검색 애플리케이션입니다. Google Gemini API를 활용한 AI 채팅과 시맨틱 검색 기능을 제공합니다.

## 주요 기능

- 📝 노트 작성 및 관리
- 🤖 AI 채팅 기능 (Google Gemini)
- 🔍 벡터 기반 시맨틱 검색
- 🔐 JWT 기반 사용자 인증
- 📄 문서 파일 지원 (PDF, DOCX)

## 기술 스택

### Backend
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy + Alembic
- Qdrant/Milvus (벡터 데이터베이스)
- Google Gemini API
- Sentence Transformers

### Frontend
- React 19 + TypeScript
- Material-UI
- React Router
- Axios

## 사전 요구사항

설치하기 전에 다음 프로그램들이 설치되어 있어야 합니다:

- Python 3.9 이상
- Node.js 16 이상 및 npm
- PostgreSQL 12 이상
- Git

## 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/serendipitygen/vector_note.git
cd vector_note
```

### 2. 데이터베이스 설정

PostgreSQL에 접속하여 데이터베이스와 사용자를 생성합니다:

```bash
psql -U postgres
```

다음 SQL 명령어를 실행합니다:

```sql
-- 새 사용자 생성
CREATE USER vector_note WITH PASSWORD 'vector_note_password';

-- 데이터베이스 생성
CREATE DATABASE vector_note;

-- 사용자에게 데이터베이스 권한 부여
GRANT ALL PRIVILEGES ON DATABASE vector_note TO vector_note;
```

종료: `\q`

### 3. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 필요한 값을 설정합니다:

```env
# 필수 설정
GOOGLE_API_KEY=your_google_api_key_here

# 데이터베이스 설정 (기본값 사용 가능)
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=vector_note
POSTGRES_PASSWORD=vector_note_password
POSTGRES_DB=vector_note

# JWT 시크릿 키 (프로덕션 환경에서는 반드시 변경)
SECRET_KEY=your-secret-key-change-this-in-production

# 선택 사항
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
```

### 4. Backend 설치 및 실행

#### 의존성 설치

```bash
pip install -r requirements.txt
```

#### 데이터베이스 마이그레이션

```bash
cd backend
alembic upgrade head
cd ..
```

#### 서버 실행

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

백엔드 서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### 5. Frontend 설치 및 실행

새 터미널 창을 열어서 다음 명령어를 실행합니다:

```bash
cd frontend
npm install
npm start
```

프론트엔드 애플리케이션이 자동으로 브라우저에서 열립니다:
- http://localhost:4996

## 개발 가이드

### Backend 개발

```bash
# 서버 실행 (hot reload)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 새 마이그레이션 생성
cd backend
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

### Frontend 개발

```bash
cd frontend

# 개발 서버 실행
npm start

# 테스트 실행
npm test

# 프로덕션 빌드
npm run build
```

### 프로세스 종료 (Windows)

```bash
# 모든 Node.js 및 Python 프로세스 종료
taskkill /F /IM node.exe & taskkill /F /IM python.exe

# Node.js 프로세스만 종료
taskkill /F /IM node.exe
```

## 프로젝트 구조

```
vector_note/
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── api/         # API 엔드포인트
│   │   ├── core/        # 설정 및 보안
│   │   ├── db/          # 데이터베이스 설정
│   │   ├── models/      # SQLAlchemy 모델
│   │   ├── schemas/     # Pydantic 스키마
│   │   ├── services/    # 비즈니스 로직
│   │   └── main.py      # FastAPI 앱
│   ├── alembic/         # 데이터베이스 마이그레이션
│   └── alembic.ini
├── frontend/            # React 프론트엔드
│   ├── public/
│   ├── src/
│   │   ├── components/  # React 컴포넌트
│   │   ├── contexts/    # Context API
│   │   └── App.tsx
│   └── package.json
├── .env                 # 환경 변수 (git에 포함 안 됨)
├── .env.example         # 환경 변수 예시
├── requirements.txt     # Python 의존성
├── CLAUDE.md           # Claude Code 가이드
└── README.md           # 이 파일
```

## 문제 해결

### 데이터베이스 연결 오류

PostgreSQL이 실행 중인지 확인하고, `.env` 파일의 데이터베이스 설정이 올바른지 확인하세요.

```bash
# PostgreSQL 서비스 상태 확인 (Windows)
# 서비스 관리자에서 PostgreSQL 서비스 확인

# PostgreSQL 서비스 상태 확인 (Linux/Mac)
sudo systemctl status postgresql
```

### 포트 충돌

기본 포트가 이미 사용 중인 경우:
- Backend: `--port` 옵션으로 다른 포트 지정
- Frontend: `package.json`의 `PORT` 환경 변수 수정

### Google API 키 오류

Google Cloud Console에서 Gemini API가 활성화되어 있고, API 키가 유효한지 확인하세요.

## 보안 주의사항

- `.env` 파일은 절대 git에 커밋하지 마세요
- 프로덕션 환경에서는 반드시 강력한 `SECRET_KEY`를 사용하세요
- API 키는 환경 변수로만 관리하고 코드에 직접 작성하지 마세요

## 라이선스

이 프로젝트는 개인 프로젝트입니다.

## 기여

이슈와 풀 리퀘스트는 환영합니다!
