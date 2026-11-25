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

`_posts/2026-11-25-first-page.md`는 디자인을 확인할 수 있도록 넣은 시작 글입니다. 원하는 내용으로 수정하거나 삭제해도 됩니다. 블로그 제목과 소개 문구는 `_config.yml`에서 바꿀 수 있습니다.

## 프로젝트 추가하기

프로젝트마다 `_projects/my-project.md`처럼 파일을 하나 만드세요. 파일 이름은 상세 페이지 주소(`/projects/my-project/`)에 쓰입니다.

```markdown
---
title: 프로젝트 이름
topic: 주제
description: 프로젝트를 한 문장으로 소개하세요.
---

## 작업 과정

시작한 계기, 구현 과정, 결과를 적으세요.
관련 링크나 스크린샷도 여기에 넣을 수 있습니다.
```

메인에는 최대 두 개, 소개 페이지에는 모든 프로젝트가 표시됩니다. 요약을 클릭하면 본문이 열립니다.

## 소개 페이지 채우기

수상, 경력, 학력은 `_data/cv.yml`에서 관리합니다.

```yaml
awards:
  - year: "2026"
    title: 수상 이름
    organization: 주최 기관
    description: 짧은 설명
    url: https://example.com
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
