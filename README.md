A chatbox app.
frontend: vue
backend: fastapi+langgraph

cd frontend
npm run dev
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
