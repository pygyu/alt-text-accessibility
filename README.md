# 이미지 속 상품 정보를 읽을 수 있는 정보로

**시각장애인을 위한 온라인 쇼핑몰 대체 텍스트 자동 생성 AI**

2023 제1회 K-디지털플랫폼 AI 경진대회 · 4인 팀 프로젝트 · **최우수상(한국산업인력공단 이사장상)**

상품 이미지를 등록하면 OCR과 이미지 설명을 바탕으로 대체 텍스트 초안을 생성하고, 판매자가 확인·수정한 내용을 저장하여 상품 이미지의 `alt` 속성에 반영하는 Django 프로토타입입니다.

> 이 저장소는 2023년 해커톤 결과물을 포트폴리오용으로 정리한 코드입니다. 당시 사용한 외부 AI SDK와 API의 현재 호환성은 확인되지 않았습니다. 아래의 로컬 웹·DB 검증과 실제 Azure 호출의 검증 범위를 구분해 주세요.

## 왜 만들었나요?

온라인 쇼핑이 익숙한 일상이 되었지만, 이미지에 담긴 상품 정보는 화면 낭독기로 읽기 어렵다는 기사를 접했습니다. 대체 텍스트가 필요하다는 사실에서 한 걸음 더 나아가, 판매자가 이를 작성하는 수고를 줄일 수 있다면 어떨지 질문했습니다.

작성 부담을 문제의 한 요인으로 보고, 자동 생성한 초안을 사람이 검토하고 수정하는 방식을 구상했습니다. 비용과 번거로움이 미제공의 유일한 원인이라고 검증한 것은 아닙니다.

- [서울신문: 시각장애인의 온라인 쇼핑 어려움](https://www.seoul.co.kr/news/newsView.php?id=20230612500255)
- [NULI: 판매자 입장에서의 대체 텍스트 제공 방식 사례](https://nuli.navercorp.com/community/article/1133151)

## 어떻게 동작하나요?

1. 판매자가 상품 이미지를 업로드합니다.
2. Azure Vision에서 이미지 속 문자(OCR)와 이미지 설명(Dense Captions)을 추출합니다.
3. Azure OpenAI에 **추출된 텍스트**를 전달하여 한국어 설명 초안을 생성합니다.
4. 판매자가 상품명과 설명을 검토·수정합니다.
5. DB에 저장한 설명을 상품 상세 페이지의 이미지 `alt` 속성에 반영합니다.

GPT에 이미지를 직접 전달하는 구조가 아니라, Vision이 추출한 문자와 설명을 GPT가 종합하는 구조입니다. 화면 낭독은 사용자의 스크린리더가 담당하며, 자체 음성 합성 기능은 포함하지 않습니다.

## 본인 담당 — 박규현

팀이 함께 서비스 아이디어를 구체화하고 AI 처리·웹 화면을 구성했습니다. 저는 **DB 설계와 데이터 입출력, 웹 연동**을 담당했습니다.

| 담당 작업 | 코드에서 확인할 부분 |
| --- | --- |
| 이미지와 상품 정보를 연결하는 데이터 구조 | `home/models.py`, `home/migrations/` |
| 업로드 이미지 저장 및 생성 결과 저장 | `home/views.py`의 `upload` |
| 사용자가 수정한 상품명·대체 텍스트 저장 | `home/views.py`의 `review` |
| 저장 결과 조회와 상품 페이지 연결 | `main`, `detail`, `home/templates/home/` |

초기에는 화면을 순서대로 보여주는 발표 형식이었습니다. 실제로 작동하는 서비스까지 구현하자고 제안했고, 경험이 없던 DB·웹 연동을 맡았습니다. 연결이 되지 않는 문제에 부딪혔지만, 24시간 해커톤 동안 자료를 찾아보고 반복해서 시도하여 연동을 완성했습니다.

등록한 이미지와 생성된 설명이 DB에 저장되고 스크린리더로 읽히는 것을 확인했을 때, 아이디어가 실제 사용 가능한 흐름으로 이어졌음을 느꼈습니다. 팀은 최우수상을 수상했습니다. 개별 오류의 당시 로그는 남아 있지 않아, 구체적인 오류 원인이나 해결 순서를 사후에 만들어 기술하지 않았습니다.

## 코드 살펴보기

| 경로 | 설명 |
| --- | --- |
| `home/models.py` | `UploadedFile`과 `Goods` 모델, 외래키 관계 |
| `home/views.py` | 업로드·AI 호출·저장·수정·조회 |
| `home/urls.py` | 서비스 URL 연결 |
| `home/templates/home/` | 상품 목록, 업로드, 수정, 상세 화면 |
| `alt_text/my_settings.py` | 환경변수 기반 DB·키 설정 |
| `OCR/` | 당시 별도로 작성한 실험용 엔드포인트. 메인 흐름과 별개이며 구형 OpenAI 호출은 호환성 수정 필요 |

`UploadedFile`에는 이미지 파일 자체가 아니라 **파일 경로**가 저장됩니다. 파일은 `uploads/`에 보관하며, `Goods`가 이미지 레코드를 참조하고 상품명·대체 텍스트·생성/수정 시간을 저장합니다.

## 로컬 실행

### 1. 가상환경과 기본 패키지

당시 환경 기록은 Python 3.11.5, 프로젝트 생성 버전은 Django 4.2.5입니다. 배포용 최신화가 아니라 기존 구조를 보존한 개발 실행 안내입니다.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

macOS / Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

출력된 값을 `.env`의 `DJANGO_SECRET_KEY`에 작은따옴표로 감싸 넣습니다. `.env`는 Git에 올리지 않습니다.

### 2. DB 생성과 웹 실행

기본 DB는 별도 서버 없이 확인할 수 있는 SQLite입니다. 원래 프로젝트의 MySQL 계열 설정도 환경변수로 선택할 수 있도록 남겼습니다.

```bash
python manage.py migrate
python manage.py check
python manage.py runserver
```

Windows에서는 위 `python` 대신 `.\.venv\Scripts\python.exe`를 사용합니다.

접속 주소: **http://127.0.0.1:8000/home/**

기본 패키지만 설치해도 목록·업로드 화면을 열 수 있습니다. **이미지 업로드 후 AI 생성까지 실행하려면 다음 외부 서비스 설정이 필요합니다.** API 설정 없이 업로드하면 생성 단계에서 실패합니다.

### 3. 실제 AI 생성 연결 — 레거시 의존성

`requirements-ai-legacy.txt`는 원래 코드가 사용하는 `azure.ai.vision` 계열 SDK의 설치 후보를 분리한 파일입니다. 원본에 정확한 잠금 파일이 없어 당시 환경의 완전한 재현을 보장하지 않습니다.

```bash
python -m pip install -r requirements-ai-legacy.txt
```

`.env`에 본인의 Azure 리소스 설정을 입력합니다.

| 변수 | 용도 |
| --- | --- |
| `VISION_ENDPOINT`, `VISION_KEY` | Azure Vision 엔드포인트·키 |
| `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` | Azure OpenAI 엔드포인트·키 |
| `AZURE_OPENAI_DEPLOYMENT` | 본인이 생성한 배포 이름 |
| `AZURE_OPENAI_API_VERSION` | 해당 리소스에서 지원하는 API 버전 |

예제의 API 버전은 원본에 사용된 값입니다. 현재 서비스에서 지원하지 않으면 SDK·호출 코드를 함께 수정해야 합니다. 실제 호출에는 본인의 Azure 사용 요금이 발생할 수 있습니다.

MySQL을 사용하려면 서버에 빈 DB와 계정을 준비하고 `mysqlclient`를 설치한 뒤, `.env`의 `DB_ENGINE=mysql`과 `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`를 설정하고 `migrate`를 실행합니다. MySQL 연결은 이번 정리에서 재검증하지 않았습니다.

## 검증 범위와 한계

- 외부 AI 호출 없이 Django 설정과 SQLite 마이그레이션을 확인했습니다.
- AI 반환값을 임시 값으로 대체한 검증으로 이미지 저장, 생성 설명 저장, 수정 내용 저장, 상세 페이지 `alt` 반영을 확인했습니다.
- 실제 Azure 응답 품질, 현재 API 호환성, 실제 스크린리더 동작은 이번 정리에서 재검증하지 않습니다.
- 사용자 인증·권한, 파일 업로드 제한, API 실패 처리, 접근성 전반에 대한 검증은 추가 개발이 필요합니다. 공개 운영 서버로 바로 배포하기 위한 코드가 아닙니다.
- 자동 요약은 원재료·알레르기·규격 등의 정보를 누락하거나 잘못 표현할 수 있어 판매자의 검토가 필요합니다. 접근성 개선의 실제 효과를 입증하는 사용자 평가 자료는 포함하지 않습니다.

## 포트폴리오 공개를 위한 정리

원래 팀 작업과 이번 공개 준비를 구분하기 위해 변경 범위를 명시합니다.

- 하드코딩된 API 키·DB 인증정보·Django 비밀키를 제거하고 `.env.example` 제공
- 가상환경, 캐시, 로컬 DB, 업로드 이미지, 개인 실험 앱과 개인 경로 제거
- `.gitignore`, 기본 실행 의존성 및 README 추가
- 로컬 확인을 위한 SQLite 기본 설정 추가
- 업로드 파일 이름이 중복되어 바뀌어도 실제 저장 경로를 AI 처리에 전달하도록 수정
- 업로드 요청의 CSRF 검사 예외 제거

팀 프로젝트의 전체 저작권을 개인에게 귀속시키는 별도 라이선스는 추가하지 않았습니다. 포함된 외부 라이브러리의 저작권 고지는 유지했습니다.
