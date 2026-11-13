"""폰잘알 만들어줄게 | streamlit run app.py
GitHub에 app.py와 requirements.txt를 올리고 Streamlit Community Cloud에서 배포하세요.
CSV 교환형: 실시간 전송, 실제 로그인, 서버 영구 저장은 제공하지 않습니다.
"""
import base64
import csv
import io
import uuid
import warnings
import html
from datetime import datetime
import streamlit as st
from PIL import Image, ImageOps
st.set_page_config(page_title="폰잘알 만들어줄게", page_icon="📱", layout="centered", initial_sidebar_state="collapsed")
csv.field_size_limit(8 * 1024 * 1024)


MAX_IMAGE = 3 * 1024 * 1024

MAX_CSV = 20 * 1024 * 1024

MAX_RECORDS = 300

FIELDS = ["id", "kind", "author", "role", "text", "created_at", "image_b64", "topic"]

LESSONS = {
    "앱 설치하기": [
        ("앱을 받는 가게 열기", "갤럭시는 ‘Play 스토어’, 아이폰은 ‘App Store’를 찾아 눌러 주세요. 휴대폰 종류에 따라 화면이 조금 달라요."),
        ("찾고 싶은 앱 이름 쓰기", "돋보기 모양을 누르고 앱 이름을 써 주세요. 이름과 만든 회사가 맞는지 확인해요. 광고나 비슷한 이름의 앱에 주의하세요."),
        ("설치 또는 받기 누르기", "‘설치’나 ‘받기’를 눌러요. 금액이 보이면 유료일 수 있으니 먼저 확인해요. 지문이나 얼굴 확인을 요청할 수 있어요."),
        ("열어서 확인하기", "설치가 끝나면 ‘열기’를 눌러요. 연락처·위치 등 사용 허락을 묻는다면 꼭 필요한지 확인하고 결정하세요.")],
    "회원가입하기": [
        ("회원가입 버튼 찾기", "회원가입은 서비스를 처음 쓰기 위해 내 이름표를 만드는 일이에요. ‘회원가입’ 또는 ‘처음이세요?’를 찾아요."),
        ("필수 내용만 천천히 쓰기", "이름, 이메일 등 꼭 필요한 내용을 써요. ‘선택’이라고 된 광고 수신 동의는 원하지 않으면 체크하지 않아도 돼요."),
        ("나만 아는 비밀번호 정하기", "다른 곳과 겹치지 않는 비밀번호를 정해요. 비밀번호는 가족 대화방이나 도움 사진에도 올리지 마세요."),
        ("본인 확인 후 마무리하기", "문자로 받은 인증번호는 가입 중인 공식 화면에만 입력해요. 다른 사람에게 알려 주지 말고, 가입 완료 안내를 확인해요.")],
    "로그인하기": [
        ("로그인 버튼 누르기", "로그인은 이미 만든 내 이름표로 들어가는 일이에요. ‘로그인’을 눌러요. 처음 이용한다면 먼저 회원가입을 해요."),
        ("아이디와 비밀번호 쓰기", "가입할 때 쓴 이메일이나 아이디, 비밀번호를 입력해요. 한글·영문 상태와 큰 글자 입력 상태를 확인해요."),
        ("들어가기 누르기", "‘로그인’ 또는 ‘들어가기’를 눌러요. 다른 사람의 휴대폰이라면 로그인 상태 유지에 체크하지 마세요."),
        ("기억나지 않을 때", "여러 번 추측하기보다 공식 앱의 ‘비밀번호 찾기’를 이용하세요. 문자 속 낯선 주소로 들어가지는 마세요.")],
    "화면 사진 남기기": [
        ("도움받을 화면 열기", "어디서 막혔는지 보이는 화면을 열어요. 비밀번호·인증번호·계좌번호·신분증이 보이지 않는지 먼저 확인해요."),
        ("화면을 사진으로 저장하기", "대부분의 갤럭시는 전원 버튼과 소리 줄이기 버튼을 짧게 동시에 눌러요. Face ID 아이폰은 옆면 버튼과 소리 키우기 버튼, 홈 버튼이 있는 아이폰은 홈 버튼과 옆면 또는 상단 버튼을 함께 눌러요. 기종에 따라 달라요."),
        ("사진을 확인하기", "사진 앱이나 갤러리에서 저장된 사진을 확인해요. 민감한 부분은 잘라내거나 가린 후 공유해요. 보안 때문에 화면 사진이 안 되는 앱도 있어요."),
        ("도움 요청에 올리기", "이 앱의 ‘사진으로 도움’에서 사진을 골라 주세요. 다른 휴대폰으로 화면을 촬영해 올려도 돼요. 카메라는 접속 환경에 따라 지원되지 않을 수 있어요.")],
}

WORDS = {
    "앱": "휴대폰에 넣어 쓰는 작은 도구예요. 예: 지도, 날씨, 메시지.",
    "설치": "새 도구를 휴대폰에 넣는 일이에요.",
    "아이디": "서비스에서 나를 구별하는 이름표예요. 이메일 주소를 쓰기도 해요.",
    "로그인": "내 이름표와 비밀번호로 서비스에 들어가는 일이에요.",
    "로그아웃": "내 사용을 마치고 안전하게 나오는 일이에요.",
    "회원가입": "서비스를 처음 쓰기 위해 내 이름표를 만드는 일이에요.",
    "인증번호": "본인인지 확인하는 일회용 숫자예요. 남에게 알려 주면 안 돼요.",
    "업로드": "내 휴대폰의 사진이나 파일을 서비스에 올리는 일이에요.",
    "다운로드": "서비스에 있는 사진이나 파일을 내 휴대폰에 받는 일이에요.",
    "와이파이": "가까운 무선 인터넷에 연결하는 방법이에요. 공공 장소에서는 중요한 금융 업무에 주의해요.",
    "데이터": "여기서는 통신사 인터넷 사용량을 뜻해요. 요금제에 따라 비용이 들 수 있어요.",
    "알림": "새 소식이 왔다고 휴대폰이 알려 주는 표시예요.",
    "권한": "앱이 카메라나 위치 등을 써도 되는지 묻는 허락이에요.",
    "업데이트": "앱을 새 버전으로 바꾸는 일이에요. 기능이나 안전성이 좋아질 수 있어요.",
    "스크린샷": "지금 보이는 휴대폰 화면을 그대로 사진으로 남기는 일이에요.",
    "CSV": "이 앱에서는 가족 대화와 사진을 묶어 주고받는 보관 파일이에요. 암호화되지 않으므로 가족끼리만 안전하게 보관해요.",
}

def go(page):
    st.session_state.page = page
    st.rerun()

def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")

def image_data(upload):
    if upload is None:
        return ""
    raw = upload.getvalue()
    if len(raw) > MAX_IMAGE:
        raise ValueError("사진은 3MB 이하로 골라 주세요.")
    return normalize_image(raw)

def normalize_image(raw):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as im:
                if im.format not in ("JPEG", "PNG", "WEBP"):
                    raise ValueError("JPG, PNG, WEBP 사진만 사용할 수 있어요.")
                if im.width * im.height > 24000000:
                    raise ValueError("사진 크기가 너무 커요. 작은 사진으로 바꿔 주세요.")
                im = ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((1600, 1600))
                out = io.BytesIO()
                im.save(out, format="JPEG", quality=82)
                return base64.b64encode(out.getvalue()).decode("ascii")
    except (Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
        raise ValueError("사진 크기가 너무 커요.") from exc
    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError("사진을 읽지 못했어요. 다른 사진을 골라 주세요.") from exc

def add_record(kind, text, photo="", topic=""):
    if len(st.session_state.records) >= MAX_RECORDS:
        raise ValueError("최대 300개까지 보관해요. 먼저 파일로 보관한 후 대화를 비워 주세요.")
    name = st.session_state.name.strip()
    if not name:
        raise ValueError("왼쪽 메뉴에서 부를 이름을 먼저 적어 주세요.")
    if not text.strip() and not photo:
        raise ValueError("메시지를 쓰거나 사진을 골라 주세요.")
    st.session_state.records.append(dict(id=str(uuid.uuid4()), kind=kind, author=name[:30], role=st.session_state.role,
                                         text=text.strip()[:2000], created_at=now(), image_b64=photo, topic=topic))

def export_csv():
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=FIELDS)
    writer.writeheader()
    for record in st.session_state.records:
        # Excel 등의 수식 실행을 막으며, 다시 가져올 때 원래 글로 복원합니다.
        safe = {k: ("'" + str(record[k]) if str(record[k]).startswith(("=", "+", "-", "@", "\t", "\r", "'")) else record[k]) for k in FIELDS}
        writer.writerow(safe)
    return out.getvalue().encode("utf-8-sig")

def read_csv(raw):
    if len(raw) > MAX_CSV:
        raise ValueError("보관 파일은 20MB 이하만 가져올 수 있어요.")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames != FIELDS:
        raise ValueError("폰잘알 만들어줄게에서 내려받은 CSV 파일을 골라 주세요.")
    result = []
    for i, row in enumerate(reader):
        if i >= MAX_RECORDS:
            raise ValueError("파일 안의 대화는 최대 300개까지 가져올 수 있어요.")
        if None in row or any(v is None for v in row.values()):
            raise ValueError("파일의 열 개수가 맞지 않아요.")
        row = {k: (v[1:] if v.startswith("'") else v) for k, v in row.items()}
        uuid.UUID(row["id"])
        datetime.fromisoformat(row["created_at"])
        if row["kind"] not in ("chat", "help") or row["role"] not in ("부모님", "자녀"):
            raise ValueError("대화 종류나 역할을 확인해 주세요.")
        if not row["author"].strip() or len(row["author"]) > 30 or len(row["text"]) > 2000 or len(row["topic"]) > 100:
            raise ValueError("이름 또는 메시지 길이가 맞지 않아요.")
        if row["image_b64"]:
            photo = base64.b64decode(row["image_b64"], validate=True)
            if len(photo) > MAX_IMAGE:
                raise ValueError("파일 안에 너무 큰 사진이 있어요.")
            row["image_b64"] = normalize_image(photo)
        if not row["text"].strip() and not row["image_b64"]:
            raise ValueError("내용이 없는 대화가 있어요.")
        result.append(row)
    return result

DEFAULTS = {"page": "시작", "records": [], "done": [], "name": "", "role": "부모님", "scale": "크게", "lesson": "앱 설치하기", "step": 0, "chat_index": 0, "dict_index": 0, "help_stage": 0}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 크기 변경은 위젯 콜백 이후 재실행 시 즉시 반영됩니다.
font, button_height, picture_height = {"기본": (18, 52, 175), "크게": (22, 64, 190), "아주 크게": (26, 76, 200)}[st.session_state.scale]
st.markdown(f"""<style>
:root {{ --ink:#183E36; --green:#21664F; --paper:#F3F8F5; --accent:#B7521C; }}
.stApp {{background:var(--paper);color:var(--ink);font-family:system-ui,'Apple SD Gothic Neo',sans-serif;}}
.block-container {{max-width:640px;padding:1rem 1rem 2rem;}}
h1,h2,h3 {{text-align:center;color:var(--ink);word-break:keep-all;}}
h1 {{font-size:clamp(24px,6vw,34px)!important;}} h2,h3 {{font-size:{font+2}px!important;}}
p,label,li,[data-testid='stMarkdownContainer'] p {{font-size:{font}px!important;line-height:1.55;}}
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button {{width:100%;min-height:{button_height}px;border:2px solid var(--green);border-radius:17px;background:white;color:var(--ink);font-weight:750;}}
.stButton>button p,.stFormSubmitButton>button p,.stDownloadButton>button p {{font-size:{font}px!important;}}
button[kind='primary'],[data-testid='stBaseButton-primary'] {{background:var(--green)!important;color:white!important;}}
.stButton>button:hover {{border-color:var(--accent);background:#E4F1EA;}}
input,textarea {{font-size:{font}px!important;}}
.explain {{padding:14px 18px;background:#FFF5E9;border-left:5px solid var(--accent);border-radius:10px;font-size:{font}px;line-height:1.6;text-align:left;overflow-wrap:anywhere;}}
.brand {{text-align:center;font-size:14px;letter-spacing:.03em;color:#426658;margin:4px 0 12px;}}
.illustration {{display:flex;justify-content:center;margin:4px auto 10px;}}
.illustration svg {{height:{picture_height}px;max-width:100%;}}
.note {{text-align:center;color:#426658;font-size:15px;margin:8px 0;}}
[data-testid='stImage'] {{display:flex;justify-content:center;}}
button:focus-visible,input:focus-visible,textarea:focus-visible {{outline:4px solid #B7521C!important;outline-offset:3px;}}
@media(max-width:480px) {{.block-container{{padding-left:.7rem;padding-right:.7rem;}} [data-testid='stHorizontalBlock']{{gap:.45rem;}}}}
</style>""", unsafe_allow_html=True)


def explain(text):
    st.markdown('<div class="explain">'+html.escape(text)+'</div>', unsafe_allow_html=True)


def drawing(kind="logo", title="", step=0):
    """외부 이미지 없이 포함된 벡터 그림. 교육 화면은 실제 앱 캡처가 아닌 예시입니다."""
    title = html.escape(title)
    if kind == "logo":
        art = '''<circle cx="160" cy="112" r="100" fill="#DCEEE3"/>
        <rect x="111" y="30" width="98" height="162" rx="22" fill="#183E36"/>
        <rect x="119" y="42" width="82" height="132" rx="13" fill="white"/>
        <path d="M145 107 C126 88 141 70 160 87 C179 70 194 88 175 107 L160 122Z" fill="#B7521C"/>
        <path d="M55 150 Q79 123 116 145 L144 163 Q154 175 142 180 L111 166 Q87 186 70 178Z" fill="#EBC3A3"/>
        <path d="M265 150 Q241 123 204 145 L176 163 Q166 175 178 180 L209 166 Q233 186 250 178Z" fill="#EBC3A3"/>
        <circle cx="160" cy="183" r="4" fill="white"/>'''
    else:
        labels = {
          "앱 설치하기": ["앱 가게", "앱 이름 찾기", "설치 · 받기", "열기"],
          "회원가입하기": ["회원가입", "이름 · 이메일", "비밀번호", "가입 완료"],
          "로그인하기": ["로그인", "아이디 입력", "들어가기", "비밀번호 찾기"],
          "화면 사진 남기기": ["도움받을 화면", "버튼 함께 누르기", "사진 확인", "사진 올리기"]}
        label = html.escape(labels.get(kind, ["사진 선택", "사진 확인", "도움 요청", "완료"])[step % 4])
        art = f'''<rect x="90" y="8" width="140" height="206" rx="23" fill="#183E36"/>
        <rect x="98" y="23" width="124" height="174" rx="13" fill="white"/>
        <rect x="140" y="14" width="40" height="4" rx="2" fill="#87A496"/>
        <rect x="111" y="42" width="98" height="21" rx="5" fill="#E3EEE7"/>
        <rect x="111" y="76" width="98" height="17" rx="5" fill="#EEF3F0"/>
        <rect x="111" y="103" width="98" height="17" rx="5" fill="#EEF3F0"/>
        <rect x="104" y="133" width="112" height="42" rx="9" fill="#21664F"/>
        <text x="160" y="159" text-anchor="middle" fill="white" font-size="13" font-family="sans-serif">{label}</text>
        <circle cx="223" cy="168" r="16" fill="#B7521C"/><text x="223" y="174" text-anchor="middle" fill="white" font-size="18">{step+1}</text>'''
    st.markdown(f'<div class="illustration"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 225" role="img" aria-label="{title or "가족과 스마트폰 그림"}">{art}</svg></div>', unsafe_allow_html=True)


def nav():
    # 주요 기능은 모든 내부 페이지 상단에 반복 배치합니다.
    for col, (label, target) in zip(st.columns(3), [("📱 배우기", "배우기"), ("📷 도움", "도움"), ("💬 대화", "대화")]):
        if col.button(label, key="nav_"+target, type="primary" if st.session_state.page == target else "secondary", use_container_width=True):
            go(target)
    st.markdown('<div class="brand">폰잘알 만들어줄게</div>', unsafe_allow_html=True)


def message(record):
    with st.container(border=True):
        st.write(f"{'🙋' if record['role']=='부모님' else '💚'} {record['author']} · {record['role']}")
        st.caption(record['created_at'].replace('T',' '))
        if record['kind'] == 'help':
            st.write('📷 ' + record['topic'])
        if record['text']:
            st.text(record['text'])
        if record['image_b64']:
            st.image(base64.b64decode(record['image_b64']), caption="공유한 사진", width=240)


# 첫 접속에는 메뉴·개인정보 입력·체크박스 없이 브랜드 화면만 표시합니다.
if st.session_state.page != "시작":
    with st.sidebar:
        st.title("☰ 메뉴")
        for label, target in [("🏠 메인", "메인"), ("📖 쉬운 말", "사전"), ("⚙️ 크기·이름", "설정"), ("📁 파일 보관", "보관"), ("ℹ️ 이용 안내", "안내")]:
            if st.button(label, key="menu_"+target):
                go(target)
        st.caption("대화는 접속 중에만 보관돼요. 종료 전 CSV로 내려받으세요.")
    nav()

page = st.session_state.page
if page == "시작":
    drawing()
    st.title("폰잘알 만들어줄게")
    st.markdown('<div class="note">스마트폰, 가족과 함께 한 걸음</div>', unsafe_allow_html=True)
    if st.button("시작하기 →", type="primary"):
        go("메인")

elif page == "메인":
    drawing()
    st.title("무엇을 도와드릴까요?")
    # 기능 선택 화면에서는 기능명과 그림·이모지만 사용합니다.
    if st.button("📱 배우기", type="primary"):
        go("배우기")
    a,b = st.columns(2)
    if a.button("📷 도움 요청"):
        go("도움")
    if b.button("💬 가족 대화"):
        go("대화")
    if st.button("☰ 메뉴"):
        go("메뉴")

elif page == "메뉴":
    st.title("☰ 메뉴")
    for label, target in [("📖 쉬운 말", "사전"), ("⚙️ 크기·이름", "설정"), ("📁 파일 보관", "보관"), ("ℹ️ 이용 안내", "안내"), ("🏠 메인", "메인")]:
        if st.button(label):
            go(target)

elif page == "배우기":
    st.title("📱 배우기")
    for icon, lesson in zip(["📥", "🪪", "🔑", "📸"], LESSONS):
        if st.button(icon + " " + lesson):
            st.session_state.lesson = lesson
            st.session_state.step = 0
            go("교육")

elif page == "교육":
    lesson, idx = st.session_state.lesson, st.session_state.step
    steps = LESSONS[lesson]
    drawing(lesson, "학습용 휴대폰 화면 예시", idx)
    st.caption("화면 그림은 연습용 예시예요. 실제 앱과 모양이 다를 수 있어요.")
    st.subheader(f"{idx+1} / {len(steps)} · {steps[idx][0]}")
    explain(steps[idx][1])
    a,b = st.columns(2)
    if a.button("← 이전", disabled=idx==0):
        st.session_state.step -= 1
        st.rerun()
    if b.button("다음 →" if idx<3 else "완료 ✓", type="primary"):
        if idx<3:
            st.session_state.step += 1
            st.rerun()
        else:
            if lesson not in st.session_state.done:
                st.session_state.done.append(lesson)
            go("학습완료")
    if st.button("📷 이 단계 질문"):
        st.session_state.help_context = f"{lesson} · {idx+1}단계"
        st.session_state.help_stage = 0
        go("도움")

elif page == "학습완료":
    drawing()
    st.title("참 잘하셨어요! 🎉")
    if st.button("📱 다른 사용법 배우기", type="primary"):
        go("배우기")
    if st.button("🏠 메인"):
        go("메인")

elif page == "설정":
    st.title("⚙️ 크기·이름")
    st.subheader("글씨와 버튼 크기")
    cols = st.columns(3)
    for col, label in zip(cols, ["기본", "크게", "아주 크게"]):
        if col.button(label, type="primary" if st.session_state.scale == label else "secondary"):
            st.session_state.scale = label
            st.rerun()
    st.caption("고른 크기는 글씨와 버튼에 함께 적용돼요. 이번 접속에만 유지돼요.")
    with st.form("profile"):
        name = st.text_input("부를 이름", value=st.session_state.name, max_chars=30)
        role = st.selectbox("역할", ["부모님", "자녀"], index=0 if st.session_state.role=="부모님" else 1)
        if st.form_submit_button("저장 ✓", type="primary"):
            st.session_state.name = name.strip()
            st.session_state.role = role
            st.success("저장했어요.")
    st.caption("이름과 역할은 표시용이며 실제 회원가입·로그인이 아니에요.")

elif page == "사전":
    st.title("📖 쉬운 말")
    query = st.text_input("말 찾기", placeholder="예: 로그인")
    terms = [(k,v) for k,v in WORDS.items() if query.casefold() in (k+v).casefold()]
    if terms:
        idx = min(st.session_state.dict_index, len(terms)-1)
        st.subheader(terms[idx][0])
        explain(terms[idx][1])
        st.caption(f"{idx+1} / {len(terms)}")
        a,b = st.columns(2)
        if a.button("← 이전", disabled=idx==0):
            st.session_state.dict_index=idx-1
            st.rerun()
        if b.button("다음 →", disabled=idx==len(terms)-1):
            st.session_state.dict_index=idx+1
            st.rerun()
    else:
        st.info("아직 없는 말이에요. 가족에게 물어보세요.")

elif page == "도움":
    st.title("📷 도움 요청")
    stage = st.session_state.help_stage
    if stage == 0:
        explain("1. 막힌 화면 사진을 골라 주세요. 비밀번호·인증번호·계좌번호는 먼저 가리세요.")
        method = st.selectbox("사진 가져오기", ["저장된 사진", "카메라"])
        upload = st.file_uploader("사진 선택 · 3MB 이하", type=["jpg","jpeg","png","webp"], key="help_image") if method == "저장된 사진" else st.camera_input("다른 휴대폰 화면 촬영")
        if st.button("다음 →", type="primary"):
            try:
                if upload is None:
                    raise ValueError("사진을 먼저 골라 주세요.")
                st.session_state.draft_image = image_data(upload)
                st.session_state.help_stage = 1
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
        if st.button("💬 사진 없이 질문"):
            st.session_state.draft_image = ""
            st.session_state.help_stage = 1
            st.rerun()
    else:
        st.caption("2 / 2 · 질문 남기기")
        photo = st.session_state.get("draft_image", "")
        if photo:
            st.image(base64.b64decode(photo), width=180, caption="중요한 정보가 없는지 확인하세요")
        with st.form("help_send"):
            topic = st.text_input("질문 제목", value=st.session_state.get("help_context", "스마트폰 사용 질문"), max_chars=100)
            text = st.text_area("궁금한 점", max_chars=2000, height=90, placeholder="예: 여기서 무엇을 누르나요?")
            st.caption("아래 버튼을 누르기 전 사진과 글의 개인정보를 확인하세요.")
            sent = st.form_submit_button("확인했어요 · 질문 남기기", type="primary")
        if sent:
            try:
                add_record("help", text, photo, topic)
                st.session_state.help_stage=0
                go("작성완료")
            except ValueError as exc:
                st.error(str(exc))
                if not st.session_state.name.strip():
                    st.caption("☰ 메뉴 → 크기·이름에서 이름을 저장하세요.")
        if st.button("← 사진 다시 고르기"):
            st.session_state.help_stage=0
            st.rerun()

elif page == "대화":
    st.title("💬 가족 대화")
    a,b=st.columns(2)
    if a.button("✏️ 글·사진 남기기", type="primary"):
        go("메시지작성")
    if b.button("📁 파일 교환"):
        go("보관")
    records = sorted(st.session_state.records,key=lambda r: datetime.fromisoformat(r['created_at']).timestamp())
    if records:
        idx = min(st.session_state.chat_index, len(records)-1)
        message(records[idx])
        st.caption(f"{idx+1} / {len(records)} · 한 번에 한 대화씩 보여요")
        a,b=st.columns(2)
        if a.button("← 이전 대화", disabled=idx==0):
            st.session_state.chat_index=idx-1
            st.rerun()
        if b.button("다음 대화 →", disabled=idx==len(records)-1):
            st.session_state.chat_index=idx+1
            st.rerun()
    else:
        drawing()
        explain("아직 대화가 없어요. 첫 인사를 남겨 보세요.")
    st.caption("실시간 전송이 아니에요. CSV를 주고받아 대화를 이어가요.")

elif page == "메시지작성":
    st.title("✏️ 가족에게 한마디")
    with st.form("send_message", clear_on_submit=False):
        text = st.text_area("메시지", max_chars=2000, height=100)
        upload = st.file_uploader("사진 · 선택 · 3MB 이하", type=["jpg","jpeg","png","webp"])
        st.caption("비밀번호·인증번호 등 중요한 정보는 올리지 마세요.")
        submit = st.form_submit_button("정보 확인했어요 · 남기기", type="primary")
    if submit:
        try:
            add_record("chat",text,image_data(upload))
            st.session_state.chat_index=len(st.session_state.records)-1
            go("작성완료")
        except ValueError as exc:
            st.error(str(exc))
            if not st.session_state.name.strip():
                st.caption("☰ 메뉴 → 크기·이름에서 이름을 저장하세요.")

elif page == "작성완료":
    drawing()
    st.title("남겼어요 ✓")
    explain("가족에게 전달하려면 CSV를 내려받아 평소 쓰는 메시지 앱으로 보내 주세요.")
    if st.button("📁 파일 내려받기", type="primary"):
        go("보관")
    if st.button("💬 대화 보기"):
        st.session_state.chat_index=max(0,len(st.session_state.records)-1)
        go("대화")

elif page == "보관":
    st.title("📁 파일 보관")
    for label,target in [("⬇ 대화 내려받기","내려받기"),("⬆ 가족 파일 가져오기","가져오기"),("🗑 대화 비우기","비우기")]:
        if st.button(label):
            go(target)
    st.caption("사진과 글을 CSV 한 파일로 보관해요. 학습 진도·설정은 포함되지 않아요.")

elif page == "내려받기":
    st.title("⬇ 대화 내려받기")
    explain("파일을 내려받은 다음 카카오톡 등 평소 쓰는 메시지 앱으로 가족에게 보내 주세요. 공개 GitHub에는 올리지 마세요.")
    raw=export_csv()
    if len(raw)<=MAX_CSV:
        st.download_button("📥 CSV 내려받기",raw,file_name="ponjalal_"+datetime.now().strftime('%Y%m%d_%H%M%S')+".csv",mime="text/csv",disabled=not st.session_state.records)
    else:
        st.error("파일이 20MB를 넘었어요. 현재 파일은 내려받을 수 있지만 다시 가져오기는 20MB 이하만 가능해요.")
        st.download_button("전체 백업 내려받기",raw,file_name="ponjalal_large_backup.csv",mime="text/csv")
    st.caption(f"대화 {len(st.session_state.records)}개 · CSV는 암호화되지 않아요.")

elif page == "가져오기":
    st.title("⬆ 가족 파일 가져오기")
    upload=st.file_uploader("CSV 선택 · 20MB 이하",type=["csv"])
    if st.button("대화 합치기",disabled=upload is None,type="primary"):
        try:
            incoming=read_csv(upload.getvalue())
            existing={r['id']:r for r in st.session_state.records}
            before=len(existing)
            for r in incoming:
                if r['id'] not in existing:
                    existing[r['id']]=r
            if len(existing)>MAX_RECORDS:
                raise ValueError("합치면 300개를 넘어요. 먼저 현재 대화를 보관해 주세요.")
            if sum(len(r['image_b64'])+len(r['text'].encode('utf-8'))+1000 for r in existing.values())>MAX_CSV-100000:
                raise ValueError("합친 파일이 너무 커요. 더 작은 사진으로 나누어 보내 주세요.")
            st.session_state.records=list(existing.values())
            st.session_state.chat_index=max(0,len(existing)-1)
            st.success(f"새 대화 {len(existing)-before}개를 합쳤어요.")
        except Exception as exc:
            st.error("가져오지 못했어요. "+(str(exc) if isinstance(exc,ValueError) else "CSV 파일을 확인해 주세요."))
    if st.button("💬 대화 보기"):
        go("대화")

elif page == "비우기":
    st.title("🗑 대화 비우기")
    explain("현재 접속의 사진과 대화가 모두 지워져요. 먼저 CSV를 내려받아 주세요.")
    if st.button("CSV 보관했어요 · 삭제 확인",type="primary"):
        go("삭제확인")
    if st.button("취소"):
        go("보관")

elif page == "삭제확인":
    st.title("정말 지울까요?")
    if st.button("네 · 모두 지우기",type="primary"):
        st.session_state.records=[]
        st.session_state.chat_index=0
        go("대화")
    if st.button("아니요 · 돌아가기"):
        go("보관")

elif page == "안내":
    st.title("ℹ️ 이용 안내")
    explain("대화와 사진은 지금 접속한 동안만 남아요. 새로고침하거나 접속을 끝내기 전에 CSV를 내려받으세요. 다른 휴대폰으로 자동 전송되는 실시간 채팅은 아니에요.")
    with st.expander("사진과 개인정보"):
        st.write("사진은 JPG·PNG·WEBP, 최대 3MB예요. 사진의 촬영 위치 등 부가정보는 다시 저장하며 제거해요. 사진에 보이는 개인정보를 자동으로 가려 주지는 않아요. CSV는 암호화되지 않아요.")
    with st.expander("가족이 사용하는 순서"):
        st.write("부모님이 글이나 사진을 남겨요 → CSV를 내려받아 자녀에게 보내요 → 자녀가 CSV를 가져와 답장을 남겨요 → 다시 CSV를 보내요. 이름과 역할은 표시용이고 가족 인증 기능은 없어요.")
    with st.expander("화면과 학습"):
        st.write("기능은 별도 화면으로 바뀌어요. 교육·사전·대화는 하나씩 넘겨 봐요. 아주 작은 화면, 아주 큰 글씨, 사진·입력창에서는 내용이 잘리지 않도록 스크롤이 남을 수 있어요. 학습 그림은 실제 앱 캡처가 아닌 설명용 예시예요.")
