# ChangeLens

ChangeLens는 빠르게 변하는 기술 뉴스를 확인하고, 관심 있는 뉴스를 개인 인사이트와 함께 저장하는 웹 애플리케이션입니다.

개인 과제 환경에서 GitHub Flow, 브랜치 전략, Pull Request, 코드 리뷰 반영 과정을 체험하는 것을 목표로 합니다.

## 주요 기능

- GeekNews RSS 기반 최신 기술 뉴스 목록 조회
- 뉴스 본문 미리보기와 발행 시간 표시
- 관심 뉴스 저장 시 인사이트 작성
  - 영향도: `Low`, `Medium`, `High`
  - 해석
  - 다음 행동
- 내 저장 목록 조회
  - 저장한 뉴스
  - 작성한 인사이트
  - 영향도
  - 저장 시간
- 저장한 인사이트 삭제
- 뉴스 조회, 저장 목록 조회, 저장, 삭제의 로딩/에러/빈 상태 처리

## 기술 스택

- Frontend: Vue 3, Vite
- Backend: Python 3.12, FastAPI, Uvicorn
- RSS Parser: feedparser
- Runtime: Docker Compose
- Storage: 서버 메모리 기반 FakeDB

## 프로젝트 구조

```text
changeLens/
  backend/
    app/
      main.py
      models.py
      services/
    tests/
    Dockerfile
    requirements.txt
  frontend/
    src/
      App.vue
      main.js
      style.css
    Dockerfile
    package.json
  docker-compose.yml
  README.md
```

## 실행 전 준비

Docker 실행을 권장합니다.

필수:

- Docker Desktop
- Docker Compose

선택 로컬 실행 시 필요:

- Node.js 22.12 이상 또는 Vite 요구사항을 만족하는 Node.js
- Python 3.12

## Docker로 실행하기

저장소 루트에서 실행합니다.

```bash
docker compose up --build
```

실행 후 접속 주소:

- Frontend: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`
- Backend Health Check: `http://localhost:8000/health`

종료:

```bash
docker compose down
```

## 코드 컴파일 및 검증

### Frontend 빌드

Docker 환경에서 Vite production build를 실행합니다.

```bash
docker compose run --rm --no-deps frontend npm run build
```

### Backend 테스트

Docker 환경에서 백엔드 unittest를 실행합니다.

```bash
docker compose run --rm --no-deps backend python -m unittest discover tests
```

## 로컬 개발 실행

Docker 없이 실행하려면 프론트엔드와 백엔드를 각각 실행합니다.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8000 npm run dev -- --host 0.0.0.0
```

Frontend 접속 주소:

```text
http://localhost:5173
```

## 사용 방법

1. `http://localhost:5173`에 접속합니다.
2. 최신 기술 뉴스 목록을 확인합니다.
3. 관심 있는 뉴스의 `저장` 버튼을 누릅니다.
4. 인사이트 작성 창에서 영향도, 해석, 다음 행동을 입력합니다.
5. 저장하면 `내 저장 목록`에서 저장한 뉴스와 작성한 인사이트를 확인할 수 있습니다.
6. 저장 목록에서 필요 없는 항목은 `삭제` 버튼으로 제거할 수 있습니다.

## 주요 API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | 백엔드 상태 확인 |
| `GET` | `/api/news` | GeekNews 기반 최신 뉴스 목록 조회 |
| `GET` | `/api/insights` | 저장한 인사이트 원본 목록 조회 |
| `GET` | `/api/saved-news` | 내 저장 목록 조회 |
| `POST` | `/api/insights` | 뉴스와 인사이트 저장 |
| `DELETE` | `/api/insights/{insight_id}` | 저장한 인사이트 삭제 |

## 데이터 저장 방식

현재 MVP는 별도 데이터베이스를 사용하지 않고, 백엔드 프로세스 메모리에 데이터를 저장합니다.

따라서 다음 동작은 의도된 제한 사항입니다.

- 브라우저 새로고침 후에도 백엔드 컨테이너가 살아 있으면 저장 목록은 유지됩니다.
- `docker compose down` 또는 백엔드 재시작 후에는 저장 데이터가 초기화됩니다.
- 영구 저장이 필요하면 SQLite 같은 파일 기반 저장소를 추가해야 합니다.

## 과제 진행 방식

이 프로젝트는 개인 과제지만 협업 흐름을 시뮬레이션하기 위해 GitHub Flow를 사용했습니다.

- 기능 단위 브랜치 생성
- Pull Request 생성
- CodeRabbit 기반 코드 리뷰 확인
- 반영할 리뷰와 반영하지 않을 리뷰를 판단
- 리뷰 반영 커밋 추가
- PR 머지 후 다음 작업 진행

