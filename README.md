# arecia

GitHub Pages와 Jekyll로 운영하는 블로그와 소개 페이지 템플릿입니다.

사이트에 표시되는 닉네임은 `arecia`이며, 저장소와 GitHub Pages 주소에는 `areciah`를 사용합니다.

## 글 쓰기

`_posts` 폴더에 `YYYY-MM-DD-제목.md` 형식의 파일을 만드세요.

```markdown
---
layout: post
title: "새 글 제목"
description: "목록에 표시할 짧은 소개"
date: 2026-11-25
category: 기록
---

본문을 여기에 작성합니다.
```

예시 글 ‘요청 ID와 로그 분석’은 Notion에서 관리합니다. 블로그 제목과 소개 문구는 `_config.yml`에서 바꿀 수 있습니다.

Markdown 글 주소는 `/posts/파일이름/`입니다(날짜 접두사 제외). 글 상단에 `slug: request-id-logs`처럼 고정 이름을 지정할 수도 있습니다.

## 프로젝트 추가하기

프로젝트마다 `_projects/my-project.md`처럼 파일을 하나 만드세요. 파일 이름은 상세 페이지 주소(`/projects/my-project/`)에 쓰입니다.

```markdown
---
title: 프로젝트 이름
topic: 주제
description: 프로젝트를 한 문장으로 소개하세요.
role: 직접 맡은 기능이나 업무 (선택)
---

## 작업 과정

시작한 계기, 구현 과정, 결과를 적으세요.
관련 링크나 스크린샷도 여기에 넣을 수 있습니다.
```

메인에는 최대 두 개, 프로젝트 목록(`/projects/`)과 소개 페이지에는 모든 프로젝트가 표시됩니다. 요약을 클릭하면 본문이 열립니다.

## 소개 페이지 채우기

수상, 외부활동, 경력, 학력은 `_data/cv.yml`에서 관리합니다.

```yaml
awards:
  - year: "2026"
    title: 수상 이름
    organization: 주최 기관
    description: 짧은 설명
    role: 직접 맡은 업무 (선택)
    url: https://example.com
activities:
  - title: 활동 이름
    period: "2026.03–06"
    organization: 활동 기관 또는 모임
    description: 활동 소개
    role: 직접 맡은 업무 (선택)
experience:
  - period: "2025–현재"
    role: 역할
    organization: 소속
    description: 담당한 일
education:
  - period: "2022–2026"
    school: 학교
    detail: 전공 또는 학위
```

상단의 `name`, `headline`, `summary`, `links`도 같은 파일에서 바꿀 수 있습니다. 소개 페이지의 인쇄 버튼으로 PDF 저장이 가능합니다.

## 로컬에서 확인하기

Jekyll이 설치되어 있다면 저장소 루트에서 `jekyll serve`를 실행하세요. GitHub Pages에 올리면 별도 빌드 설정 없이 게시됩니다.

처음 방문하면 터미널 인트로가 한 번 표시됩니다. 인트로를 다시 확인하려면 새 브라우저 세션을 열거나 해당 사이트의 세션 저장소를 비우세요.

첫 화면에는 화면 크기와 픽셀 밀도에 따라 `assets/hero-archive.gif`, `assets/hero540.gif`, `assets/hero1080.gif` 중 하나가 표시됩니다. 이미지는 CSS로 천천히 회전합니다. 움직임 줄이기 설정에서는 `assets/hero-archive.png`가 대신 표시됩니다.

## Notion 자동 발행

1. Notion 데이터베이스에 제목 속성과 **상태**(상태 타입, 옵션 이름 `발행`)를 만드세요. 선택 속성은 **발행일**(날짜, 기본값은 페이지 생성일), **카테고리**(글의 분야, 다중 선택), **태그**(세부 키워드, 다중 선택), **요약**(텍스트)입니다.
2. Notion에서 읽기 권한을 가진 내부 연결을 만들고 데이터베이스의 연결 메뉴에서 추가하세요. 데이터베이스 링크에서 경로 끝의 **데이터베이스 ID**를 복사하세요. 링크의 `?v=` 뒤에는 뷰 ID가 들어갑니다.
3. GitHub 저장소의 **Settings → Secrets and variables → Actions**에서 두 값을 Repository secrets에 등록하세요. `NOTION_TOKEN`은 Notion 읽기 토큰이고, `DATABASE_ID`는 단일 데이터 소스를 가진 블로그 데이터베이스의 ID입니다. GitHub Pages 배포에는 Actions 기본 토큰을 사용합니다.
4. 변경 사항을 기본 브랜치 main에 푸시하고 **Settings → Pages → Source → GitHub Actions**를 선택하세요. **Actions → Publish Notion and Jekyll → Run workflow**로 첫 배포를 확인할 수 있습니다.

이후 Notion에서 상태를 **발행**으로 바꾸면 15분 주기의 다음 실행에서 블로그가 빌드됩니다. GitHub 실행 대기 시간만큼 늦어질 수 있습니다. 발행된 글의 수정도 반영되고, 상태를 초안으로 되돌리면 다음 성공한 배포에서 내려갑니다. Notion 글 주소는 `/posts/제목-짧은ID/` 형식입니다. 제목을 고쳐도 주소를 유지하려면 첫 발행 전에 텍스트 속성 `주소`에 고정 이름을 넣으세요. 기존 페이지 ID 주소도 새 주소로 연결됩니다. 매 실행은 새 체크아웃에서 시작하며, 기존 Markdown 글도 함께 빌드합니다.

### 비밀번호로 발행하는 글

Notion에서 글마다 `글 비밀번호`를 입력하고 상태를 `발행 (비밀번호)`로 선택하세요. 이 상태에는 비밀번호가 필수입니다. 메인과 목록에 제목과 잠금 표시가 나오고 상세 페이지에서 비밀번호를 입력하면 본문을 읽을 수 있습니다. 기존 `비공개` 상태는 목록에도 올라가지 않습니다.

배포에는 암호화된 본문이 포함되므로 글마다 길고 추측하기 어려운 비밀번호를 사용하세요. Notion 데이터베이스를 공유받은 사람은 비밀번호 속성을 볼 수 있습니다. 암호화 범위는 본문 텍스트이며 외부 링크나 첨부 파일 자체의 접근 권한은 해당 서비스에서 관리합니다. 이미 공개했던 글의 이전 사본은 회수할 수 없습니다.
