import streamlit as st
import requests
from datetime import datetime
from io import BytesIO
from PIL import Image

# ------------------------------------------------------------
# 우리家 - 중장년층을 위한 스마트폰 배움 & 가족 소통 앱
# 실행: streamlit run app.py
# 실제 가족 간 공유를 사용하려면 Supabase 설정이 필요합니다.
# ------------------------------------------------------------

st.set_page_config(
    page_title="우리家 | 스마트폰 도우미",
    page_icon="🏡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- 디자인 ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: #F7F7F0; }
.block-container { max-width: 850px; padding-top: 1.5rem; padding-bottom: 3rem; }
h1, h2, h3, p, label { color: #24352D; }
.hero {
    background: linear-gradient(135deg, #E3F0E5, #F1F5E9);
    border: 1px solid #D5E5D7; border-radius: 24px;
    padding: 28px 24px; text-align: center; margin-bottom: 18px;
}
.hero-logo { font-size: 3.5rem; line-height: 1.2; }
.hero-title { font-size: 2.15rem; font-weight: 800; color: #24583B; margin: 8px 0; }
.hero-sub { font-size: 1.12rem; color: #466451; }
div.stButton > button {
    min-height: 68px; width: 100%; border-radius: 16px;
    border: 1px solid #D7E3D8; background: #FFFFFF;
    color: #254735; font-size: 1.15rem; font-weight: 700;
    white-space: normal; padding: 12px 16px;
}
div.stButton > button:hover { border-color: #5D966B; background: #EDF5EE; color: #204B31; }
div[data-testid="stFileUploader"] {
    background: #FFFFFF; border: 1px dashed #A9C5AE;
    border-radius: 16px; padding: 12px;
}
.info-card {
    background: #FFFFFF; border: 1px solid #E1E8DF;
    border-radius: 18px; padding: 18px; margin: 10px 0;
}
.step {
    background: #FFFFFF; border-left: 6px solid #6D9E78;
    border-radius: 12px; padding: 15px 17px; margin: 10px 0;
    font-size: 1.08rem;
}
.small-note { color: #66766A; font-size: .92rem; }
.chat-me { background: #E4F1E5; padding: 12px 16px; border-radius: 16px 16px 4px 16px; margin: 8px 0 8px 18%; }
.chat-other { background: #FFFFFF; border: 1px solid #E2E8E1; padding: 12px 16px; border-radius: 16px 16px 16px 4px; margin: 8px 18% 8px 0; }
</style>
""", unsafe_allow_html=True)

# ---------- Supabase 연결 ----------
def get_setting(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

SUPABASE_URL = get_setting("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = get_setting("SUPABASE_ANON_KEY", "")
BUCKET = "family-photos"

def cloud_ready():
    return bool(SUPABASE_URL and SUPABASE_KEY)

def headers(extra=None):
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    if extra:
        h.update(extra)
    return h

def get_cloud_messages(room):
    url = f"{SUPABASE_URL}/rest/v1/family_messages"
    params = {
        "select": "*",
        "room_code": f"eq.{room}",
        "order": "created_at.asc",
        "limit": "100",
    }
    try:
        r = requests.get(url, headers=headers(), params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error("가족 대화 내용을 불러오지 못했어요. Supabase 설정을 확인해 주세요.")
        return []

def send_cloud_message(room, sender, kind, content="", image_url=""):
    url = f"{SUPABASE_URL}/rest/v1/family_messages"
    payload = {
        "room_code": room,
        "sender": sender,
        "kind": kind,
        "content": content,
        "image_url": image_url,
    }
    try:
        r = requests.post(
            url, headers=headers({"Content-Type": "application/json", "Prefer": "return=minimal"}),
            json=payload, timeout=20
        )
        r.raise_for_status()
        return True
    except Exception:
        st.error("메시지를 보내지 못했어요. Supabase의 표와 권한 설정을 확인해 주세요.")
        return False

def upload_cloud_image(room, uploaded_file):
    safe_name = f"{room}/{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uploaded_file.name.replace(' ', '_')}"
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{safe_name}"
    content_type = uploaded_file.type or "application/octet-stream"
    try:
        r = requests.post(
            url,
            headers=headers({"Content-Type": content_type, "x-upsert": "false"}),
            data=uploaded_file.getvalue(),
            timeout=30
        )
        r.raise_for_status()
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{safe_name}"
    except Exception:
        st.error("사진을 올리지 못했어요. 사진 저장 공간과 권한 설정을 확인해 주세요.")
        return ""

# ---------- 상태 ----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "person" not in st.session_state:
    st.session_state.person = "부모님"
if "room" not in st.session_state:
    st.session_state.room = "우리집"
if "local_messages" not in st.session_state:
    st.session_state.local_messages = []
if "tutorial_index" not in st.session_state:
    st.session_state.tutorial_index = 0

def go(page):
    st.session_state.page = page
    st.rerun()

def top_bar():
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("🏡 처음", key="top_home"):
            go("home")
    with c2:
        st.markdown("<div style='padding-top:14px;font-size:1.05rem;font-weight:700;color:#315C3D'>우리家 · 스마트폰 도우미</div>", unsafe_allow_html=True)
    st.divider()

def page_title(icon, title, desc=""):
    st.markdown(f"## {icon} {title}")
    if desc:
        st.markdown(f"<p style='font-size:1.05rem;color:#617266'>{desc}</p>", unsafe_allow_html=True)

def show_message(message, sender, kind="text", content="", image_url=""):
    if cloud_ready():
        return send_cloud_message(st.session_state.room, sender, kind, content, image_url)
    st.session_state.local_messages.append({
        "sender": sender, "kind": kind, "content": content,
        "image_url": image_url, "created_at": datetime.now().isoformat()
    })
    return True

def all_messages():
    if cloud_ready():
        return get_cloud_messages(st.session_state.room)
    return st.session_state.local_messages

# ---------- 시작 / 로고 화면 ----------
if st.session_state.page == "welcome":
    st.markdown("""
    <div class="hero">
      <div class="hero-logo">🏡📱</div>
      <div class="hero-title">우리家</div>
      <div class="hero-sub">스마트폰은 쉽게 배우고,<br>가족과는 더 가까워져요.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;font-size:1.12rem;margin:20px 0'>처음부터 천천히, 함께 해봐요!</div>", unsafe_allow_html=True)
    if st.button("시작하기  →", key="start", type="primary"):
        go("home")
    st.stop()

# ---------- 공통 상단 ----------
top_bar()

# ---------- 메인 화면 ----------
if st.session_state.page == "home":
    st.markdown("""
    <div class="hero">
      <div class="hero-logo">🏡</div>
      <div class="hero-title">우리家</div>
      <div class="hero-sub">모르는 건 배우고, 어려운 건 가족에게 물어봐요.</div>
    </div>
    """, unsafe_allow_html=True)

    a, b = st.columns(2)
    with a:
        if st.button("📱  스마트폰 배우기\n쉬운 설명을 보며 따라 해요"):
            go("learn")
        if st.button("💬  가족과 대화하기\n메시지와 사진을 주고받아요"):
            go("chat")
    with b:
        if st.button("🙋  도와주세요\n어려운 화면을 가족에게 보내요"):
            go("help")
        if st.button("🖼️  가족 사진첩\n가족이 나눈 사진을 모아 봐요"):
            go("gallery")

    st.markdown("<div class='info-card'><b>🌱 오늘의 작은 팁</b><br>잘못 눌러도 괜찮아요. 대부분은 이전 화면으로 돌아갈 수 있어요.</div>", unsafe_allow_html=True)
    with st.expander("⚙️ 우리 가족 설정"):
        st.session_state.person = st.selectbox("나는 누구인가요?", ["부모님", "자녀", "가족"])
        st.session_state.room = st.text_input("가족방 이름 (가족끼리 똑같이 입력)", value=st.session_state.room, help="예: 우리집")
        st.caption("가족방 이름을 가족 모두 똑같이 입력해야 같은 대화방을 볼 수 있어요.")
        if cloud_ready():
            st.success("가족 간 공유 모드가 연결되어 있어요.")
        else:
            st.warning("현재 체험 모드예요. 다른 휴대폰과 공유하려면 아래 '앱 연결 안내'에서 Supabase를 연결해 주세요.")

# ---------- 스마트폰 배우기 ----------
elif st.session_state.page == "learn":
    page_title("📱", "스마트폰 배우기", "궁금한 주제를 고르고 한 단계씩 따라 해보세요.")
    lessons = {
        "앱 설치하기": [
            "휴대폰에서 'Play 스토어' 또는 '앱스토어'를 찾아 눌러요.",
            "화면 위쪽의 검색 칸을 눌러 설치할 앱 이름을 적어요.",
            "검색 결과에서 원하는 앱을 확인하고 '설치' 또는 '받기'를 눌러요.",
            "설치가 끝나면 '열기'를 눌러 앱을 시작해요."
        ],
        "회원가입하기": [
            "앱을 열고 '회원가입' 또는 '새 계정 만들기'를 눌러요.",
            "이름과 안내된 정보를 차례대로 적어요.",
            "휴대폰 문자로 숫자 인증번호가 오면 앱에 입력해요.",
            "비밀번호를 만들고 가입을 마쳐요. 비밀번호는 가족에게도 함부로 알려주지 마세요."
        ],
        "로그인하기": [
            "앱을 열고 '로그인'을 눌러요.",
            "가입할 때 사용한 이메일이나 전화번호를 적어요.",
            "내가 정한 비밀번호를 입력해요.",
            "'로그인'을 누르면 내 계정으로 들어갈 수 있어요."
        ],
        "사진 보내기": [
            "가족과 대화하는 화면을 열어요.",
            "글을 쓰는 칸 옆의 '+' 또는 사진 모양을 눌러요.",
            "보내고 싶은 사진을 골라요.",
            "'전송' 또는 종이비행기 모양을 누르면 사진이 전달돼요."
        ],
        "와이파이 연결하기": [
            "휴대폰의 '설정'을 열어요.",
            "'Wi-Fi' 또는 '와이파이'를 눌러요.",
            "집이나 장소의 와이파이 이름을 골라요.",
            "비밀번호를 입력하고 '연결'을 눌러요."
        ],
        "글씨 크게 바꾸기": [
            "휴대폰의 '설정'을 열어요.",
            "'디스플레이' 또는 '화면' 메뉴를 찾아요.",
            "'글자 크기'를 눌러요.",
            "막대를 움직여 글씨를 편하게 읽을 수 있는 크기로 바꿔요."
        ],
        "앱 삭제하기": [
            "지우고 싶은 앱 아이콘을 손가락으로 길게 눌러요.",
            "'삭제' 또는 '앱 제거'를 찾아 눌러요.",
            "정말 지울지 물어보면 앱 이름을 확인해요.",
            "필요 없는 앱이 맞을 때만 '삭제'를 눌러요."
        ],
    }
    selected = st.selectbox("무엇을 배우고 싶으세요?", list(lessons.keys()))
    st.markdown(f"### 🌼 {selected}")
    st.info("휴대폰 기종이나 화면에 따라 글자와 버튼 이름이 조금 다를 수 있어요.")
    for i, step in enumerate(lessons[selected], 1):
        st.markdown(f"<div class='step'><b>{i}단계</b><br>{step}</div>", unsafe_allow_html=True)
    st.markdown("#### 👍 여기까지 해보셨나요?")
    if st.button("다 했어요! 가족에게 알려주기"):
        show_message("", st.session_state.person, "text", f"'{selected}' 사용법을 따라 해봤어요!")
        st.success("가족방에 완료 소식을 보냈어요!" if cloud_ready() else "완료 소식을 이 기기의 체험 대화에 저장했어요.")
    if st.button("잘 모르겠어요. 도움 요청하기"):
        go("help")

# ---------- 도움 요청 ----------
elif st.session_state.page == "help":
    page_title("🙋", "도와주세요", "어려운 화면을 사진으로 찍어 가족에게 물어볼 수 있어요.")
    st.markdown("<div class='info-card'>📷 <b>사진 올리는 방법</b><br>휴대폰 화면을 다른 휴대폰으로 찍거나, 지금 사용 중인 기기에서 화면 사진을 골라 올려주세요.</div>", unsafe_allow_html=True)
    photo = st.file_uploader("어려운 화면 사진 고르기", type=["png", "jpg", "jpeg"])
    if photo:
        st.image(photo, caption="올릴 사진 미리 보기", use_container_width=True)
    question = st.text_area("무엇이 어려우신가요?", placeholder="예: 여기서 어떤 버튼을 눌러야 할지 모르겠어요.", height=110)
    if st.button("가족에게 도움 요청 보내기", type="primary"):
        if not photo and not question.strip():
            st.warning("사진을 올리거나 질문을 적어주세요.")
        else:
            image_url = ""
            if photo and cloud_ready():
                image_url = upload_cloud_image(st.session_state.room, photo)
            elif photo:
                st.session_state.local_messages.append({
                    "sender": st.session_state.person, "kind": "image_local",
                    "content": question, "image_bytes": photo.getvalue(),
                    "created_at": datetime.now().isoformat()
                })
            if not photo or cloud_ready():
                show_message("", st.session_state.person, "help", question or "이 화면을 어떻게 사용하면 될까요?", image_url)
            st.success("가족에게 도움 요청을 보냈어요!" if cloud_ready() else "체험 모드에 저장했어요. 실제 가족 공유에는 앱 연결이 필요해요.")
    st.caption("🔒 계좌번호, 비밀번호, 인증번호처럼 중요한 정보가 보이는 화면은 사진으로 보내지 마세요.")

# ---------- 가족 채팅 ----------
elif st.session_state.page == "chat":
    page_title("💬", "가족과 대화하기", "가족방 이름을 맞추면 같은 대화 내용을 볼 수 있어요.")
    st.session_state.person = st.selectbox("보내는 사람", ["부모님", "자녀", "가족"], key="chat_person")
    st.session_state.room = st.text_input("가족방 이름", value=st.session_state.room, key="chat_room")
    if not cloud_ready():
        st.warning("현재는 이 브라우저 안에서만 보이는 체험 모드예요. 서로 다른 휴대폰에서 대화하려면 Supabase 연결이 필요해요.")
    messages = all_messages()
    if not messages:
        st.markdown("<div class='info-card'>아직 대화가 없어요. 첫 인사를 보내보세요! 👋</div>", unsafe_allow_html=True)
    for m in messages:
        sender = m.get("sender", "가족")
        mine = sender == st.session_state.person
        css = "chat-me" if mine else "chat-other"
        st.markdown(f"<div class='{css}'><b>{sender}</b><br>{m.get('content','')}</div>", unsafe_allow_html=True)
        image_url = m.get("image_url", "")
        if image_url:
            st.image(image_url, use_container_width=True)
        if m.get("kind") == "image_local" and m.get("image_bytes"):
            st.image(m["image_bytes"], use_container_width=True)
    st.divider()
    with st.form("send_message_form", clear_on_submit=True):
        msg = st.text_input("메시지를 적어주세요", placeholder="예: 오늘 사진 고마워요!")
        send = st.form_submit_button("보내기 ✉️")
    if send:
        if msg.strip():
            if show_message("", st.session_state.person, "text", msg.strip()):
                st.rerun()
        else:
            st.warning("메시지를 먼저 적어주세요.")
    if st.button("대화 새로고침"):
        st.rerun()

# ---------- 가족 사진첩 ----------
elif st.session_state.page == "gallery":
    page_title("🖼️", "가족 사진첩", "가족방에서 주고받은 사진을 모아볼 수 있어요.")
    messages = all_messages()
    photos = [m for m in messages if m.get("image_url") or (m.get("kind") == "image_local" and m.get("image_bytes"))]
    if not photos:
        st.info("아직 공유된 사진이 없어요. '도와주세요'나 가족 대화에서 사진을 올려보세요.")
    else:
        for item in reversed(photos):
            st.markdown(f"**{item.get('sender','가족')}님이 공유한 사진**")
            if item.get("image_url"):
                st.image(item["image_url"], use_container_width=True)
            elif item.get("image_bytes"):
                st.image(item["image_bytes"], use_container_width=True)
            if item.get("content"):
                st.caption(item["content"])

# ---------- 연결 안내 ----------
elif st.session_state.page == "setup":
    page_title("🔧", "가족끼리 실제로 연결하기", "다른 휴대폰에서도 대화와 사진을 함께 보려면 처음 한 번만 설정해 주세요.")
    st.markdown("""
    <div class='info-card'>
    <b>준비할 것</b><br>
    1. 무료 Supabase 계정<br>
    2. Supabase 프로젝트 1개<br>
    3. 프로젝트 주소와 anon key
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 1. Supabase에 표와 사진 저장 공간 만들기")
    sql = """create table if not exists public.family_messages (
  id bigint generated by default as identity primary key,
  room_code text not null,
  sender text not null,
  kind text not null default 'text',
  content text default '',
  image_url text default '',
  created_at timestamptz not null default now()
);

alter table public.family_messages enable row level security;

create policy "family messages can be read"
on public.family_messages for select to anon using (true);

create policy "family messages can be added"
on public.family_messages for insert to anon with check (true);

insert into storage.buckets (id, name, public)
values ('family-photos', 'family-photos', true)
on conflict (id) do nothing;

create policy "family photos can be uploaded"
on storage.objects for insert to anon
with check (bucket_id = 'family-photos');

create policy "family photos can be viewed"
on storage.objects for select to anon
using (bucket_id = 'family-photos');"""
    st.code(sql, language="sql")
    st.caption("Supabase의 SQL Editor에 위 내용을 붙여 넣고 실행하세요.")
    st.markdown("### 2. Streamlit에 연결 정보 넣기")
    st.markdown("GitHub에 앱을 올린 뒤 Streamlit의 앱 설정에서 **Secrets**에 아래 내용을 입력하세요.")
    st.code('SUPABASE_URL = "https://프로젝트주소.supabase.co"\nSUPABASE_ANON_KEY = "프로젝트의 anon key"', language="toml")
    st.warning("이 예시는 가족용 시제품입니다. 사진 저장 공간은 공개 읽기 방식이므로 민감한 사진이나 개인정보를 올리지 마세요. 실제 서비스로 공개하기 전에는 가족별 로그인과 비공개 권한 설정을 추가해야 합니다.")
    st.markdown("### 3. 앱 실행")
    st.code("pip install -r requirements.txt\nstreamlit run app.py", language="bash")

# ---------- 하단 ----------
st.divider()
f1, f2 = st.columns(2)
with f1:
    if st.button("🔧 가족 연결 안내", key="setup_bottom"):
        go("setup")
with f2:
    if st.button("🏡 메인 화면", key="home_bottom"):
        go("home")
st.markdown("<p class='small-note' style='text-align:center'>우리家 · 천천히 배워도 괜찮아요 🌿</p>", unsafe_allow_html=True)
