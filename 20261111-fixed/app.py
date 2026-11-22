# App documentation omitted from visible UI.
import sys as _sys
import types as _types
# Assets and helper modules are kept as ordinary project files rather than embedded
# as multi-megabyte strings. This makes deployment and future debugging easier.
from pathlib import Path as _Path
_ASSET_DIR = _Path(__file__).parent / "assets"
_APP_ASSETS = {p.name: base64.b64encode(p.read_bytes()).decode("ascii")
               for p in _ASSET_DIR.glob("*.png")}
import courseware, features, design, services
_SETUP_DOC = '두 파일 버전: app.py와 requirements.txt만 올리면 됩니다. 별도 이미지나 모듈 파일은 필요 없습니다. 아래 폴더 설명은 내부 구성에 대한 참고이며 모두 app.py에 포함되어 있습니다.\n\n# 앱잘알 — 스마트폰 배우기 · 가족과 소통하기\n\n앞서 만든 앱잘알 로고, 사용자가 제공한 고양이 화면의 캐릭터 영역, ‘열기’ 시작 화면을 포함한 Streamlit 확장판입니다. 상용 출시를 지향하는 개발용 소스이며 실제 운영·보안·접근성 인증이 완료된 제품은 아닙니다.\n\n## 폴더와 실행\n\n```text\napp.py          공통 디자인·홈·학습·사진·가족 CSV·진도·50개 언어 UI\ncourseware.py   추가 21개 한국어 교육 과정과 문제\nfeatures.py     인증 화면·가상 연습·음성·퀴즈·질문 도우미\nservices.py     Supabase 인증/진도 저장·선택형 외부 AI 연결\nassets/         logo.png, icon.png, character.png\nschema.sql      본인 기록만 읽고 쓰는 RLS 정책\nrequirements.txt\n.streamlit/config.toml\nsecrets.example.toml  설정 예제 (진짜 키를 적어 GitHub에 올리지 마세요)\n```\n\nPython 3.11 또는 3.12를 권장합니다.\n\n```bash\npip install -r requirements.txt\nstreamlit run app.py\n```\n\n## GitHub → Streamlit Community Cloud\n\n1. GitHub에 저장소를 만들고 **이 폴더의 내용 전체**를 올립니다. app.py뿐 아니라 모듈과 assets 폴더도 필요합니다.\n2. 실제 비밀번호, .streamlit/secrets.toml, DB 연결 키, 이용자 CSV를 올리지 마세요. .gitignore가 포함되어 있습니다.\n3. Streamlit에서 GitHub 저장소와 브랜치를 선택하고 실행 파일을 `app.py`로 지정합니다.\n4. Python 버전을 지원되는 3.11/3.12로 설정하고 배포합니다.\n5. 처음에는 ‘열기’ → 계정 화면으로 이동합니다. Supabase 미연결이면 ‘체험 시작하기’를 누릅니다. 로딩 점은 준비 상태 애니메이션이며 실제 다운로드 진행률이 아닙니다. 자동으로 넘기지 않고 사용자가 열기를 누르는 방식을 유지했습니다.\n6. Supabase 연결은 앱의 Secrets 설정에 아래 값을 넣습니다. 로컬은 .streamlit/secrets.toml에 저장합니다.\n\n```toml\nSUPABASE_URL = "https://YOUR_PROJECT.supabase.co"\nSUPABASE_ANON_KEY = "YOUR_PUBLIC_ANON_KEY"\n```\n\n`service_role` 또는 프로젝트 secret key는 사용하지 마세요. 이 앱은 로그인한 사용자의 토큰과 RLS로 접근을 제한합니다.\n\n## Supabase 설정\n\n1. 본인의 Supabase 프로젝트를 생성합니다. 이용 한도·이메일 발송 한도·비용은 계정의 현재 제공 조건을 확인하세요. 유료 플랜을 자동 신청하는 코드는 없습니다.\n2. SQL Editor에서 `schema.sql` 전체를 실행합니다. RLS가 켜져 있어야 합니다. 다른 사람의 user_id로 읽고 쓰기가 거부되는지 별도 사용자 2개로 테스트하세요.\n3. Authentication에서 이메일/비밀번호 로그인을 활성화하고 이메일 확인을 유지합니다. 아이디는 **이메일**입니다. 앱 자체가 비밀번호를 CSV나 DB 테이블에 저장하지 않습니다.\n4. Auth URL 설정의 Site URL과 허용 리디렉션 URL에 실제 배포 주소를 설정합니다.\n5. 이메일 확인 템플릿은 Supabase 기본 확인 링크를 사용할 수 있습니다. 메일 인증 후 앱에서 로그인합니다. 운영용 이메일 전송은 SMTP 발송 설정과 한도를 검토하세요.\n6. **비밀번호 복구 메일 템플릿**에는 `{{ .Token }}`을 포함하여 복구 코드를 보여 주세요. 사용자가 앱의 ‘비밀번호 찾기’에서 이메일·코드·새 비밀번호를 입력하면 recovery OTP 검증 후 변경합니다. 코드의 유효기간과 재시도 제한은 Supabase 설정을 따릅니다. 이 화면은 기본 복구 링크만 있는 템플릿으로는 완성되지 않으므로 토큰 템플릿 설정이 필요합니다.\n7. 회원가입 → 메일 확인 → 로그인 → 학습 완료 → 로그아웃 → 재로그인 순서로 저장 여부를 확인하세요. 로그인 시 로그인 계정의 학습 데이터로 바꾸며 다른 계정의 가족 메시지는 비웁니다.\n\n### 저장 범위\n\n- 계정 연동: 완료 학습, 단계, 즐겨찾기, 퀴즈 결과, 표시 이름, 최근 학습. 로그인 상태는 **현재 Streamlit 접속 세션** 동안 유지합니다. 서비스 장애·새 접속·브라우저 종료 후에는 재로그인이 필요할 수 있습니다. 비밀번호를 저장하는 장기 로그인 쿠키는 구현하지 않았습니다.\n- 가족 사진/대화: 기존 **CSV 교환 방식**을 유지합니다. 실시간 채팅이 아닙니다. 서버의 가족 공유 테이블을 만들거나 다른 사용자에게 자동 공개하지 않습니다.\n- CSV: 사진·메시지·기존 학습 진행을 백업합니다. 추가 퀴즈/즐겨찾기도 확장 메타데이터로 저장합니다. 계정 비밀번호/토큰은 포함하지 않습니다. CSV는 암호화되지 않습니다.\n- 기기별 최근 변경 충돌을 병합하는 협업 서버는 아닙니다. 동일 계정의 동시 학습은 나중 저장이 앞선 상태를 덮어쓸 수 있습니다.\n- 계정 삭제 기능은 제공하지 않습니다. 실제 서비스에서는 운영자가 본인 확인 후 Supabase 사용자 삭제 및 데이터 삭제 절차를 마련해야 합니다.\n\n## 교육 기능\n\n기존 앱 설치·회원가입·로그인·화면 사진·와이파이 5개와 추가 21개, 총 26개 과정입니다. 스마트폰 기본, 생활 속 활용, 금융·보안으로 분류되며 모든 과정은 한 단계씩 진행합니다. 기종과 앱 버전에 따라 화면이 다르다는 점을 안내합니다. 금융, 민원, 모바일 신분증은 일반적인 사용/안전 교육이며 현재의 법적 요건·발급 대상·금융 상품을 검증한 안내는 아닙니다. 실제 서비스의 공식 안내를 확인해야 합니다.\n\n가상 문자·샘플 사진 첨부·연락처 저장/삭제·가상 전화·설정 화면·송금 확인을 연습할 수 있습니다. 실제 전화, 문자, 송금, 결제, 예약, 민원, 신분증 발급은 발생하지 않습니다. 실제 연락처나 카드번호를 입력하지 마세요. 모의 기기는 Streamlit 위젯 기반이며 실제 Android/iOS 화면을 복제하거나 기기를 제어하지 않습니다.\n\n카테고리별 객관식 21문제와 재도전 기능을 제공합니다. 퀴즈는 추가 21개 과정 기준이며 기존 5개 과정의 별도 퀴즈는 없습니다. 음성은 브라우저 Web Speech 기능으로 한국어 단계를 읽습니다. 음성 종류·네트워크 사용 여부는 기기/브라우저 정책에 따릅니다. 음성 버튼은 사용자가 직접 눌러야 하며 한국어 음성이 없거나 iframe 정책이 막는 환경에서는 사용할 수 없습니다.\n\n## 언어 지원과 한계\n\n- 기존 50개 언어 선택, 페이지 간 선택 유지, 중국어 간체/번체 구분, 아랍어·히브리어 등의 RTL 및 폰트 대체를 유지했습니다.\n- 기존 공통 UI와 새 메뉴의 한국어/영어 사전은 코드 안에 있습니다. 나머지 48개는 deep-translator의 공개 온라인 번역을 사용하므로 API 키는 없지만 차단·속도 제한·번역 오류가 발생할 수 있습니다. 실패 시 영어임을 안내합니다. 유료 번역 API 자동 결제 코드는 없습니다.\n- **26개 학습 본문, 퀴즈, 가상 연습, 계정 관리의 상세 문구는 현재 한국어입니다.** 이 페이지에는 한국어 콘텐츠 안내를 표시합니다. 50개 언어로 앱 전체가 전문 번역되었다고 표시하지 않습니다. Streamlit 기본 파일 업로드/카메라 도구의 시스템 문구도 브라우저에서 완전히 번역되지 않을 수 있습니다.\n- Pretendard와 Google Fonts 대체 글꼴을 온라인으로 가져옵니다. 외부 폰트가 막히면 기기 기본 글꼴로 보입니다. 로고의 한국어는 브랜드 이미지라 번역하지 않습니다.\n\n## 질문 도우미와 선택형 AI\n\n기본 질문 도우미는 무료 **키워드 검색**입니다. 학습 자료에서 연관된 과정을 보여 주며 생성형 AI처럼 표시하지 않습니다. 의미 검색/진단을 하는 기능은 아닙니다.\n\n외부 AI가 필요한 경우 관리자가 별도 제공자와 계약한 뒤 Secrets에 세 값을 모두 설정할 수 있습니다.\n\n```toml\nAI_CHAT_URL = "https://YOUR_PROVIDER/v1/chat/completions"\nAI_API_KEY = "YOUR_PRIVATE_KEY"\nAI_MODEL = "YOUR_CHOSEN_MODEL"\n```\n\nOpenAI 호환 chat completions JSON 규격을 지원하는 HTTPS 주소를 사용합니다. 특정 공급자를 기본 연결하지 않습니다. 사용자가 외부 AI 사용을 직접 선택해야 질문과 관련 학습 자료가 전송됩니다. 사진·가족 메시지·계정 비밀번호는 AI로 보내지 않습니다. AI 제공자 비용이 발생할 수 있으며 운영자가 한도·남용 방지·요금 정책을 정해야 합니다. 실패하면 검색 결과를 제공합니다. 실제 AI 서비스 호출은 본 패키지 제작 중 검증하지 않았습니다.\n\n## 운영 전 필수 확인\n\n이 패키지는 실제 Supabase 프로젝트나 AI 키를 제공받지 않은 상태에서 작성했습니다. 인증·복구 메일·RLS 격리·실제 DB 저장·외부 AI·외부 48개 언어 번역·휴대폰 음성·카메라 권한은 배포 환경에서 직접 확인해야 합니다. 코드 검사/모의 실행을 실제 상용 서비스 검수로 보지 마세요.\n\n- 휴대폰·PC에서 큰 글씨/줄바꿈/버튼/접이식 메뉴와 하단 메뉴\n- 가족 사진의 개인정보 가림과 CSV 재업로드, 다운로드 가능한 크기\n- 메일 확인과 OTP 복구, 만료 세션, 다른 계정 간 데이터 분리\n- 네트워크 중단 시 저장 오류, 무료 한도 초과 시 동작\n- 접근성 리더·키보드·음성 지원과 50개 언어 번역 품질\n- 실제 이용약관·개인정보 처리방침·보관기간·삭제 요청·백업 정책·보안 모니터링\n\n제공된 캐릭터는 업로드된 화면에서 잘라 포함했습니다. 원본 투명 PNG가 있으면 `assets/character.png`만 교체할 수 있습니다. 외형을 새로 그리지 않았습니다. 아이콘은 앞서 만든 로고의 심벌 영역을 잘라 512px 정사각형으로 맞춘 파일입니다.\n\n\n## 이번 디자인 확장 반영\n\n- 기존 앱잘알 로고와 열기 시작 화면을 유지했습니다. 새 지침에 따라 스마트폰을 든 중년 사람 안내자 이미지를 `assets/human_guide.png`로 추가하여 기본 홈 캐릭터로 사용합니다. 이전 고양이는 `assets/character.png`로 보존했습니다.\n- 색상·버튼 높이·모서리·글씨 크기·화면 폭을 `design.py`의 TOKENS 및 css()에서 관리합니다. 기존 세부 CSS는 app.py에 남아 있으므로 디자인 전체가 완전히 단일 파일로 분리된 상태는 아닙니다.\n- 홈에 주제별 학습 목록, 연습 강조 영역, 추천 학습, 이어보기 영역을 배치했습니다. 하단은 홈·배우기·연습·질문·마이페이지 5개입니다. 질문 메뉴는 기본 검색 도우미이며 설정 없이 실제 생성형 AI라고 표시하지 않습니다.\n- 상세 학습의 ‘단계 그림과 설명 다시 보기’에는 현재 단계 위치를 보여주는 휴대폰 개념 그림과 같은 단계 설명이 있습니다. 실제 문자 앱 버튼 위치 등을 복제한 화면 캡처는 아닙니다.\n- 쉬운 설명 모드는 문장을 줄 단위로 나누는 기능입니다. 개인별 난이도를 자동 분석하거나 새로운 내용을 생성하지 않습니다.\n- 동영상 촬영 과정 1개가 추가되어 총 26개 과정과 21문제입니다. 퀴즈의 전체 문제 수는 추가 과정 기준입니다.\n- 마이페이지는 체험 상태에서도 학습 요약과 환경 설정으로 연결됩니다. 계정 저장 기능은 Supabase 설정 후 이용합니다. 현재 세션 유지와 브라우저 재시작 후 장기 로그인 유지는 다릅니다.\n- 모바일 대응 CSS는 작성했으나 실제 스마트폰 브라우저 확인은 수행하지 못했습니다. 브라우저 UI가 완성도 목표에 도달했는지는 실제 기기에서 별도 검수해야 합니다.\n'
_SETUP_SQL = "-- Run in Supabase SQL Editor using your project-owner account.\n-- Never put the service_role / secret key in this app.\ncreate table if not exists public.learning_state (\n  user_id uuid primary key references auth.users(id) on delete cascade,\n  payload jsonb not null default '{}'::jsonb,\n  updated_at timestamptz not null default now(),\n  constraint small_learning_payload check (octet_length(payload::text) < 200000)\n);\nalter table public.learning_state enable row level security;\nrevoke all on public.learning_state from anon;\ngrant select, insert, update, delete on public.learning_state to authenticated;\ndrop policy if exists own_state_select on public.learning_state;\ncreate policy own_state_select on public.learning_state for select to authenticated using ((select auth.uid()) = user_id);\ndrop policy if exists own_state_insert on public.learning_state;\ncreate policy own_state_insert on public.learning_state for insert to authenticated with check ((select auth.uid()) = user_id);\ndrop policy if exists own_state_update on public.learning_state;\ncreate policy own_state_update on public.learning_state for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);\ndrop policy if exists own_state_delete on public.learning_state;\ncreate policy own_state_delete on public.learning_state for delete to authenticated using ((select auth.uid()) = user_id);\ncreate or replace function public.set_learning_updated_at() returns trigger language plpgsql set search_path=public as $$\nbegin new.updated_at = now(); return new; end; $$;\ndrop trigger if exists learning_updated_at on public.learning_state;\ncreate trigger learning_updated_at before update on public.learning_state for each row execute function public.set_learning_updated_at();\n"
# App documentation omitted from visible UI.
from pathlib import Path
import base64
import csv
import html
import io
import json
import uuid
from datetime import datetime, timezone
from PIL import Image, ImageOps
import streamlit as st
# No online translator is imported.
from courseware import EXTRA,CATEGORIES
import features
import design
import services

st.set_page_config(page_title="앱잘알", page_icon="📱", layout="centered", initial_sidebar_state="collapsed")
LANGUAGES = [
('ko','한국어'),('en','English'),('ja','日本語'),('zh-CN','简体中文'),('zh-TW','繁體中文'),
('es','Español'),('fr','Français'),('de','Deutsch'),('it','Italiano'),('pt','Português'),
('ru','Русский'),('ar','العربية'),('hi','हिन्दी'),('vi','Tiếng Việt'),('th','ไทย'),
('id','Bahasa Indonesia'),('ms','Bahasa Melayu'),('tl','Filipino'),('my','မြန်မာ'),('km','ខ្មែរ'),
('lo','ລາວ'),('mn','Монгол'),('ne','नेपाली'),('bn','বাংলা'),('ur','اردو'),('fa','فارسی'),
('tr','Türkçe'),('nl','Nederlands'),('sv','Svenska'),('no','Norsk'),('da','Dansk'),('fi','Suomi'),
('pl','Polski'),('cs','Čeština'),('sk','Slovenčina'),('hu','Magyar'),('ro','Română'),('bg','Български'),
('el','Ελληνικά'),('uk','Українська'),('iw','עברית'),('sw','Kiswahili'),('af','Afrikaans'),
('ta','தமிழ்'),('te','తెలుగు'),('mr','मराठी'),('pa','ਪੰਜਾਬੀ'),('si','සිංහල'),('kk','Қазақша'),('uz','O‘zbekcha')]
TEXT = {
'home':'홈','learn':'따라 하며 배우기','photo':'사진으로 물어보기','chat':'가족과 대화하기',
'record':'내 학습 이어가기','settings':'언어와 데이터 설정','title':'모르는 게 생겼나요?',
'subtitle':'앱잘알에게 물어보세요','intro':'스마트폰 사용부터 가족과의 대화까지, 천천히 함께해요.',
'search':'무엇을 도와드릴까요?','search_hint':'예: 앱 설치, 로그인, 회원가입','results':'찾은 학습',
'none':'찾는 내용이 없어요. 가족에게 사진으로 물어보세요.','progress':'차근차근, 잘하고 있어요',
'complete':'완료한 학습','total':'전체 학습','continue':'이어서 배우기','start':'앱잘알 시작하기',
'welcome':'스마트폰과 조금 더 가까워지는 시간','back':'홈으로','next':'다음 단계','prev':'이전 단계',
'done':'학습 완료하기','step':'단계','content_note':'학습 본문은 한국어로 제공됩니다. UI 언어와 별개이며 번역된 학습 자료가 아닙니다.',
'choose':'배울 내용을 골라 주세요','upload':'사진 선택','camera':'카메라로 찍기','message':'전하고 싶은 말',
'name':'보내는 사람 이름','send':'가족에게 남기기','saved':'저장했어요. CSV를 내려받아 가족에게 전달해 주세요.',
'privacy':'비밀번호, 인증번호, 주민등록번호, 계좌 정보는 가린 뒤 공유하세요.',
'csv_note':'실시간 채팅이 아닙니다. CSV 파일을 가족에게 보내고 받은 파일을 불러오면 대화를 이어갈 수 있어요.',
'empty':'아직 남긴 내용이 없어요. 첫 이야기를 남겨 보세요.','validation':'이름과 메시지 또는 사진을 입력해 주세요.',
'export':'기록 CSV 내려받기','import':'가족에게 받은 CSV 불러오기','import_button':'기록 합치기',
'import_ok':'기록을 합쳤어요. 같은 기록은 중복으로 넣지 않았어요.','invalid':'파일을 읽을 수 없어요. 앱잘알에서 받은 CSV인지 확인해 주세요.',
'limit':'파일은 15MB 이하, 사진은 8MB 이하로 올려 주세요.','photo_bad':'사진을 읽을 수 없어요. JPG 또는 PNG 파일을 사용해 주세요.',
'language':'사용할 언어','data':'내 기록 보관하기','volatile':'기록은 현재 접속 중에만 보관됩니다. 새로고침하거나 접속을 종료하기 전에 CSV를 내려받으세요.',
'backup_notice':'CSV에는 사진과 대화가 포함되며 암호화되지 않습니다. 믿을 수 있는 가족에게만 전달하세요.',
'recent':'최근 가족 이야기','photo_help':'막힌 화면을 올리고, 어떤 부분이 어려운지 적어 주세요. 가족이 CSV로 받아 답변할 수 있어요.',
'photo_no_ai':'사진을 자동 분석하거나 답변하는 기능은 아닙니다.','history':'학습 기록','not_started':'아직 완료한 학습이 없어요.',
'open':'학습 열기','reset':'학습 처음부터 보기','brand':'쉽게 배우고, 따뜻하게 연결되는 곳',
'assets':'원본 캐릭터 추가','assets_note':'스마트폰을 든 사람 안내자를 기본으로 사용해요. 기존 고양이 원본도 assets 폴더에 보관했습니다. 다른 원본 이미지를 올리면 현재 접속 동안 추가할 수 있어요.',
'cream':'크림색 캐릭터 원본','cat':'고양이 캐릭터 원본','font':'글씨 크기','normal':'크게','large':'더 크게',
'auto_note':'UI 문구는 온라인 자동 번역이며 오류가 있을 수 있습니다. 사용자 메시지와 학습 본문은 번역하지 않습니다.',
'no_search':'검색어를 입력하면 관련 한국어 학습을 찾아드려요.','required_photo':'공유할 사진을 먼저 선택해 주세요.',
'menu':'메뉴','translation_status':'UI 번역 상태','online_status':'온라인 자동 번역','built_in_status':'내장 번역','fallback_status':'번역을 불러오지 못해 영어 UI로 표시 중입니다.','translation_info':'한국어와 영어는 내장 사전을 사용합니다. 다른 48개 언어는 키 없이 공개 웹 번역을 이용하며, 이 코드에는 유료 API나 결제 설정이 없습니다. 인터넷 연결과 제공자 정책에 따라 번역이 지연되거나 제한될 수 있습니다. 사용자 사진과 메시지는 번역 서비스로 보내지 않습니다.','search_content_status':'학습 자료는 한국어로 제공됩니다. 검색 결과가 없다면 사진 도움을 이용해 주세요.','learn_hint':'한 단계씩, 내 속도로 배워요','photo_hint':'막힌 화면을 가족에게 보여 주세요','chat_hint':'안부와 도움을 따뜻하게 나눠요','record_hint':'배우던 곳부터 다시 시작해요','retry_translation':'번역 다시 시도','storage_full':'기록이 많아졌어요. CSV 백업 후 새 접속에서 이어가 주세요.','updated':'설정을 적용했어요.','all':'전체','finish_note':'완료 기록도 CSV에 함께 저장됩니다.'}
# Centralized dictionaries: no user content is sent to the translation provider.
ENGLISH = dict(line.split('|', 1) for line in "home|Home\nlearn|Learn step by step\nphoto|Ask with a photo\nchat|Talk with family\nrecord|Continue learning\nsettings|Language and data\ntitle|Something you don't know?\nsubtitle|Ask APP잘알\nintro|From using your phone to talking with family, let's take it one step at a time.\nsearch|What would you like help with?\nsearch_hint|Try: install an app, log in, sign up\nresults|Lessons found\nnone|No lesson found. Ask your family with a photo.\nprogress|Little by little, you are doing well\ncomplete|Lessons completed\ntotal|All lessons\ncontinue|Continue learning\nstart|Get started\nwelcome|Feel a little more at home with your smartphone\nback|Back to home\nnext|Next step\nprev|Previous step\ndone|Complete lesson\nstep|Step\ncontent_note|Lesson content is available in Korean only. The selected language applies to the interface, not to lesson translations.\nchoose|Choose a lesson\nupload|Choose a photo\ncamera|Take a photo\nmessage|Your message\nname|Sender name\nsend|Save for family\nsaved|Saved. Download the CSV and share it with your family.\nprivacy|Hide passwords, verification codes, identity numbers and banking details before sharing.\ncsv_note|This is not live chat. Send the CSV to your family and import their file to continue the conversation.\nempty|No messages yet. Leave your first message.\nvalidation|Enter your name and a message or photo.\nexport|Download records as CSV\nimport|Import a family CSV\nimport_button|Merge records\nimport_ok|Records merged. Existing records were not duplicated.\ninvalid|Unable to read the file. Please use a CSV downloaded from this app.\nlimit|CSV files must be under 15 MB and photos under 8 MB.\nphoto_bad|Unable to read the photo. Please use a JPG or PNG file.\nlanguage|Language\ndata|Keep my records\nvolatile|Records are kept only during this connection. Download a CSV before refreshing or leaving.\nbackup_notice|The CSV contains photos and messages and is not encrypted. Share it only with trusted family members.\nrecent|Family conversation\nphoto_help|Upload the screen where you need help and describe the problem. Your family can reply by sharing a CSV.\nphoto_no_ai|Photos are not automatically analyzed or answered.\nhistory|Learning history\nnot_started|No completed lessons yet.\nopen|Open lesson\nreset|Start this lesson again\nbrand|Learn simply. Stay connected.\nassets|Add original characters\nassets_note|The cat cropped from your supplied screen is included by default. Upload original images to replace it during this connection.\ncream|Original cream character\ncat|Original cat character\nfont|Text size\nnormal|Large\nlarge|Extra large\nauto_note|Some interface text uses online machine translation and may contain errors. Your messages and Korean lessons are not translated.\nno_search|Search lesson titles in Korean or try common English phone terms.\nrequired_photo|Choose a photo to share first.\nmenu|Menu\ntranslation_status|Interface translation status\nonline_status|Online machine translation\nbuilt_in_status|Built-in translation\nfallback_status|Translation could not be loaded. The interface is currently in English.\ntranslation_info|Korean and English use built-in dictionaries. The other 48 languages use a public web translation service without an API key. This code contains no paid API or billing setup. Availability depends on connectivity and provider policies. Your photos and messages are not sent for translation.\nsearch_content_status|Lessons are provided in Korean. If you cannot find a lesson, use photo help.\nlearn_hint|Learn at your own pace, one step at a time\nphoto_hint|Show your family where you need help\nchat_hint|Share a greeting, a photo or a helping hand\nrecord_hint|Pick up where you left off\nretry_translation|Try translation again\nstorage_full|Your records are getting large. Back up your CSV before starting a new connection.\nupdated|Settings applied.\nall|All\nfinish_note|Completed lessons are included in your CSV backup.".splitlines())
TEXT.update(features.NEW_KO)
ENGLISH.update(features.NEW_EN)
assert set(ENGLISH) == set(TEXT), 'English UI dictionary is incomplete'

LESSONS = {
'install':('앱 설치하기','앱은 휴대폰에 넣어 쓰는 작은 도구예요.',[
'안드로이드 휴대폰에서는 Play 스토어, 아이폰에서는 App Store를 찾아 눌러요.',
'검색창에 설치하려는 앱 이름을 적어요. 검색 결과에서 만든 회사와 앱 이름을 확인해요.',
'설치 또는 받기를 눌러요. 가격이 표시되면 유료이므로 결제 전 다시 확인해요.',
'설치가 끝나면 열기를 눌러요. 사진이나 위치 사용을 요청하면 필요한 권한인지 확인하고 선택해요.']),
'signup':('회원가입하기','회원가입은 처음 이용할 때 내 이용 정보를 만드는 일이에요.',[
'이용하려는 앱에서 회원가입 또는 시작하기를 눌러요.',
'이용약관을 읽고 필수와 선택 항목을 구분해요. 선택 동의는 꼭 하지 않아도 돼요.',
'요청한 정보를 입력해요. 비밀번호는 다른 곳과 다르게 만들고 가족 대화에 올리지 않아요.',
'문자로 받은 인증번호는 해당 앱 입력칸에만 적어요. 다른 사람에게 알려주지 않아요.',
'가입 완료 안내를 확인해요. 앱마다 화면과 순서가 조금씩 다를 수 있어요.']),
'login':('로그인하기','로그인은 내가 등록한 이용자임을 확인하고 들어가는 일이에요.',[
'앱을 열고 로그인을 찾아 눌러요.',
'가입할 때 사용한 아이디를 적어요. 아이디는 나를 구분하는 이름으로, 이메일이나 전화번호일 수 있어요.',
'비밀번호를 입력하고 로그인 버튼을 눌러요. 공용 기기에서는 자동 로그인을 선택하지 않아요.',
'비밀번호가 기억나지 않으면 비밀번호 찾기를 눌러요. 공식 앱 안에서 안내에 따라 다시 설정해요.']),
'photo':('화면 사진 보내기','화면 사진은 휴대폰에 보이는 모습을 사진으로 남긴 것이에요.',[
'휴대폰 화면을 찍기 전에 비밀번호와 인증번호 등 민감한 정보가 없는지 확인해요.',
'많은 안드로이드 휴대폰은 전원 버튼과 소리 줄이기 버튼을 짧게 함께 누르면 화면을 찍을 수 있어요. 기종마다 달라요.',
'홈 버튼이 없는 아이폰은 옆면 버튼과 소리 높이기 버튼을 짧게 함께 눌러요. 홈 버튼이 있는 기종은 방법이 달라요.',
'앱잘알의 사진으로 물어보기에서 사진 선택을 눌러 사진을 올려요. 화면 촬영이 어렵다면 다른 휴대폰 카메라로 찍어도 돼요.',
'어디에서 막혔는지 적고 저장해요. CSV를 내려받아 가족에게 전달해요.']),
'wifi':('와이파이 연결하기','와이파이는 가까운 무선 인터넷에 연결하는 기능이에요.',[
'휴대폰의 설정 앱을 열고 Wi-Fi 또는 와이파이를 눌러요.',
'와이파이를 켜고 집이나 믿을 수 있는 장소의 이름을 골라요.',
'비밀번호를 입력하고 연결을 눌러요. 모르는 공공 와이파이에서는 금융 거래를 피하는 것이 좋아요.',
'연결됨 표시를 확인해요. 와이파이가 끊기면 이동통신 데이터가 사용되어 요금이 생길 수 있어요.'])}

LESSONS.update({key:(item['title'],item['desc'],item['steps']) for key,item in EXTRA.items()})
LESSON_CATEGORY={key:(EXTRA[key]['category'] if key in EXTRA else ('스마트폰 기본' if key in ('wifi','photo') else '처음 시작하기')) for key in LESSONS}

# Static dictionaries only. Never contact an online translation service.
TEXT['safety']='스마트폰 안전 교육'
ENGLISH['safety']='Phone safety'
STATIC_UI = {'ko':dict(TEXT),'en':dict(ENGLISH)}
_STATIC_CORE = {
'ja':['ホーム','一つずつ学ぶ','写真で質問','家族と話す','学習を続ける','言語とデータ','わからないことがありますか？','アプジャルアルに聞いてみましょう','言語','メニュー','スマホで練習','学習クイズ','質問サポート','マイページ'],
'zh-CN':['首页','分步学习','拍照提问','与家人交流','继续学习','语言与数据','遇到不懂的问题了吗？','向앱잘알提问','语言','菜单','模拟手机练习','学习测验','提问助手','个人中心'],
'zh-TW':['首頁','逐步學習','拍照提問','與家人交流','繼續學習','語言與資料','遇到不懂的問題了嗎？','向앱잘알提問','語言','選單','模擬手機練習','學習測驗','提問助手','個人中心'],
'es':['Inicio','Aprender paso a paso','Preguntar con una foto','Hablar con la familia','Continuar aprendiendo','Idioma y datos','¿Hay algo que no sabes?','Pregunta a 앱잘알','Idioma','Menú','Practicar con el teléfono','Cuestionario','Ayuda con preguntas','Mi perfil'],
'fr':['Accueil','Apprendre pas à pas','Poser une question avec une photo','Parler en famille','Continuer à apprendre','Langue et données','Une question ?','Demandez à 앱잘알','Langue','Menu','Téléphone virtuel','Quiz','Aide aux questions','Mon profil'],
'de':['Startseite','Schritt für Schritt lernen','Mit einem Foto fragen','Mit der Familie sprechen','Weiterlernen','Sprache und Daten','Haben Sie eine Frage?','Fragen Sie 앱잘알','Sprache','Menü','Am virtuellen Handy üben','Quiz','Fragenhilfe','Mein Profil'],
'vi':['Trang chủ','Học từng bước','Hỏi bằng ảnh','Trò chuyện với gia đình','Tiếp tục học','Ngôn ngữ và dữ liệu','Bạn có điều chưa biết?','Hãy hỏi 앱잘알','Ngôn ngữ','Danh sách','Luyện tập điện thoại','Câu hỏi ôn tập','Trợ giúp câu hỏi','Trang cá nhân'],
'ar':['الرئيسية','التعلم خطوة بخطوة','السؤال بصورة','التحدث مع العائلة','متابعة التعلم','اللغة والبيانات','هل لديك سؤال؟','اسأل 앱잘알','اللغة','القائمة','التدرب على الهاتف','اختبار التعلم','مساعد الأسئلة','ملفي الشخصي']}
_CORE_KEYS=['home','learn','photo','chat','record','settings','title','subtitle','language','menu','practice','quiz','assistant','account']
for _code,_words in _STATIC_CORE.items():
    STATIC_UI[_code]=dict(ENGLISH)
    STATIC_UI[_code].update(dict(zip(_CORE_KEYS,_words)))

def translate_ui(code):
    return dict(STATIC_UI.get(code,ENGLISH)),code in ('ko','en')



LOGO_IMAGE = _APP_ASSETS['logo.png']

CHARACTER_IMAGE = _APP_ASSETS['character.png']

def fresh():
    return {'schema':'appjalal-v1', 'page':'welcome','lang':'ko','messages':[],
            'completed':{},'steps':{},'lesson':'install','big':False,'assets':{'guide':_APP_ASSETS['human_guide.png']},'favorites':[],'quiz_scores':{},'profile_name':''}
for key, value in fresh().items():
    if key not in st.session_state:
        st.session_state[key] = value
S = st.session_state


def encode_image(raw):
    if len(raw)>8*1024*1024:
        raise ValueError('limit')
    with Image.open(io.BytesIO(raw)) as image:
        if image.width * image.height > 24000000:
            raise ValueError('limit')
        image = ImageOps.exif_transpose(image)
        image.thumbnail((1400,1400))
        if image.mode not in ('RGB','RGBA'):
            image = image.convert('RGBA')
        out=io.BytesIO()
        image.save(out,format='PNG',optimize=True)
    return base64.b64encode(out.getvalue()).decode('ascii')


def export_csv(messages=None, completed=None, steps=None):
    out=io.StringIO(newline='')
    writer=csv.DictWriter(out,fieldnames=['schema','kind','id','payload'])
    writer.writeheader()
    def row(kind, ident, payload):
        # JSON starts with {, so text cannot become spreadsheet formulas.
        writer.writerow(dict(schema='appjalal-v1',kind=kind,id=ident,payload=json.dumps(payload,ensure_ascii=False)))
    for message in (S.messages if messages is None else messages):
        row('message',message['id'],message)
    for lesson, date in (S.completed if completed is None else completed).items():
        row('complete',lesson,{'date':date})
    for lesson, step in (S.steps if steps is None else steps).items():
        row('step',lesson,{'step':step})
    row('preferences','local',{'lang':S.lang,'lesson':S.lesson,'big':S.big,'favorites':S.favorites,'quiz_scores':S.quiz_scores})
    return out.getvalue().encode('utf-8-sig')


def parse_csv(raw):
    if len(raw)>15*1024*1024:
        raise ValueError('limit')
    # Python default field cap is too small for embedded photographs.
    csv.field_size_limit(16*1024*1024)
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    if reader.fieldnames != ['schema','kind','id','payload']:
        raise ValueError('invalid')
    messages=[]; completed={}; steps={}
    for count,row in enumerate(reader):
        if count>=3000 or row['schema']!='appjalal-v1':
            raise ValueError('invalid')
        data=json.loads(row['payload']); kind=row['kind']; ident=row['id']
        if not isinstance(data,dict): raise ValueError('invalid')
        if kind=='message':
            if not all(isinstance(data.get(k),str) for k in ['id','name','text','time','image']): raise ValueError('invalid')
            if data['id']!=ident or len(ident)>100 or len(data['name'])>60 or len(data['text'])>2000: raise ValueError('invalid')
            stamp=datetime.fromisoformat(data['time'])
            if stamp.tzinfo is None: stamp=stamp.replace(tzinfo=timezone.utc)
            data['time']=stamp.astimezone(timezone.utc).isoformat()
            if data['image']:
                data['image']=encode_image(base64.b64decode(data['image'],validate=True))
            messages.append({k:data[k] for k in ['id','name','text','time','image']})
        elif kind=='complete' and ident in LESSONS:
            datetime.fromisoformat(data['date']); completed[ident]=data['date']
        elif kind=='step' and ident in LESSONS:
            if type(data.get('step')) is not int or not 0<=data['step']<len(LESSONS[ident][2]): raise ValueError('invalid')
            steps[ident]=data['step']
        elif kind!='preferences':
            raise ValueError('invalid')
    return messages,completed,steps


def go(page):
    S.page=page
    st.rerun()

# The opening gate is checked before menus, translation calls, or functional pages.
if not S.get('app_opened', False):
    st.markdown("""<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    .stApp {background:#F5F8F4;color:#26372D;font-family:Pretendard,sans-serif;}
    .block-container {max-width:560px;padding:3rem 1.5rem;}
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {display:none;}
    .opening-title {text-align:center;color:#26372D;font-size:44px;font-weight:800;margin:8px 0;}
    .opening-copy {text-align:center;color:#647168;font-size:21px;line-height:1.7;margin:8px 0 24px;}
    .stButton>button {width:100%;min-height:66px;border-radius:15px;background:#527B63;color:#FFFFFF;border:1px solid #527B63;}
    .stButton>button p {font-family:Pretendard,sans-serif;font-size:24px;font-weight:700;color:#FFFFFF;}
    .ready-dots {display:flex;justify-content:center;gap:7px;margin:22px 0;} .ready-dots i {width:7px;height:7px;background:#6F987A;border-radius:50%;animation:breathe 1.4s infinite alternate;} .ready-dots i:nth-child(2){animation-delay:.2s;} .ready-dots i:nth-child(3){animation-delay:.4s;} @keyframes breathe {from{opacity:.3;transform:translateY(0)}to{opacity:1;transform:translateY(-4px)}} @media(prefers-reduced-motion:reduce){.ready-dots i{animation:none;}}
    .stButton>button:hover {background:#3E624D;border-color:#3E624D;color:white;}
    .stButton>button:focus-visible {outline:3px solid #26372D;outline-offset:4px;}
    </style>""",unsafe_allow_html=True)
    left,center,right=st.columns([.15,1,.15])
    with center:
        st.image(base64.b64decode(LOGO_IMAGE),use_container_width=True)
    st.markdown('<p class="opening-copy">모르는 게 생겼나요?<br>앱잘알과 천천히 배워 보세요.</p>',unsafe_allow_html=True)
    st.markdown('<div class="ready-dots" aria-label="준비되었어요"><i></i><i></i><i></i></div>',unsafe_allow_html=True)
    st.caption('준비되었어요. 열기를 누르면 로그인 또는 체험을 선택할 수 있어요.')
    if st.button('열기',key='open_app',use_container_width=True):
        S.app_opened=True
        S.page='account'
        st.rerun()
    st.stop()

# Read the widget return directly; no callback or explicit rerun is needed.
_language_codes=[code for code,_ in LANGUAGES]
_language_names=dict(LANGUAGES)
if S.get('_appjalal_language_v2') not in _language_codes:
    S['_appjalal_language_v2']=S.lang if S.lang in _language_codes else 'ko'
S.lang=st.selectbox('🌐 언어 / Language', _language_codes,
    format_func=lambda code:_language_names[code]+(' · 영어로 표시 / English fallback' if code not in STATIC_UI else ''),
    key='_appjalal_language_v2')
UI,translated=translate_ui(S.lang)
def t(key):
    return UI.get(key,ENGLISH.get(key,TEXT.get(key,str(key))))

if S.lang not in ('ko','en'):
    if S.lang in STATIC_UI:
        st.info('주요 메뉴만 선택한 언어로 준비되어 있어요. 나머지 안내는 영어, 학습 본문은 한국어입니다. · Main menus are translated; other interface text is English and lessons are Korean.')
    else:
        st.info('이 언어의 번역 사전은 아직 준비되지 않아 영어로 표시합니다. · This language dictionary is not yet available. Showing English.')
with st.container(key='topbar'):
    brand,menu=st.columns([3,1])
    with brand:
        st.image(base64.b64decode(LOGO_IMAGE),width=160)
    with menu:
        with st.popover('☰ '+t('menu'),use_container_width=True):
            for page in ['home','learn','assistant','practice','safety','record','account','settings']:
                if st.button(t(page),key='topnav_'+page,use_container_width=True):go(page)
rtl=S.lang in ('ar','iw','ur','fa') and S.lang in STATIC_UI
FONT_MAP={'ja':'Noto Sans JP','zh-CN':'Noto Sans SC','zh-TW':'Noto Sans TC','ar':'Noto Sans Arabic','fa':'Noto Sans Arabic','ur':'Noto Nastaliq Urdu','iw':'Noto Sans Hebrew','hi':'Noto Sans Devanagari','ne':'Noto Sans Devanagari','mr':'Noto Sans Devanagari','th':'Noto Sans Thai','my':'Noto Sans Myanmar','km':'Noto Sans Khmer','lo':'Noto Sans Lao','bn':'Noto Sans Bengali','ta':'Noto Sans Tamil','te':'Noto Sans Telugu','pa':'Noto Sans Gurmukhi','si':'Noto Sans Sinhala'}
fallback_font=FONT_MAP.get(S.lang,'Noto Sans')
font_url='https://fonts.googleapis.com/css2?family='+fallback_font.replace(' ','+')+'&display=swap'
size=23 if S.big else 20
st.markdown(f'''<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
@import url('{font_url}');
:root {{--app-background:#F7F9F6;--app-surface:#FFFFFF;--app-ink:#26372D;--app-muted:#647168;--app-blue:#EAF2EB;--app-lavender:#F0F4EF;--app-sage:#E8F1E9;--app-coral:#F5F3E8;color-scheme:light;}}
.stApp {{background:#F7F9F6;color:#26372D;}}
html,body,[class*="css"],.stApp,button,input,textarea,select {{font-family:'Pretendard','{fallback_font}','Noto Sans','Arial',sans-serif!important;}}
.block-container {{max-width:1020px;padding:1.8rem 1.3rem 4rem;}}
h1,h2,h3,p,label {{color:#26372D!important;}}
h1 {{font-size:clamp(32px,5.7vw,52px)!important;font-weight:800!important;letter-spacing:-.045em;line-height:1.25!important;}}
h2 {{font-size:30px!important;font-weight:800!important;}}
p,.stMarkdown li,label,[data-testid="stWidgetLabel"] p {{font-size:{size}px!important;line-height:1.65!important;}}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button {{min-height:64px;border-radius:15px;border:1px solid #CDD3DF;background:#FFFFFF;color:#26372D!important;box-shadow:0 2px 5px #26372D06;padding:14px 20px;transition:transform .15s,box-shadow .15s;}}
.stButton>button p,.stDownloadButton>button p,.stFormSubmitButton>button p {{font-size:{size}px!important;font-weight:600!important;line-height:1.4!important;text-align:center;}}
.stButton>button:hover,.stDownloadButton>button:hover,.stFormSubmitButton>button:hover {{border-color:#73947A;box-shadow:0 5px 14px #26372D14;transform:translateY(-2px);}}
.stButton>button:active {{transform:translateY(1px);}}
.st-key-topbar {{border-bottom:1px solid #E6E2D8;padding-bottom:18px;margin-bottom:12px;}}
.st-key-subnav button {{min-height:48px;box-shadow:none;background:transparent;padding:8px 16px;}}
.st-key-subnav button p {{font-size:17px!important;}}
.st-key-featuregrid {{margin-top:14px;margin-bottom:16px;}}
.st-key-featuregrid [data-testid="stCaptionContainer"] p {{font-size:18px!important;line-height:1.5!important;margin:6px 2px 12px;color:#46556B!important;}}
[data-testid="stFileUploader"] section {{background:#FFFFFF;border-color:#CDD3DF;border-radius:16px;}}
[data-testid="stProgress"] [role="progressbar"] {{accent-color:#5679A6;}}
@media(prefers-reduced-motion:reduce) {{button {{transition:none!important;transform:none!important;}}}}
button:focus-visible,input:focus-visible,textarea:focus-visible {{outline:3px solid #527B63!important;outline-offset:3px;}}
button:disabled {{background:#ECEBE7!important;color:#72757B!important;opacity:.65;box-shadow:none!important;transform:none!important;}}
button[kind="primary"],.stFormSubmitButton>button {{background:#527B63!important;border-color:#527B63!important;color:#FFFFFF!important;}}
button[kind="primary"] p,.stFormSubmitButton>button p {{color:#FFFFFF!important;}}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea {{font-size:{size}px!important;background:#FFFFFF!important;color:#26372D!important;border-radius:12px;min-height:54px;}}
[data-testid="stSelectbox"] * {{color:#26372D;}}
[data-baseweb="select"] > div {{background:#FFFFFF!important;}}
[data-baseweb="input"], [data-baseweb="textarea"] {{background:#FFFFFF!important;}}
[role="listbox"] {{background:#FFFFFF!important;color:#26372D!important;}}
.st-key-feature_learn button {{background:#EAF2EB!important;}}
.st-key-feature_photo button {{background:#F0F4EF!important;}}
.st-key-feature_chat button {{background:#E8F1E9!important;}}
.st-key-feature_record button {{background:#F5F3E8!important;}}
[class*="st-key-feature_"] button {{min-height:112px;width:100%;border:1px solid #26372D14;}}
[class*="st-key-feature_"] button p {{font-size:{size+2}px!important;font-weight:600!important;}}
.hero {{padding:30px 0 22px;}}
.eyebrow {{font-size:14px!important;font-weight:750;letter-spacing:.12em;color:#657A87!important;}}
.hero-sub {{font-size:clamp(27px,4vw,39px)!important;font-weight:750;line-height:1.35!important;margin:8px 0 18px;letter-spacing:-.04em;}}
.soft-panel {{background:#F2F0E8;border:1px solid #E4E1D7;border-radius:18px;padding:22px;margin:18px 0;}}
[data-testid="stVerticalBlockBorderWrapper"] {{border-radius:18px!important;}}
[data-testid="stHeader"] {{background:#F7F9F6E8;}}
[data-testid="stSidebar"] {{background:#F8F5EF;border-inline-end:1px solid #E4DED3;}}
[data-testid="stSidebarUserContent"] {{padding:1.4rem 1rem 2rem;overflow-wrap:anywhere;}}
[data-testid="stSidebar"] button {{white-space:normal;height:auto;min-height:56px;}}
[data-testid="stSidebar"] button p {{text-align:start!important;font-size:18px!important;}}
.st-key-topbar [data-testid="stPopover"] button {{min-height:52px;margin-top:28px;box-shadow:none;background:transparent;}}
.st-key-topbar h3 {{white-space:nowrap;}}
.st-key-learningbody {{direction:ltr;text-align:left;}}
[data-testid="stCaptionContainer"] p {{color:#647168!important;}}
.st-key-featuregrid [data-testid="stCaptionContainer"] {{min-height:3.2rem;}}
@media(min-width:768px) {{.st-key-hero_layout {{padding-top:20px;padding-bottom:10px;}}}}
@media(max-width:600px) {{.st-key-topbar [data-testid="stHorizontalBlock"] {{flex-wrap:wrap!important;}} .st-key-topbar [data-testid="stColumn"] {{min-width:130px!important;}} .st-key-topbar [data-testid="stPopover"] button {{margin-top:0;}}}}
[data-testid="stAppViewContainer"] > .main {{direction:{'rtl' if rtl else 'ltr'};}}
[data-testid="stMainBlockContainer"] {{direction:{'rtl' if rtl else 'ltr'};text-align:{'right' if rtl else 'left'};}}
@media(max-width:600px) {{.block-container {{padding:1rem .85rem 3rem;}} [class*="st-key-feature_"] button {{min-height:112px;padding:10px 6px;}} [class*="st-key-feature_"] button p {{font-size:19px!important;}} .st-key-featuregrid [data-testid="stHorizontalBlock"] {{flex-wrap:nowrap!important;gap:10px;}} .st-key-featuregrid [data-testid="stColumn"] {{min-width:0!important;width:calc(50% - 5px)!important;flex:1 1 0!important;}}}}
</style>''',unsafe_allow_html=True)



with st.sidebar:
    st.image(base64.b64decode(LOGO_IMAGE),width=160)
    st.caption(t('brand'))
    for page in ['home','learn','assistant','practice','safety','record','account','settings']:
        if st.button(t(page),key='sidebar_'+page,use_container_width=True,
                     type='primary' if S.page==page else 'secondary'):
            go(page)
    st.divider()
    st.caption(t('translation_status')+' · '+(t('built_in_status') if S.lang in ('ko','en') else ('Static dictionary' if S.lang in STATIC_UI else 'English')))
    st.caption(t('csv_note'))

def nav():
    with st.container(key='subnav'):
        a,b=st.columns(2)
        if a.button('⌂ '+t('home'),key='subnav_home',use_container_width=True):go('home')
        if b.button('⚙ '+t('settings'),key='subnav_settings',use_container_width=True):go('settings')

def show_assets():
    if S.assets:
        cols=st.columns(len(S.assets))
        for col,data in zip(cols,S.assets.values()):
            col.image(base64.b64decode(data),width=150)

def progress():
    st.markdown('### '+t('progress'))
    count=len(S.completed)
    st.progress(count/len(LESSONS))
    st.write(f"{t('complete')} {count} / {len(LESSONS)}")

def thread():
    if not S.messages: st.info(t('empty'))
    for item in sorted(S.messages,key=lambda m:m['time']):
        with st.container(border=True):
            st.text(item['name'])
            st.caption(item['time'][:16].replace('T',' ')+' UTC')
            if item['text']: st.text(item['text'])
            if item['image']: st.image(base64.b64decode(item['image']),use_container_width=True)

def composer(photo=False):
    st.warning(t('privacy'))
    method=st.radio(t('upload'),[t('upload'),t('camera')],horizontal=True,key='method_'+str(photo))
    if method==t('camera'):
        picture=st.camera_input(t('camera'),key='camera_'+str(photo))
    else:
        picture=st.file_uploader(t('upload'),type=['png','jpg','jpeg'],key='pic_'+str(photo))
    with st.form('compose_'+str(photo),clear_on_submit=True):
        name=st.text_input(t('name'),max_chars=60)
        message=st.text_area(t('message'),max_chars=2000)
        submitted=st.form_submit_button(t('send'),use_container_width=True)
    if submitted:
        if not name.strip() or (not message.strip() and picture is None):st.error(t('validation'))
        elif photo and picture is None:st.error(t('required_photo'))
        else:
            try:
                image=encode_image(picture.getvalue()) if picture else ''
                entry={'id':str(uuid.uuid4()),'name':name.strip(),'text':message.strip(),
                    'time':datetime.now(timezone.utc).isoformat(),'image':image}
                candidate=S.messages+[entry]
                if len(candidate)>2900 or len(export_csv(messages=candidate))>15*1024*1024:
                    st.error(t('storage_full'))
                else:
                    S.messages=candidate
                    st.success(t('saved'))
            except Exception as exc:
                st.error(t('limit') if str(exc)=='limit' else t('photo_bad'))

def backup():
    st.warning(t('volatile'))
    st.caption(t('backup_notice'))
    st.download_button(t('export'),export_csv(),'appjalal_backup.csv','text/csv',use_container_width=True)
    uploaded=st.file_uploader(t('import'),type=['csv'])
    if st.button(t('import_button'),disabled=uploaded is None,use_container_width=True):
        try:
            messages,completed,steps=parse_csv(uploaded.getvalue())
            extended={}
            for row in csv.DictReader(io.StringIO(uploaded.getvalue().decode('utf-8-sig'))):
                if row['kind']=='preferences':
                    value=json.loads(row['payload'])
                    favorites=value.get('favorites',[])
                    scores=value.get('quiz_scores',{})
                    if not isinstance(favorites,list) or any(k not in LESSONS for k in favorites):raise ValueError('invalid')
                    if not isinstance(scores,dict):raise ValueError('invalid')
                    for key,score in scores.items():
                        if key not in EXTRA or not isinstance(score,dict) or type(score.get('attempts')) is not int or not 0<=score['attempts']<=1000000 or type(score.get('correct')) is not bool:raise ValueError('invalid')
                    extended={'favorites':favorites,'quiz_scores':scores}
            # Commit only after the entire file passes validation; local preferences never overwritten.
            merged={m['id']:m for m in messages}
            merged.update({m['id']:m for m in S.messages})
            new_messages=list(merged.values())
            new_completed=dict(S.completed)
            new_steps=dict(S.steps)
            for lesson,date in completed.items():
                new_completed[lesson]=max(date,new_completed.get(lesson,date))
            for lesson,step in steps.items():new_steps[lesson]=max(step,new_steps.get(lesson,0))
            if len(new_messages)>2900 or len(export_csv(new_messages,new_completed,new_steps))>15*1024*1024:
                raise ValueError('limit')
            S.messages=new_messages
            S.completed=new_completed
            S.steps=new_steps
            S.favorites=list(dict.fromkeys(S.favorites+extended.get('favorites',[])))
            S.quiz_scores.update(extended.get('quiz_scores',{}))
            st.success(t('import_ok'))
        except Exception as exc:
            st.error(t('limit') if str(exc)=='limit' else t('invalid'))

S.completed={k:v for k,v in S.completed.items() if k in LESSONS and isinstance(v,str)}
S.steps={k:min(max(v,0),len(LESSONS[k][2])-1) for k,v in S.steps.items() if k in LESSONS and type(v) is int}
if S.lesson not in LESSONS:S.lesson='install'
if S.pop('_load_warning',False):
    st.warning(t('sync_failed'))
st.markdown(design.css(S.big),unsafe_allow_html=True)
# Attempt saving completed interactions before the next functional render.
try:
    services.save_progress()
except Exception as exc:
    st.warning(t('sync_failed'))
    print('APPJALAL_SAVE_PROGRESS_ERROR:', type(exc).__name__, str(exc)[:500])

if S.page=='welcome':
    st.markdown('<div class="hero"><p class="eyebrow">APPJALAL</p><h1>앱잘알</h1></div>',unsafe_allow_html=True)
    st.write(t('welcome')); st.caption(t('brand')); show_assets()
    if st.button(t('start'),type='primary',use_container_width=True):go('home')
    st.info(t('csv_note'))
    if st.button(t('settings'),use_container_width=True):go('settings')
elif S.page=='home':
    with st.container(key='hero_layout'):
        if S.assets:
            greeting,characters=st.columns([1.8,1],gap='large')
        else:
            greeting=st.container()
            characters=None
        with greeting:
            st.markdown(f'<div class="hero"><p class="eyebrow">APP잘알</p><h1>{html.escape(t("title"))}</h1><p class="hero-sub">{html.escape(t("subtitle"))}</p></div>',unsafe_allow_html=True)
            st.write(t('intro'))
        if characters is not None:
            with characters: show_assets()
    if S.profile_name:st.write(S.profile_name+' 님, 반가워요.')
    query=st.text_input(t('search'),placeholder=t('search_hint'))
    st.caption(t('no_search') if S.lang in ('ko','en') else t('search_content_status'))
    if query.strip():
        aliases={'install':'install download app store 앱 설치 다운로드','signup':'sign up signup register account 회원가입 가입','login':'log in login password 로그인 비밀번호','photo':'photo screenshot picture 화면 사진 캡처','wifi':'wifi wi-fi internet 와이파이 인터넷'}
        terms=query.casefold().split()
        matches=[key for key,(title,desc,steps) in LESSONS.items() if all(term in (' '.join([title,desc,aliases.get(key,'')]+steps)).casefold() for term in terms)]
        st.caption(t('content_note'))
        if not matches:st.info(t('none'))
        for key in matches:
            if st.button(LESSONS[key][0],key='search_'+key,use_container_width=True):S.lesson=key;go('learn')
    with st.container(key='featuregrid'):
        for row in [[('learn','▤'),('photo','▧')],[('chat','♡'),('record','✓')]]:
            cols=st.columns(2,gap='medium')
            for col,(page,icon) in zip(cols,row):
                with col:
                    with st.container(key='feature_'+page):
                        if st.button(icon+'  '+t(page),key='home_'+page,use_container_width=True):go(page)
                    st.caption(t(page+'_hint'))
    st.divider()
    progress()
    st.caption(LESSONS[S.lesson][0]+' · '+t('step')+' '+str(S.steps.get(S.lesson,0)+1))
    if st.button(t('continue'),key='home_continue',type='primary',use_container_width=True):go('learn')
elif S.page=='safety':
    nav();st.title(t('safety'));st.write('급한 송금이나 인증번호 요구에는 응하지 말고 공식 창구에서 확인해요.');features.quiz()
elif S.page=='learn':
    nav();st.title(t('learn'));st.info(t('content_note'))
    category=st.selectbox(t('category'),[t('all')]+CATEGORIES+[t('favorites')])
    available=[key for key in LESSONS if category==t('all') or LESSON_CATEGORY[key]==category or (category==t('favorites') and key in S.favorites)]
    if not available:
        st.info('아직 즐겨찾기가 없어요. 학습 화면에서 별 버튼을 눌러 보세요.');st.stop()
    lesson=st.selectbox(t('choose'),available,index=available.index(S.lesson) if S.lesson in available else 0,format_func=lambda k:LESSONS[k][0])
    S.lesson=lesson
    title,desc,steps=LESSONS[lesson]
    step=S.steps.get(lesson,0)
    st.subheader(title);st.write(desc)
    st.caption('난이도: 처음 배우는 분 · '+str(len(steps))+'단계')
    if st.button(('★ ' if lesson in S.favorites else '☆ ')+t('favorite')):
        if lesson in S.favorites:S.favorites.remove(lesson)
        else:S.favorites.append(lesson)
        st.rerun()
    st.progress((step+1)/len(steps));st.caption(f"{t('step')} {step+1} / {len(steps)}")
    easy=st.toggle('쉬운 설명 모드',value=S.get('easy_mode',False),key='easy_mode_toggle')
    S.easy_mode=easy
    with st.container(border=True,key='learningbody'):
        text=steps[step]
        if easy:
            for sentence in text.replace('다.','다.\n').replace('요.','요.\n').splitlines():
                if sentence.strip():st.write(sentence.strip())
        else:st.write(text)
    with st.expander('단계 그림과 설명 다시 보기',expanded=False):
        st.image(design.step_picture(title,step,len(steps)),use_container_width=True)
        st.caption('단계 위치를 보여주는 개념 그림입니다. 실제 휴대폰 화면이 아닙니다.')
        st.write(steps[step])
    features.voice(steps[step])
    a,b=st.columns(2)
    if a.button('← '+t('prev'),disabled=step==0,use_container_width=True):S.steps[lesson]=step-1;st.rerun()
    if step<len(steps)-1:
        if b.button(t('next')+' →',type='primary',use_container_width=True):S.steps[lesson]=step+1;st.rerun()
    elif b.button(t('done'),type='primary',use_container_width=True):
        S.completed[lesson]=datetime.now(timezone.utc).isoformat();S.just_completed=True;go('record')
    if st.button(t('reset'),use_container_width=True):S.steps[lesson]=0;st.rerun()
elif S.page=='photo':
    nav();st.title(t('photo'));st.write(t('photo_help'));st.info(t('photo_no_ai'))
    composer(True);st.info(t('csv_note'));backup()
elif S.page=='chat':
    nav();st.title(t('chat'));st.info(t('csv_note'))
    composer();st.subheader(t('recent'));thread();backup()
elif S.page=='record':
    nav();st.title(t('history'))
    if S.get('just_completed',False):
        st.success(t('done'))
        show_assets()
        S.just_completed=False
    progress();st.caption(t('content_note'))
    for category in CATEGORIES:
        keys=[key for key in LESSONS if LESSON_CATEGORY[key]==category]
        st.write(category+': '+str(sum(k in S.completed for k in keys))+' / '+str(len(keys)))
    if st.button(t('quiz'),key='record_quiz'):go('quiz')
    if not S.completed:st.info(t('not_started'))
    for key,(title,_,steps) in LESSONS.items():
        with st.container(border=True):
            st.write(('✓ ' if key in S.completed else '○ ')+title)
            st.caption(S.completed[key][:10] if key in S.completed else f"{t('step')} {S.steps.get(key,0)+1} / {len(steps)}")
            if st.button(t('open'),key='history_'+key,use_container_width=True):S.lesson=key;go('learn')
    st.caption(t('finish_note'));backup()
elif S.page in ('practice','quiz','assistant','account'):
    nav()
    st.caption(t('quiz_ko'))
    if S.page=='practice':features.practice()
    elif S.page=='quiz':features.quiz()
    elif S.page=='assistant':features.assistant(LESSONS)
    else:features.account()
elif S.page=='settings':
    nav();st.title(t('settings'));
    for _dest in ['photo','chat','quiz','practice','assistant','account']:
        if st.button(t(_dest),key='settings_link_'+_dest,use_container_width=True):go(_dest)
    st.info('외부 번역을 사용하지 않습니다. 최상단 언어 선택은 내장 사전을 즉시 적용합니다. · Offline UI dictionaries only.')
    st.write(t('translation_status')+' · '+(t('built_in_status') if S.lang in ('ko','en') else ('Static dictionary' if S.lang in STATIC_UI else 'English')))
    st.caption('한국어·영어는 전체 공통 UI, 일본어·중국어 간체/번체·스페인어·프랑스어·독일어·베트남어·아랍어는 주요 메뉴가 준비되어 있습니다. 그 밖의 문구와 언어는 영어로 표시하며 학습 콘텐츠는 한국어입니다.')
    st.write(t('language')+' · '+dict(LANGUAGES)[S.lang])
    big=st.toggle(t('font')+' · '+t('large'),value=S.big)
    if big!=S.big:S.big=big;st.rerun()
    st.subheader('음성 안내와 쉬운 설명')
    st.toggle('학습 음성 안내 켜기',key='voice_enabled')
    st.toggle('쉬운 설명 기본 사용',key='easy_mode')
    st.caption('음성 안내를 켜면 상세 학습 화면에 읽어주기 버튼이 나타나요. 쉬운 설명은 문장을 짧게 나누어 보여줘요.')
    st.subheader(t('assets'));st.caption(t('assets_note'))
    for key in ['cream','cat']:
        asset=st.file_uploader(t(key),type=['png','jpg','jpeg'],key='asset_'+key)
        if asset is not None:
            try:S.assets[key]=encode_image(asset.getvalue())
            except Exception:st.error(t('photo_bad'))
    show_assets();st.subheader(t('data'));backup()
# Save results created during the current interaction as well.
try:
    services.save_progress()
except Exception as exc:
    st.warning(t('sync_failed'))
    print('APPJALAL_SAVE_PROGRESS_ERROR:', type(exc).__name__, str(exc)[:500])
with st.container(key='bottom_nav'):
    columns=st.columns(5)
    for col,page,label in zip(columns,['home','learn','practice','assistant','account'],['bottom_home','bottom_learn','bottom_practice','assistant','account']):
        if col.button(t(label),key='bottom_'+page,use_container_width=True):go(page)
st.divider();st.caption('앱잘알 · '+t('brand'))

if S.get('page') == 'settings':
    with st.expander('배포 안내와 데이터베이스 설정'):
        st.markdown(_SETUP_DOC)
        st.download_button('Supabase SQL 내려받기',_SETUP_SQL,'schema.sql','text/plain',key='setup_sql')
