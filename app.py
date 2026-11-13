"""가족 손길 | 실행: streamlit run app.py
Streamlit Community Cloud에서 app.py를 시작 파일로 선택하세요.
CSV 파일 교환형 시제품입니다. 실제 계정 인증/실시간 전송/서버 영구 저장은 하지 않습니다.
"""
import base64
import csv
import hashlib
import io
import uuid
import warnings
from datetime import datetime

import streamlit as st
from PIL import Image, ImageOps

st.set_page_config(page_title="가족 손길", page_icon="🌷", layout="centered")
MAX_IMAGE = 3 * 1024 * 1024
MAX_CSV = 20 * 1024 * 1024
MAX_RECORDS = 300
FIELDS = ["id", "kind", "author", "role", "text", "created_at", "image_b64", "topic"]
csv.field_size_limit(8 * 1024 * 1024)

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

for key, default in {"page": "시작", "records": [], "done": [], "name": "", "role": "부모님", "large": True}.items():
    if key not in st.session_state:
        st.session_state[key] = default
size = 23 if st.session_state.large else 19
st.markdown(f"""<style>
.stApp {{background:#FAF8F3;color:#203A35;}}
.block-container {{max-width:850px;padding-top:2rem;padding-bottom:4rem;}}
p,li,label,[data-testid='stMarkdownContainer'] p {{font-size:{size}px !important;line-height:1.75;}}
h1 {{color:#215D4E;font-size:2.35rem !important;}} h2 {{color:#215D4E;}}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button {{min-height:64px;width:100%;font-size:{size}px !important;border-radius:16px;border:2px solid #387563;}}
.stTextInput input,.stTextArea textarea {{font-size:{size}px !important;}}
[data-testid='stMetricValue'] {{color:#215D4E;}}
button:focus-visible,input:focus-visible,textarea:focus-visible {{outline:4px solid #A55E0B !important;outline-offset:3px;}}
</style>""", unsafe_allow_html=True)


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
        raise ValueError("가족 손길에서 내려받은 CSV 파일을 골라 주세요.")
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


def show_records(items):
    if not items:
        st.info("아직 대화가 없어요. 첫 인사를 남겨 보세요.")
    for record in items:
        with st.container(border=True):
            st.write(f"{'🙋' if record['role'] == '부모님' else '💚'} {record['author']} · {record['role']}")
            st.caption(record["created_at"].replace("T", " "))
            if record["kind"] == "help":
                st.write("도움 요청 · " + record["topic"])
            if record["text"]:
                st.text(record["text"])
            if record["image_b64"]:
                st.image(base64.b64decode(record["image_b64"]), caption="가족이 공유한 사진")


with st.sidebar:
    st.title("🌷 가족 손길")
    st.caption("천천히 배워도 괜찮아요")
    st.text_input("나를 부를 이름", key="name", max_chars=30, placeholder="예: 엄마, 아빠, 민지")
    st.radio("나의 역할", ["부모님", "자녀"], key="role")
    st.caption("이름과 역할은 표시용이에요. 실제 로그인이나 본인 확인 기능은 아니에요.")
    st.toggle("더 큰 글씨", key="large", on_change=lambda: None)
    page = st.selectbox("이동할 화면", ["시작", "메인", "사용법 배우기", "쉬운 말 사전", "사진으로 도움", "가족 대화방", "파일 보관함"], index=["시작", "메인", "사용법 배우기", "쉬운 말 사전", "사진으로 도움", "가족 대화방", "파일 보관함"].index(st.session_state.page))
    if page != st.session_state.page:
        go(page)
    st.warning("대화는 현재 접속 안에서만 보관돼요. 끝내기 전에 CSV로 내려받아 주세요.")

page = st.session_state.page
if page != "시작":
    if st.button("⌂ 메인 화면으로", key="home"):
        go("메인")

if page == "시작":
    st.title("🌷 가족 손길")
    st.header("스마트폰, 함께하면 쉬워져요")
    st.write("한 번에 하나씩 배우고, 막히면 가족에게 물어보세요. 잘못 눌러도 괜찮아요.")
    st.info("① 왼쪽 메뉴에서 이름 쓰기 → ② 사용법 배우기 → ③ 사진과 메시지로 도움받기")
    if st.button("시작하기 →", type="primary"):
        go("메인")
    st.caption("휴대폰에서는 화면 왼쪽 위 메뉴를 눌러 이름과 역할을 설정할 수 있어요.")

elif page == "메인":
    st.title("오늘도 함께, 한 걸음")
    st.write(f"{st.session_state.name.strip() or '가족'}님, 무엇을 도와드릴까요?")
    for label, target in [("📱 스마트폰 사용법 배우기", "사용법 배우기"), ("📖 어려운 말을 쉽게 찾기", "쉬운 말 사전"), ("📷 사진으로 도움 요청하기", "사진으로 도움"), ("💬 가족과 이야기 나누기", "가족 대화방"), ("📁 대화 보관하고 가져오기", "파일 보관함")]:
        if st.button(label, key="main_" + target):
            go(target)
    st.success(f"이번 접속에서 배운 사용법: {len(st.session_state.done)} / {len(LESSONS)}개")
    st.caption("학습 완료 표시는 이번 접속에만 남아요. CSV에는 사진과 대화만 담겨요.")

elif page == "사용법 배우기":
    st.title("📱 한 번에 하나씩 배워요")
    lesson = st.selectbox("배우고 싶은 것을 골라 주세요", list(LESSONS))
    key = "step_" + lesson
    if key not in st.session_state:
        st.session_state[key] = 0
    idx = st.session_state[key]
    steps = LESSONS[lesson]
    st.progress((idx + 1) / len(steps))
    st.subheader(f"{idx + 1}단계 / {len(steps)}단계 · {steps[idx][0]}")
    st.write(steps[idx][1])
    prev, nxt = st.columns(2)
    if prev.button("← 이전 단계", disabled=idx == 0):
        st.session_state[key] -= 1
        st.rerun()
    if nxt.button("다음 단계 →" if idx < len(steps) - 1 else "다 배웠어요 ✓", type="primary"):
        if idx < len(steps) - 1:
            st.session_state[key] += 1
            st.rerun()
        else:
            if lesson not in st.session_state.done:
                st.session_state.done.append(lesson)
            st.success("잘하셨어요! 필요할 때 언제든 다시 보세요.")
    if st.button("이 단계가 어려워요 · 가족에게 묻기"):
        st.session_state.help_context = f"{lesson} · {idx + 1}단계: {steps[idx][0]}"
        go("사진으로 도움")

elif page == "쉬운 말 사전":
    st.title("📖 쉬운 말 사전")
    query = st.text_input("궁금한 말을 써 주세요", placeholder="예: 로그인, 인증번호").strip()
    found = [(k, v) for k, v in WORDS.items() if query.casefold() in (k + v).casefold()]
    if not found:
        st.info("아직 없는 말이에요. 가족 대화방에서 물어보세요.")
    for word, meaning in found:
        with st.container(border=True):
            st.subheader(word)
            st.write(meaning)

elif page == "사진으로 도움":
    st.title("📷 어디에서 막히셨나요?")
    st.write("막힌 화면의 사진과 궁금한 점을 남겨 주세요.")
    st.warning("비밀번호·인증번호·계좌번호·신분증은 올리지 마세요. 사진을 잘라내거나 가린 뒤 올려 주세요.")
    topic = st.text_input("어떤 도움이 필요한가요?", value=st.session_state.get("help_context", "스마트폰 사용 질문"), max_chars=100)
    mode = st.radio("사진을 가져오는 방법", ["저장된 사진 고르기", "카메라로 찍기"], horizontal=False)
    photo = st.file_uploader("사진 고르기 · 3MB 이하", type=["jpg", "jpeg", "png", "webp"], key="help_upload") if mode == "저장된 사진 고르기" else st.camera_input("다른 휴대폰의 화면을 찍어 주세요", key="help_camera")
    if photo:
        try:
            checked = image_data(photo)
            st.image(base64.b64decode(checked), caption="올리기 전 사진을 확인해 주세요")
        except ValueError as exc:
            st.error(str(exc))
    with st.form("help_form", clear_on_submit=True):
        text = st.text_area("궁금한 점", placeholder="예: 설치 버튼이 어디에 있는지 모르겠어요.", max_chars=2000)
        agreed = st.checkbox("사진과 글에 비밀번호 등 중요한 정보가 없는지 확인했어요")
        submitted = st.form_submit_button("도움 요청 남기기", type="primary")
    if submitted:
        try:
            if not agreed:
                raise ValueError("중요한 정보가 없는지 확인하고 체크해 주세요.")
            add_record("help", text, image_data(photo), topic)
            st.success("이 접속의 대화방에 남겼어요. 가족에게 전달하려면 파일 보관함에서 CSV를 내려받아 보내 주세요.")
        except ValueError as exc:
            st.error(str(exc))
    if st.button("가족 대화방 보기"):
        go("가족 대화방")

elif page == "가족 대화방":
    st.title("💬 가족 대화방")
    st.info("파일 교환형 대화방이에요. 다른 휴대폰으로 자동 전송되지 않아요. CSV를 보내고 가져오면 대화가 합쳐져요.")
    only_help = st.checkbox("도움 요청만 보기")
    records = sorted(st.session_state.records, key=lambda r: datetime.fromisoformat(r["created_at"]).timestamp())
    show_records([r for r in records if not only_help or r["kind"] == "help"])
    with st.form("chat_form", clear_on_submit=True):
        st.subheader("가족에게 한마디")
        text = st.text_area("메시지", max_chars=2000, placeholder="예: 엄마, 화면 아래 초록색 버튼을 눌러 보세요.")
        photo = st.file_uploader("사진도 함께 올릴 수 있어요 · 3MB 이하", type=["jpg", "jpeg", "png", "webp"], key="chat_photo")
        agreed = st.checkbox("중요한 개인정보가 없는지 확인했어요")
        submitted = st.form_submit_button("메시지 남기기", type="primary")
    if submitted:
        try:
            if not agreed:
                raise ValueError("중요한 정보가 없는지 먼저 확인해 주세요.")
            add_record("chat", text, image_data(photo))
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

elif page == "파일 보관함":
    st.title("📁 가족의 대화 보관함")
    st.write("1. 아래에서 대화 파일을 내려받아요.\n\n2. 평소 사용하는 메시지 앱으로 가족에게 파일을 보내요.\n\n3. 가족은 자신의 앱에서 파일을 가져와요.\n\n4. 답장을 남긴 뒤 다시 내려받아 보내면 돼요.")
    st.warning("CSV에는 사진과 대화가 함께 들어 있어요. 암호화나 가족 인증 기능이 없으니 공개 GitHub 저장소에 올리지 말고 가족에게만 보내세요. 이 앱은 연결된 가족 계정을 제공하지 않아요.")
    st.write(f"현재 보관 중: {len(st.session_state.records)}개 / 최대 {MAX_RECORDS}개")
    raw = export_csv()
    if len(raw) <= MAX_CSV:
        st.download_button("⬇ 사진과 대화 CSV 내려받기", raw, file_name="family_touch_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv", mime="text/csv", disabled=not st.session_state.records)
    else:
        st.error("보관 파일이 20MB를 넘었어요. 더 작은 사진을 사용해 주세요.")
    uploaded = st.file_uploader("⬆ 가족이 보낸 CSV 가져오기 · 20MB 이하", type=["csv"])
    if st.button("파일을 확인하고 대화 합치기", disabled=uploaded is None):
        try:
            incoming = read_csv(uploaded.getvalue())
            existing = {r["id"]: r for r in st.session_state.records}
            count = 0
            for record in incoming:
                if record["id"] not in existing:
                    existing[record["id"]] = record
                    count += 1
            if len(existing) > MAX_RECORDS:
                raise ValueError("합치면 300개를 넘어요. 현재 대화를 보관하고 비운 다음 가져와 주세요.")
            # 내보내기 가능한 용량을 초과하는 가져오기는 반영하지 않습니다.
            if sum(len(r["image_b64"]) + len(r["text"].encode("utf-8")) + 1000 for r in existing.values()) > MAX_CSV - 100000:
                raise ValueError("합친 파일이 너무 커요. 더 작은 사진을 사용해 주세요.")
            st.session_state.records = list(existing.values())
            st.success(f"새 대화 {count}개를 합쳤어요. 같은 번호의 대화는 중복으로 추가하지 않아요.")
        except Exception as exc:
            st.error("파일을 가져오지 못했어요. " + (str(exc) if isinstance(exc, ValueError) else "가족 손길에서 받은 CSV인지 확인해 주세요."))
    st.divider()
    st.subheader("이 접속의 대화 비우기")
    confirm = st.checkbox("CSV를 내려받았고, 현재 대화를 모두 비워도 괜찮아요")
    if st.button("현재 대화 모두 비우기", disabled=not confirm):
        st.session_state.records = []
        st.rerun()

st.divider()
st.caption("가족 손길 · 서두르지 않아도 괜찮아요. 대화와 사진은 CSV로 보관하세요. 화면 새로고침이나 접속 종료 시 현재 기록이 사라질 수 있어요.")
