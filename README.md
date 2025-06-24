psql -U postgres

-- 새 사용자 생성
CREATE USER vector_note WITH PASSWORD 'vector_note_password';

-- 데이터베이스 생성
CREATE DATABASE vector_note;

-- 사용자에게 데이터베이스 권한 부여
GRANT ALL PRIVILEGES ON DATABASE vector_note TO vector_note;

---

## 실행 방법

npm start 
uvicorn app.main:app --reload
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## 서버 종료

taskkill /F /IM node.exe & taskkill /F /IM python.exe
taskkill /F /IM node.exe
