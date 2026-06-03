# ChangeLens

ChangeLens는 빠르게 변하는 기술 뉴스를 읽고, 개인 인사이트와 다음 행동을 기록하기 위한 웹 애플리케이션입니다.

## 과제 맥락

이 저장소는 오픈소스 개론 과제 5를 위한 프로젝트 저장소입니다.

본 과제는 조기 취업 공결로 인해 개인 과제로 진행되며, Git/GitHub 브랜치 전략과 Pull Request 기반 협업 흐름을 체험하는 데 중점을 둡니다.

## 현재 상태

Vue + FastAPI 기반 프로젝트 초기 구조를 구성했습니다.

현재 프론트엔드는 프로젝트 초기 실행 확인을 위해 `Hello World` 화면만 제공합니다.

## 기술 스택

- Frontend: Vue + Vite
- Backend: FastAPI
- Runtime: Docker Compose

## 프로젝트 구조

```text
changeLens/
  frontend/
  backend/
  docker-compose.yml
  README.md
```

## 실행 방법

Docker가 설치되어 있다면 다음 명령으로 프론트엔드와 백엔드를 함께 실행할 수 있습니다.

```bash
docker compose up --build
```

실행 후 접속 주소:

- Frontend: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`
- Backend Health Check: `http://localhost:8000/health`
