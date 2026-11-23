import base64
import csv
import html
import io
import json
import os
import uuid
from datetime import datetime, timezone

import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError

# ---------------------------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="폰잘알 · 스마트폰 사용 안내",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# 2. 8개 언어 내장 사전 및 안전한 번역 헬퍼 (t 함수)
# ---------------------------------------------------------
LANGS = ("ko", "en", "vi", "ja", "zh-CN", "th", "tl", "mn")
LANG_NAMES = {
    "ko": "한국어",
    "en": "English",
    "vi": "Tiếng Việt",
    "ja": "日本語",
    "zh-CN": "简体中文",
    "th": "ไทย",
    "tl": "Filipino",
    "mn": "Монгол",
}

WORDS = {
    "brand": (
        "폰잘알 · 스마트폰 사용 안내",
        "Ponjalal · Smartphone Guide",
        "Ponjalal · Hướng dẫn dùng điện thoại",
        "ポンジャラル · スマホ使い方ガイド",
        "智能手机使用指南",
        "คู่มือใช้สมาร์ตโฟน",
        "Gabay sa Smartphone",
        "Ухаалаг утасны гарын авлага",
    ),
    "brand_d": (
        "부모님과 초보자를 위한 쉬운 스마트폰 길잡이",
        "Easy smartphone guide for seniors & beginners",
        "Hướng dẫn điện thoại dễ hiểu cho người mới bắt đầu",
        "シニアと初心者のためのやさしいスマホ案内",
        "适合长辈和初学者的智能手机指南",
        "คู่มือสมาร์ตโฟนเข้าใจง่ายสำหรับผู้เริ่มต้น",
        "Madaling gabay sa smartphone para sa nagsisimula",
        "Эхлэн суралцагчдад зориулсан ухаалаг утасны хөтөч",
    ),
    "home_learning_title": (
        "스마트폰 차근차근 배우기",
        "Learn Smartphone Step by Step",
        "Học điện thoại từng bước",
        "スマホを一歩ずつ学ぶ",
        "一步一步学习智能手机",
        "เรียนรู้สมาร์ตโฟนทีละขั้น",
        "Matuto nang paisa-isa",
        "Ухаалаг утас алхам алхмаар сурах",
    ),
    "home_learning_desc": (
        "전화, 문자, 사진, 카카오톡처럼 필요한 기능을 골라 처음부터 배워요.",
        "Pick essential features like calls, texts, photos, and learn from the start.",
        "Chọn các tính năng cần thiết như gọi điện, nhắn tin, chụp ảnh để học từ đầu.",
        "電話、メッセージ、写真など必要な機能を選んで最初から学びます。",
        "选择电话、短信、照片等需要的功能，从头开始学习。",
        "เลือกฟังก์ชันที่ต้องการ เช่น โทรศัพท์ ข้อความ รูปภาพ แล้วเริ่มเรียน",
        "Pumili ng kailangang feature gaya ng tawag, mensahe, o larawan.",
        "Утасдах, мессеж бичих, зураг авах зэрэг үйлдлээ сонгон сураарай.",
    ),
    "home_open_curriculum": (
        "전체 배우기 과정 보기",
        "View All Lessons",
        "Xem toàn bộ khóa học",
        "すべての学習を見る",
        "查看全部课程",
        "ดูบทเรียนทั้งหมด",
        "Tingnan ang lahat ng aralin",
        "Бүх хичээлийг харах",
    ),
    "mission_title": (
        "오늘의 1분 복습 · 가상 연습",
        "Today's 1-Min Review & Practice",
        "Ôn tập 1 phút & Thực hành",
        "今日の1分復習・練習",
        "今日1分钟复习与练习",
        "ทบทวน 1 นาทีวันนี้",
        "1-Minutong Pagsasanay",
        "Өнөөдрийн 1 минутын давталт",
    ),
    "mission_desc": (
        "실제 요금이나 전송 걱정 없이 가상 휴대폰 화면에서 안전하게 연습해요.",
        "Practice safely on a virtual phone screen without real calls or charges.",
        "Thực hành an toàn trên màn hình ảo mà không lo tốn phí.",
        "実際の通話や課金の心配なく、仮想画面で安全に練習できます。",
        "在虚拟手机屏幕上安全练习，不用担心产生实际费用。",
        "ฝึกฝนอย่างปลอดภัยบนหน้าจอจำลองโดยไม่มีค่าใช้จ่ายจริง",
        "Magsanay nang ligtas sa virtual na screen nang walang bayad.",
        "Бодит төлбөр гарахгүйгээр хиймэл дэлгэц дээр аюулгүй дадлага хийгээрэй.",
    ),
    "btn_mission": (
        "가상 연습 · 퀴즈 시작",
        "Start Practice & Quiz",
        "Bắt đầu thực hành & đố vui",
        "練習・クイズを始める",
        "开始练习与测验",
        "เริ่มฝึกฝนและแบบทดสอบ",
        "Simulan ang Pagsasanay",
        "Дадлага ба сорил эхлүүлэх",
    ),
    "photo_title": (
        "사진으로 물어보기",
        "Ask with a Photo",
        "Hỏi bằng hình ảnh",
        "写真で質問する",
        "拍照提问",
        "ถามด้วยรูปภาพ",
        "Magtanong gamit ang Larawan",
        "Зургаар асуух",
    ),
    "photo_guide": (
        "화면 캡처가 어려우면, 다른 휴대폰으로 화면을 찍어 올려도 돼요.",
        "If taking a screenshot is hard, take a photo of the screen with another phone.",
        "Nếu khó chụp màn hình, hãy dùng điện thoại khác chụp lại rồi tải lên.",
        "スクリーンショットが難しい場合は、別のスマホで画面を撮って載せても大丈夫です。",
        "如果不会截屏，也可以用另一部手机拍下屏幕后上传。",
        "หากจับภาพหน้าจอยาก สามารถใช้โทรศัพท์อีกเครื่องถ่ายรูปหน้าจอแล้วอัปโหลดได้",
        "Kung mahirap mag-screenshot, kuhanan ng litrato ang screen gamit ang ibang telepono.",
        "Дэлгэцийн зураг авахад хэцүү бол өөр утсаар дэлгэцийн зургийг авч оруулж болно.",
    ),
    "nav_home": ("홈", "Home", "Trang chủ", "ホーム", "首页", "หน้าแรก", "Home", "Нүүр"),
    "nav_learn": ("배우기", "Learn", "Học", "学ぶ", "学习", "เรียนรู้", "Matuto", "Сурах"),
    "nav_practice": ("연습", "Practice", "Luyện tập", "練習", "练习", "ฝึกฝน", "Magsanay", "Дадлага"),
    "nav_family": ("가족", "Family", "Gia đình", "家族", "家人", "ครอบครัว", "Pamilya", "Гэр бүл"),
    "nav_record": ("내 기록", "History", "Lịch sử", "記録", "记录", "ประวัติ", "Kasaysayan", "Түүх"),
    "settings_title": (
        "화면 · 글씨 · 음성 설정",
        "Display, Font & Voice Settings",
        "Cài đặt màn hình & giọng nói",
        "画面・文字・音声設定",
        "屏幕、字体与语音设置",
        "การตั้งค่าหน้าจอและเสียง",
        "Mga Setting ng Screen at Boses",
        "Дэлгэц, үсэг, дууны тохиргоо",
    ),
    "privacy_warn": (
        "비밀번호, 인증번호, 주민등록번호, 계좌·카드 번호는 가린 뒤 올려 주세요.",
        "Hide passwords, verification codes, ID numbers, and bank details before sharing.",
        "Che mật khẩu, mã xác minh, số CMND và tài khoản ngân hàng trước khi chia sẻ.",
        "パスワード、認証番号、個人番号、口座情報は隠してから共有してください。",
        "分享前请遮挡密码、验证码、身份证号和银行卡信息。",
        "กรุณาปิดบังรหัสผ่าน รหัสยืนยัน และข้อมูลบัญชีก่อนแชร์",
        "Itago ang password, verification code, at detalye ng bangko bago ibahagi.",
        "Нууц үг, баталгаажуулах код, дансны мэдээллээ нуусны дараа хуваалцаарай.",
    ),
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "ko")
    row = WORDS.get(key)
    if not row:
        return key
    idx = LANGS.index(lang) if lang in LANGS else 0
    return row[idx] if idx < len(row) and row[idx] else row[0]


# ---------------------------------------------------------
# 3. 교육 커리큘럼 및 퀴즈 데이터
# ---------------------------------------------------------
LESSONS = [
    {
        "id": "calls",
        "category": "스마트폰 기본",
        "title": "전화 걸고 받기",
        "desc": "초록색 전화기 버튼으로 안전하게 전화를 걸고 끊어요.",
        "steps": [
            "홈 화면에서 초록색 전화기 모양의 [전화] 앱을 찾아 눌러요.",
            "아래쪽 [키패드]에서 번호를 누르거나 [연락처]에서 이름을 골라요.",
            "번호가 맞는지 다시 확인한 뒤 초록색 통화 버튼을 눌러요.",
            "전화가 오면 화면의 초록색 버튼을 누르거나 밀어서 받고, 끝낼 때는 빨간 버튼을 눌러요.",
        ],
        "quiz_q": "실제 휴대폰에서 통화 버튼을 누르기 전에 가장 먼저 할 일은?",
        "quiz_opts": ["상대방 번호 다시 확인하기", "버튼을 여러 번 연속으로 누르기", "인증번호 알려주기"],
        "quiz_ans": 0,
        "quiz_tip": "통화 버튼을 누르기 전에 번호를 한 번 더 확인하면 잘못 거는 전화를 막을 수 있어요.",
    },
    {
        "id": "sms",
        "category": "스마트폰 기본",
        "title": "문자와 사진 보내기",
        "desc": "안부 문자와 갤러리 사진을 가족에게 보내요.",
        "steps": [
            "[메시지] 또는 [문자] 앱을 열어 오른쪽 아래 [대화 시작]을 눌러요.",
            "받는 사람 칸에 이름이나 전화번호를 입력하고 선택해요.",
            "글자 입력칸에 안부를 적고, 사진은 왼쪽 [+] 또는 사진 아이콘을 눌러 골라요.",
            "받는 사람과 사진에 개인정보가 없는지 확인한 뒤 보내기 화살표를 눌러요.",
        ],
        "quiz_q": "사진을 문자로 보내기 전에 꼭 확인해야 할 것은?",
        "quiz_opts": ["받는 사람과 개인정보 노출 여부", "휴대폰 배터리 색깔", "확인하지 않고 바로 전송"],
        "quiz_ans": 0,
        "quiz_tip": "받는 사람이 맞는지, 사진에 신분증이나 계좌번호가 찍히지 않았는지 먼저 확인해요.",
    },
    {
        "id": "kakao",
        "category": "생활 속 활용",
        "title": "카카오톡 메시지 보내기",
        "desc": "가족·친구에게 인사를 보내고 사칭 메시지를 구별해요.",
        "steps": [
            "노란색 말풍선 모양의 [카카오톡] 앱을 열어요.",
            "아래쪽 [친구] 또는 [채팅] 탭에서 대화할 가족 이름을 찾아요.",
            "이름을 누른 뒤 [1:1 채팅]을 눌러 대화창을 열어요.",
            "아래 입력칸에 글을 적고 노란색 전송 버튼을 눌러요.",
        ],
        "quiz_q": "가족이라며 급하게 돈을 보내 달라는 카톡이 왔다면 어떻게 할까요?",
        "quiz_opts": ["기존에 저장된 전화번호로 직접 전화해 확인한다", "급하니까 바로 송금한다", "신분증 사진을 찍어 보낸다"],
        "quiz_ans": 0,
        "quiz_tip": "가족을 사칭한 문자·카톡일 수 있으므로 반드시 원래 알던 번호로 직접 통화해 확인하세요.",
    },
    {
        "id": "wifi",
        "category": "처음 시작하기",
        "title": "와이파이(Wi-Fi) 연결하기",
        "desc": "집이나 카페에서 데이터 요금 걱정 없이 인터넷을 연결해요.",
        "steps": [
            "톱니바퀴 모양의 [설정] 앱을 열어요.",
            "맨 위쪽 [연결] 또는 [Wi-Fi] 메뉴를 눌러 들어가요.",
            "와이파이 스위치를 켜고 집에서 쓰던 와이파이 이름을 골라요.",
            "비밀번호를 정확히 입력한 뒤 [연결]을 누르고 '연결됨' 글자를 확인해요.",
        ],
        "quiz_q": "공공장소에서 와이파이를 고를 때 가장 안전한 방법은?",
        "quiz_opts": ["안내판에 적힌 공식 와이파이 이름과 비밀번호 확인", "아무 이름이나 비밀번호 없는 것 연결", "모르는 사람이 알려준 링크 누르기"],
        "quiz_ans": 0,
        "quiz_tip": "공식 와이파이 이름을 확인하고 연결해야 안전하게 인터넷을 쓸 수 있어요.",
    },
    {
        "id": "display",
        "category": "처음 시작하기",
        "title": "글자 크기와 화면 밝기 조절",
        "desc": "작은 글씨를 크게 키우고 눈이 편한 밝기로 바꿔요.",
        "steps": [
            "[설정] 앱을 열고 [디스플레이] 또는 [화면 및 밝기]를 눌러요.",
            "밝기 조절 막대를 오른쪽으로 밀어 화면을 환하게 맞춰요.",
            "[글자 크기와 스타일] 또는 [텍스트 크기] 메뉴를 눌러요.",
            "글자 크기 막대를 오른쪽으로 한 칸씩 옮겨 읽기 편한 크기로 맞춘 뒤 홈 버튼을 눌러요.",
        ],
        "quiz_q": "휴대폰 글씨가 너무 작아서 읽기 어려울 때 들어가는 메뉴는?",
        "quiz_opts": ["설정 → 디스플레이(화면) → 글자 크기", "계산기 앱", "시계 알람 설정"],
        "quiz_ans": 0,
        "quiz_tip": "설정의 디스플레이 또는 접근성 메뉴에서 글자 크기를 언제든 키울 수 있어요.",
    },
]

# ---------------------------------------------------------
# 4. 세션 상태 초기화
# ---------------------------------------------------------
defaults = {
    "lang": "ko",
    "page": "home",
    "big_font": True,
    "dark_mode": False,
    "voice_enabled": True,
    "selected_lesson_id": "calls",
    "step_idx": {},
    "completed": {},
    "quiz_scores": {},
    "favorites": [],
    "sim_screen": "home",
    "sim_dial": "",
    "sim_msg_to": "딸 (지영)",
    "sim_msg_body": "",
    "sim_sent_log": [],
    "family_posts": [],
    "show_settings": False,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ---------------------------------------------------------
# 5. 시니어·모바일 친화 고대비 CSS 적용
# ---------------------------------------------------------
def apply_theme():
    dark = st.session_state["dark_mode"]
    big = st.session_state["big_font"]
    bg = "#16221C" if dark else "#F7F4EE"
    surface = "#203128" if dark else "#FFFFFF"
    highlight = "#253A2F" if dark else "#FFF8E9"
    ink = "#F4F7F5" if dark else "#1F2933"
    muted = "#D5E0DA" if dark else "#334155"
    primary = "#2E7D5B" if dark else "#1B4332"
    border = "#3B5447" if dark else "#DFD8C8"
    base_px = "19px" if big else "16px"
    btn_px = "19px" if big else "16px"

    st.markdown(
        f"""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        html, body, [class*="css"] {{
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
            color: {ink};
        }}
        .stApp {{
            background-color: {bg};
        }}
        header[data-testid="stHeader"], footer, #MainMenu {{
            visibility: hidden;
            height: 0;
        }}
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 4.5rem;
            max-width: 640px;
        }}
        p, li, label, .stMarkdown p {{
            font-size: {base_px} !important;
            line-height: 1.6 !important;
            color: {ink};
            word-break: keep-all;
        }}
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {muted} !important;
            font-size: 0.98rem !important;
        }}
        .card-box {{
            background: {surface};
            border: 1.5px solid {border};
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 14px;
        }}
        .hero-box {{
            background: {highlight};
            border: 1.5px solid {border};
            border-radius: 18px;
            padding: 18px;
            margin-bottom: 14px;
        }}
        .stButton > button, .stFormSubmitButton > button {{
            min-height: 54px;
            border-radius: 14px;
            font-size: {btn_px} !important;
            font-weight: 700 !important;
            width: 100%;
            word-break: keep-all;
        }}
        .stButton > button[kind="primary"] {{
            background-color: {primary} !important;
            color: #FFFFFF !important;
            border: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_theme()

# ---------------------------------------------------------
# 6. 보조 유틸리티 (브라우저 음성 읽기, 개념 그림, AI 사진 분석)
# ---------------------------------------------------------
def speak_button(text: str):
    if not st.session_state.get("voice_enabled", True):
        return
    lang = st.session_state.get("lang", "ko")
    payload = json.dumps([text, lang], ensure_ascii=True).replace("<", "\u003c")
    components.html(
        f"""
        <div style="display:flex;gap:8px;align-items:center;margin:4px 0;">
          <button id="playBtn" style="padding:10px 16px;font-size:17px;font-weight:700;
            border-radius:12px;border:1.5px solid #1B4332;background:#E9F5EE;color:#1B4332;cursor:pointer;">
            🔊 설명 소리로 듣기
          </button>
          <button id="stopBtn" style="padding:10px 14px;font-size:17px;font-weight:600;
            border-radius:12px;border:1px solid #CBD5E1;background:#FFFFFF;color:#334155;cursor:pointer;">
            ■ 멈춤
          </button>
          <span id="msg" style="font:14px sans-serif;color:#475569;"></span>
        </div>
        <script>
        const [txt, lang] = {payload};
        const msg = document.getElementById("msg");
        document.getElementById("playBtn").onclick = () => {{
          if (!("speechSynthesis" in window)) {{
            msg.textContent = "이 기기는 음성 읽기를 지원하지 않아요.";
            return;
          }}
          window.speechSynthesis.cancel();
          const u = new SpeechSynthesisUtterance(txt);
          u.lang = lang === "ko" ? "ko-KR" : lang;
          u.rate = 0.9;
          window.speechSynthesis.speak(u);
        }};
        document.getElementById("stopBtn").onclick = () => window.speechSynthesis?.cancel();
        </script>
        """,
        height=62,
    )


def make_step_illustration(step_num: int, total_steps: int) -> bytes:
    im = Image.new("RGB", (640, 260), "#EDF4F0")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((210, 16, 430, 244), radius=26, fill="#FFFFFF", outline="#1B4332", width=5)
    d.rounded_rectangle((285, 28, 355, 34), radius=3, fill="#94A3B8")
    d.ellipse((280, 62, 360, 142), fill="#D8F3DC")
    d.line((302, 102, 316, 116, 342, 88), fill="#1B4332", width=8)
    for i in range(total_steps):
        cx = 245 + i * (150 / max(total_steps - 1, 1))
        color = "#1B4332" if i <= step_num else "#CBD5E1"
        d.ellipse((cx - 7, 195, cx + 7, 209), fill=color)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def analyze_screen_photo(image_bytes: bytes, question: str) -> str:
    api_key = ""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return (
            "현재 AI 자동 사진 분석 키(`OPENAI_API_KEY`)가 설정되지 않아 안내 문구로 대신합니다.\n\n"
            "1. **확인 방법**: 사진 속 화면 맨 위의 제목과 가장 큰 버튼을 먼저 확인해 주세요.\n"
            "2. **가족에게 보내기**: 아래 [가족] 탭에 이 사진과 질문을 저장해 가족에게 보여 줄 수 있어요."
        )

    with Image.open(io.BytesIO(image_bytes)) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((1280, 1280))
        out = io.BytesIO()
        im.save(out, format="JPEG", quality=82)
        b64 = base64.b64encode(out.getvalue()).decode("ascii")

    sys_prompt = (
        "너는 스마트폰 사용이 익숙하지 않은 어르신을 돕는 친절한 길잡이다. "
        "사진 속 화면을 보고 1) 지금 화면 상황 2) 눌러야 할 버튼 위치와 이름 3) 주의할 점을 "
        "쉬운 한국어로 차근차근 설명하라. 비밀번호나 인증번호가 보이면 읽어 주지 말고 가리라고 안내하라."
    )
    user_q = question.strip() or "이 화면에서 다음에 무엇을 눌러야 하나요?"
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": sys_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_q},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                },
            ],
            "max_tokens": 600,
        },
        timeout=25,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


# ---------------------------------------------------------
# 7. 최상단 헤더: 앱 제목 + 🌐 언어 선택 + ⚙️ 화면 설정
# ---------------------------------------------------------
c1, c2, c3 = st.columns([3.5, 3.2, 1.3])
with c1:
    st.markdown(f"### 📱 {t('brand').split('·')[0].strip()}")
with c2:
    chosen_lang = st.selectbox(
        "🌐 Language",
        options=list(LANGS),
        index=LANGS.index(st.session_state["lang"]),
        format_func=lambda code: f"🌐 {LANG_NAMES[code]}",
        label_visibility="collapsed",
        key="top_lang_picker",
    )
    if chosen_lang != st.session_state["lang"]:
        st.session_state["lang"] = chosen_lang
        st.rerun()
with c3:
    if st.button("⚙️", key="btn_toggle_settings", help=t("settings_title")):
        st.session_state["show_settings"] = not st.session_state["show_settings"]
        st.rerun()

if st.session_state["show_settings"]:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown(f"#### ⚙️ {t('settings_title')}")
    s1, s2 = st.columns(2)
    with s1:
        new_big = st.toggle("큰 글씨 모드", value=st.session_state["big_font"], key="toggle_big")
    with s2:
        new_dark = st.toggle("어두운 화면(야간)", value=st.session_state["dark_mode"], key="toggle_dark")
    st.toggle("설명 소리 읽기 버튼 표시", value=st.session_state["voice_enabled"], key="toggle_voice")
    if new_big != st.session_state["big_font"] or new_dark != st.session_state["dark_mode"]:
        st.session_state["big_font"] = new_big
        st.session_state["dark_mode"] = new_dark
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. 화면별 페이지 렌더링
# ---------------------------------------------------------
def render_home():
    st.caption(t("brand_d"))

    # (1) 차근차근 배우기 vs 가상 연습 동선 분리
    st.markdown('<div class="hero-box">', unsafe_allow_html=True)
    st.markdown(f"#### 📘 {t('home_learning_title')}")
    st.write(t("home_learning_desc"))
    if st.button(t("home_open_curriculum"), type="primary", key="go_learn_btn"):
        st.session_state["page"] = "learn"
        st.rerun()

    st.divider()

    st.markdown(f"#### 🎯 {t('mission_title')}")
    st.write(t("mission_desc"))
    if st.button(t("btn_mission"), key="go_practice_btn"):
        st.session_state["page"] = "practice"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # (2) 사진으로 물어보기 (다른 휴대폰 촬영 안내 포함)
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown(f"#### 📸 {t('photo_title')}")
    st.info(f"💡 {t('photo_guide')}")
    st.caption(f"🔒 {t('privacy_warn')}")
    uploaded = st.file_uploader(
        "궁금한 화면 사진 선택 (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        key="home_photo_file",
    )
    q_text = st.text_input(
        "어떤 부분이 궁금하신가요? (선택)",
        placeholder="예: 여기서 다음으로 넘어가려면 어디를 눌러야 하나요?",
        key="home_photo_q",
    )
    if uploaded is not None:
        st.image(uploaded, caption="올린 화면 사진", use_container_width=True)
        if st.button("사진 설명 보기", type="primary", key="btn_analyze_photo"):
            with st.spinner("화면을 꼼꼼히 살펴보고 있어요..."):
                try:
                    ans = analyze_screen_photo(uploaded.getvalue(), q_text)
                    st.success(ans)
                except UnidentifiedImageError:
                    st.error("사진 파일을 읽을 수 없어요. JPG 또는 PNG 사진을 올려 주세요.")
                except Exception:
                    st.error("분석 중 잠시 문제가 생겼어요. 인터넷 연결을 확인하고 다시 눌러 주세요.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_learn():
    st.markdown(f"### 📘 {t('home_learning_title')}")
    st.caption("배울 주제를 고르고 [다음 단계]를 누르며 한 동작씩 따라 해 보세요.")

    titles = {item["id"]: f"[{item['category']}] {item['title']}" for item in LESSONS}
    sel_id = st.selectbox(
        "배울 기능 선택",
        options=[item["id"] for item in LESSONS],
        index=[item["id"] for item in LESSONS].index(st.session_state["selected_lesson_id"]),
        format_func=lambda lid: titles[lid],
        key="lesson_selector",
    )
    st.session_state["selected_lesson_id"] = sel_id
    lesson = next(item for item in LESSONS if item["id"] == sel_id)

    steps = lesson["steps"]
    cur = st.session_state["step_idx"].get(sel_id, 0)
    cur = max(0, min(cur, len(steps) - 1))

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown(f"#### {lesson['title']}")
    st.write(lesson["desc"])
    st.image(make_step_illustration(cur, len(steps)), use_container_width=True)
    st.markdown(f"**{cur + 1}단계 / 전체 {len(steps)}단계**")
    st.info(steps[cur])
    speak_button(f"{cur + 1}단계. {steps[cur]}")

    b1, b2 = st.columns(2)
    with b1:
        if st.button("⬅️ 이전 단계", disabled=(cur == 0), key="btn_prev_step"):
            st.session_state["step_idx"][sel_id] = cur - 1
            st.rerun()
    with b2:
        if cur < len(steps) - 1:
            if st.button("다음 단계 ➡️", type="primary", key="btn_next_step"):
                st.session_state["step_idx"][sel_id] = cur + 1
                st.rerun()
        else:
            if st.button("✅ 학습 완료하기", type="primary", key="btn_done_step"):
                st.session_state["completed"][sel_id] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.balloons()
                st.success("잘하셨어요! 이 과정의 모든 단계를 마쳤어요.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_practice():
    st.markdown(f"### 🎯 {t('mission_title')}")
    st.caption("실제 전화나 문자가 발송되지 않는 안전한 연습 공간입니다.")

    mode = st.radio(
        "연습 방법 선택",
        options=["가상 휴대폰 눌러보기", "배운 내용 확인 퀴즈"],
        horizontal=True,
        key="practice_mode_radio",
    )

    if mode == "가상 휴대폰 눌러보기":
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        sim_tab = st.selectbox(
            "연습할 앱 고르기",
            options=["전화 걸기 연습", "문자 보내기 연습"],
            key="sim_app_select",
        )
        if sim_tab == "전화 걸기 연습":
            st.write("아래 숫자 버튼을 눌러 `010-1234-5678`로 연습 전화를 걸어 보세요.")
            st.text_input("입력된 번호", value=st.session_state["sim_dial"], disabled=True)
            digits = [
                ["1", "2", "3"],
                ["4", "5", "6"],
                ["7", "8", "9"],
                ["*", "0", "#"],
            ]
            for row in digits:
                cols = st.columns(3)
                for idx, d in enumerate(row):
                    if cols[idx].button(d, key=f"dial_{d}"):
                        st.session_state["sim_dial"] += d
                        st.rerun()
            c_call, c_clear = st.columns(2)
            with c_call:
                if st.button("📞 연습 통화 걸기", type="primary", key="sim_call_go"):
                    if st.session_state["sim_dial"]:
                        st.success(f"'{st.session_state['sim_dial']}' 번호로 가상 통화 연결 연습에 성공했어요!")
                    else:
                        st.warning("먼저 숫자 버튼을 눌러 번호를 입력해 주세요.")
            with c_clear:
                if st.button("지우기", key="sim_call_clear"):
                    st.session_state["sim_dial"] = ""
                    st.rerun()
        else:
            to_who = st.text_input("받는 사람", value=st.session_state["sim_msg_to"], key="sim_to_in")
            msg_txt = st.text_input("보낼 인사말", placeholder="예: 오늘 날씨가 참 좋네요.", key="sim_body_in")
            if st.button("✉️ 연습 문자 보내기", type="primary", key="sim_sms_go"):
                if msg_txt.strip():
                    st.session_state["sim_sent_log"].append(f"{to_who}: {msg_txt.strip()}")
                    st.success("가상 문자 전송 연습 완료! 실제 요금은 나가지 않았어요.")
                else:
                    st.warning("보낼 인사말을 한 줄 적어 주세요.")
            if st.session_state["sim_sent_log"]:
                st.caption("방금 연습한 문자 기록:")
                for line in st.session_state["sim_sent_log"][-3:]:
                    st.write(f"• {line}")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        lesson = next(item for item in LESSONS if item["id"] == st.session_state["selected_lesson_id"])
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.markdown(f"#### ❓ {lesson['title']} 확인 문제")
        st.write(lesson["quiz_q"])
        choice = st.radio("정답을 골라 보세요", options=lesson["quiz_opts"], key="quiz_choice_radio")
        if st.button("정답 확인하기", type="primary", key="btn_check_quiz"):
            if lesson["quiz_opts"].index(choice) == lesson["quiz_ans"]:
                st.session_state["quiz_scores"][lesson["id"]] = True
                st.success(f"정답이에요! {lesson['quiz_tip']}")
            else:
                st.warning(f"아쉬워요. 다시 한 번 생각해 볼까요? 힌트: {lesson['quiz_tip']}")
        st.markdown("</div>", unsafe_allow_html=True)


def render_family():
    st.markdown(f"### 👨‍👩‍👧 {t('nav_family')} 공간 · 도움 메모")
    st.caption("궁금한 점이나 막힌 화면을 메모로 남기고, CSV 파일로 내려받아 가족에게 카톡이나 메일로 보낼 수 있어요.")

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    with st.form("family_note_form", clear_on_submit=True):
        sender = st.text_input("보내는 사람 이름", placeholder="예: 엄마 / 아빠")
        note = st.text_area("가족에게 남길 질문이나 안부", placeholder="예: 카카오톡 사진 보내는 법이 헷갈려요.")
        submitted = st.form_submit_button("가족 메모 저장하기", type="primary")
        if submitted:
            if sender.strip() and note.strip():
                st.session_state["family_posts"].append(
                    {
                        "id": str(uuid.uuid4())[:8],
                        "time": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
                        "sender": sender.strip(),
                        "note": note.strip(),
                    }
                )
                st.success("메모를 저장했어요! 아래에서 CSV 파일로 내려받아 가족에게 전달할 수 있어요.")
            else:
                st.warning("이름과 남길 말을 모두 입력해 주세요.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["family_posts"]:
        for post in reversed(st.session_state["family_posts"]):
            st.markdown(
                f"<div class='card-box'><strong>{html.escape(post['sender'])}</strong> "
                f"<span style='font-size:0.85em;color:#64748B;'>({post['time']})</span><br/>"
                f"{html.escape(post['note'])}</div>",
                unsafe_allow_html=True,
            )


def render_record():
    st.markdown(f"### 📊 {t('nav_record')} 및 CSV 백업")
    done_cnt = len(st.session_state["completed"])
    quiz_cnt = sum(1 for v in st.session_state["quiz_scores"].values() if v)

    c1, c2 = st.columns(2)
    c1.metric("완료한 학습", f"{done_cnt} / {len(LESSONS)}개")
    c2.metric("통과한 퀴즈", f"{quiz_cnt} / {len(LESSONS)}개")

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown("#### 학습 완료 내역")
    if not st.session_state["completed"]:
        st.write("아직 완료한 학습이 없어요. [배우기] 탭에서 첫 과정을 마쳐 보세요.")
    else:
        for item in LESSONS:
            if item["id"] in st.session_state["completed"]:
                st.write(f"✅ **{item['title']}** — 완료 시각: {st.session_state['completed'][item['id']]}")
    st.markdown("</div>", unsafe_allow_html=True)

    # CSV 내보내기 / 불러오기
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown("#### 기록 파일(CSV) 저장 및 불러오기")
    st.caption("새로고침하거나 기기를 바꿀 때 기록을 이어가려면 CSV 파일로 저장해 두세요.")

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["type", "key", "value"])
    for k, v in st.session_state["completed"].items():
        writer.writerow(["completed", k, v])
    for post in st.session_state["family_posts"]:
        writer.writerow(["family_post", post["sender"], f"{post['time']}|{post['note']}"])

    st.download_button(
        label="📥 내 학습·가족 기록 CSV 내려받기",
        data=buf.getvalue().encode("utf-8-sig"),
        file_name="ponjalal_records.csv",
        mime="text/csv",
        type="primary",
    )

    up_csv = st.file_uploader("저장해 둔 CSV 파일 불러오기", type=["csv"], key="csv_importer")
    if up_csv is not None:
        try:
            text_data = up_csv.getvalue().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text_data))
            merged = 0
            for row in reader:
                if row.get("type") == "completed" and row.get("key"):
                    st.session_state["completed"][row["key"]] = row.get("value", "")
                    merged += 1
                elif row.get("type") == "family_post" and row.get("key"):
                    raw_val = row.get("value", "")
                    t_str, _, n_str = raw_val.partition("|")
                    st.session_state["family_posts"].append(
                        {"id": str(uuid.uuid4())[:8], "time": t_str, "sender": row["key"], "note": n_str}
                    )
                    merged += 1
            st.success(f"기록 {merged}건을 안전하게 불러왔어요!")
        except Exception:
            st.error("CSV 파일을 읽지 못했어요. 폰잘알에서 내려받은 파일인지 확인해 주세요.")
    st.markdown("</div>", unsafe_allow_html=True)


# 현재 선택된 탭 렌더링
cur_page = st.session_state["page"]
if cur_page == "home":
    render_home()
elif cur_page == "learn":
    render_learn()
elif cur_page == "practice":
    render_practice()
elif cur_page == "family":
    render_family()
elif cur_page == "record":
    render_record()

# ---------------------------------------------------------
# 9. 하단 5개 고정 내비게이션
# ---------------------------------------------------------
st.divider()
nav_specs = [
    ("home", f"🏠 {t('nav_home')}"),
    ("learn", f"📘 {t('nav_learn')}"),
    ("practice", f"🎯 {t('nav_practice')}"),
    ("family", f"👨‍👩‍👧 {t('nav_family')}"),
    ("record", f"📊 {t('nav_record')}"),
]
nav_cols = st.columns(len(nav_specs))
for idx, (p_key, p_label) in enumerate(nav_specs):
    with nav_cols[idx]:
        if st.button(
            p_label,
            key=f"bottom_nav_{p_key}",
            type="primary" if st.session_state["page"] == p_key else "secondary",
        ):
            st.session_state["page"] = p_key
            st.rerun()
