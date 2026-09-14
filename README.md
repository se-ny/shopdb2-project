# SHOPDB2 프로젝트

React, FastAPI, MySQL을 사용하는 3인 팀 쇼핑몰 프로젝트입니다.

## 공통 개발환경

- Frontend: React + Vite
- Backend: FastAPI
- Database: MySQL 8
- Python: 3.13
- Node.js: 24.x
- Backend 포트: 8000
- Frontend 포트: 5173
- API prefix: `/api`

## 프로젝트 구조

```text
shopdb2-project
├─ backend
│  ├─ app
│  │  ├─ core
│  │  │  ├─ config.py
│  │  │  └─ database.py
│  │  └─ main.py
│  ├─ .env.example
│  ├─ pyproject.toml
│  └─ uv.lock
├─ frontend
│  ├─ src
│  │  ├─ App.jsx
│  │  ├─ App.css
│  │  └─ main.jsx
│  ├─ package.json
│  └─ package-lock.json
├─ database
│  └─ shopdb2_schema_data.sql
└─ docs