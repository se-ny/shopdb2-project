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

## 현재 구현 구조

현재 `develop` 브랜치에는 쇼핑몰의 상품/주문/판매자 기능과 관리자 기능, AI/RAG 관련 기능이 함께 구성되어 있습니다.

### Backend

FastAPI 애플리케이션은 기능별로 Model, Repository, Router, Schema, Service 계층을 나누어 구성합니다.

- Core
  - 환경설정
  - DB 연결
- Models
  - 사용자
  - 조직
  - 상품 / 상품 옵션
  - 재고
  - 정책
  - AI 관련 데이터
- Routers
  - 사용자 / 권한
  - 조직 관리
  - 상품
  - 주문
  - 판매자 상품 / 주문 / 프로필
  - 정책
  - AI Provider
  - RAG 문서
  - RAG 질의
- Repositories
  - 주문 Repository
  - 상품 Repository
- Services
  - 상품 / 주문 비즈니스 로직
  - Chat
  - Chunking
  - Embedding
  - Vector Store

### Frontend

React 화면은 API, 공통 컴포넌트, 역할별 페이지 구조로 구성합니다.

- 관리자
  - 조직 관리
  - 사용자 관리
  - 회사 정책 관리
  - 환불 정책 관리
  - AI / RAG 관리
  - 문서 등록
- 상품
  - 상품 목록
  - 상품 상세
  - 상품 등록/수정
  - 상품 이미지 관리
- 판매자
  - 판매자 프로필
  - 판매자 주문 목록

## 프로젝트 구조

```text
shopdb2-project/
├─ backend/
│  ├─ app/
│  │  ├─ core/
│  │  │  ├─ config.py
│  │  │  └─ database.py
│  │  ├─ models/
│  │  │  ├─ ai.py
│  │  │  ├─ inventory.py
│  │  │  ├─ org_unit.py
│  │  │  ├─ policy.py
│  │  │  ├─ product.py
│  │  │  ├─ product_variant.py
│  │  │  └─ user.py
│  │  ├─ repositories/
│  │  │  ├─ order_repository.py
│  │  │  └─ product_repository.py
│  │  ├─ routers/
│  │  │  ├─ ai_providers.py
│  │  │  ├─ orders.py
│  │  │  ├─ org_units.py
│  │  │  ├─ policies.py
│  │  │  ├─ products.py
│  │  │  ├─ rag_documents.py
│  │  │  ├─ rag_query.py
│  │  │  ├─ roles.py
│  │  │  ├─ seller_orders.py
│  │  │  ├─ seller_products.py
│  │  │  ├─ seller_profiles.py
│  │  │  └─ users.py
│  │  ├─ schemas/
│  │  │  ├─ ai.py
│  │  │  ├─ order.py
│  │  │  ├─ org_unit.py
│  │  │  ├─ policy.py
│  │  │  ├─ product.py
│  │  │  ├─ seller_order.py
│  │  │  ├─ seller_profile.py
│  │  │  └─ user.py
│  │  ├─ services/
│  │  │  ├─ chat.py
│  │  │  ├─ chunking.py
│  │  │  ├─ embeddings.py
│  │  │  ├─ order_service.py
│  │  │  ├─ product_service.py
│  │  │  └─ vector_store.py
│  │  └─ main.py
│  ├─ .env.example
│  ├─ pyproject.toml
│  └─ uv.lock
├─ database/
│  └─ shopdb2_schema_data.sql
├─ docs/
│  ├─ 01단계_프롬프트_mysqldb설계.txt
│  ├─ 02단계_프롬프트_결과1_db및사용자계정생성.txt
│  ├─ 02단계_프롬프트_결과2_create_table_insert만.txt
│  └─ 02단계_프롬프트_결과3_결과내용및테스트쿼리.txt
├─ frontend/
│  ├─ public/
│  │  ├─ favicon.svg
│  │  └─ icons.svg
│  ├─ src/
│  │  ├─ api/
│  │  │  ├─ admin.js
│  │  │  ├─ products.js
│  │  │  ├─ sellerOrders.js
│  │  │  └─ sellerProfile.js
│  │  ├─ assets/
│  │  ├─ components/
│  │  │  ├─ ProductCard.jsx
│  │  │  ├─ ProductDetail.jsx
│  │  │  ├─ ProductImageManager.jsx
│  │  │  └─ ProductList.jsx
│  │  ├─ pages/
│  │  │  ├─ admin/
│  │  │  │  ├─ AdminLayout.jsx
│  │  │  │  ├─ AiRagPage.jsx
│  │  │  │  ├─ CompanyPolicyForm.jsx
│  │  │  │  ├─ DocumentForm.jsx
│  │  │  │  ├─ OrgForm.jsx
│  │  │  │  ├─ OrgList.jsx
│  │  │  │  ├─ PolicyList.jsx
│  │  │  │  ├─ RefundPolicyForm.jsx
│  │  │  │  ├─ UserEditPanel.jsx
│  │  │  │  └─ UserList.jsx
│  │  │  ├─ orders/
│  │  │  │  └─ SellerOrderList.jsx
│  │  │  ├─ products/
│  │  │  │  ├─ ProductDetail.jsx
│  │  │  │  ├─ ProductForm.jsx
│  │  │  │  └─ ProductList.jsx
│  │  │  └─ seller/
│  │  │     └─ SellerProfile.jsx
│  │  ├─ styles/
│  │  │  ├─ admin.css
│  │  │  └─ product.css
│  │  ├─ App.jsx
│  │  ├─ App.css
│  │  ├─ index.css
│  │  └─ main.jsx
│  ├─ package.json
│  ├─ package-lock.json
│  └─ vite.config.js
├─ .gitignore
└─ README.md
```

> `.venv`, `node_modules`, `__pycache__` 등 로컬 실행 환경에서 생성되는 폴더는 프로젝트 구조 설명에서 제외했습니다.

## 실행 방법

### Backend

```powershell
cd backend
uv sync
.\.venv\Scripts\activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

FastAPI 문서:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

기본 개발 서버:

```text
http://localhost:5173
```

## Database

MySQL을 사용하며 초기 스키마 및 데이터는 다음 파일을 기준으로 구성합니다.

```text
database/shopdb2_schema_data.sql
```

백엔드 DB 접속 정보는 `backend/.env.example`을 참고하여 로컬 `.env`에 설정합니다.

## 브랜치 운영

- `main`: 최종 안정 버전
- `develop`: 팀원 작업 통합 브랜치
- 기능 개발 브랜치: 개별 기능 개발 후 Pull Request를 통해 `develop`에 병합

README의 프로젝트 구조와 구현 현황은 `develop` 브랜치를 기준으로 관리합니다.
