"""앱잘알 — 실행: streamlit run app.py
데이터는 접속 세션에만 유지됩니다. 종료 전 CSV를 내려받으세요.
CSV는 사진을 포함하므로 개인정보를 지우고 믿을 수 있는 가족에게만 전달하세요.
50개 언어 UI는 온라인 자동 번역입니다. 실패 시 한국어임을 명시합니다.
학습 본문은 검수된 한국어만 제공하며 자동 번역하지 않습니다.
원본 코드/참고 이미지가 제공되지 않아 독립적으로 구현한 버전입니다.
"""
import base64
import csv
import html
import io
import json
import uuid
from datetime import datetime, timezone
from PIL import Image, ImageOps
import streamlit as st
from deep_translator import GoogleTranslator

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
'assets':'원본 캐릭터 추가','assets_note':'원본을 제공받지 않아 캐릭터를 임의로 만들지 않았어요. 아래에 원본 이미지를 올리면 현재 접속 동안 홈에 표시됩니다.',
'cream':'크림색 캐릭터 원본','cat':'고양이 캐릭터 원본','font':'글씨 크기','normal':'크게','large':'더 크게',
'auto_note':'UI 문구는 온라인 자동 번역이며 오류가 있을 수 있습니다. 사용자 메시지와 학습 본문은 번역하지 않습니다.',
'no_search':'검색어를 입력하면 관련 한국어 학습을 찾아드려요.','required_photo':'공유할 사진을 먼저 선택해 주세요.',
'updated':'설정을 적용했어요.','all':'전체','finish_note':'완료 기록도 CSV에 함께 저장됩니다.'}
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

@st.cache_data(show_spinner=False, ttl=86400)
def translate_ui(code):
    if code == 'ko':
        return TEXT, True
    try:
        translator = GoogleTranslator(source='ko', target=code)
        # A batch is translated together; any failure reverts the entire UI honestly.
        values = translator.translate_batch(list(TEXT.values()))
        if len(values) != len(TEXT) or any(not isinstance(v,str) or not v.strip() for v in values):
            raise ValueError('Incomplete translation')
        return dict(zip(TEXT, values)), True
    except Exception:
        return TEXT, False


def fresh():
    return {'schema':'appjalal-v1', 'page':'welcome','lang':'ko','messages':[],
            'completed':{},'steps':{},'lesson':'install','big':False,'assets':{}}
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


def export_csv():
    out=io.StringIO(newline='')
    writer=csv.DictWriter(out,fieldnames=['schema','kind','id','payload'])
    writer.writeheader()
    def row(kind, ident, payload):
        # JSON starts with {, so text cannot become spreadsheet formulas.
        writer.writerow(dict(schema='appjalal-v1',kind=kind,id=ident,payload=json.dumps(payload,ensure_ascii=False)))
    for message in S.messages:
        row('message',message['id'],message)
    for lesson, date in S.completed.items():
        row('complete',lesson,{'date':date})
    for lesson, step in S.steps.items():
        row('step',lesson,{'step':step})
    row('preferences','local',{'lang':S.lang,'lesson':S.lesson})
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
            datetime.fromisoformat(data['time'])
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

# Choose language before creating translated widgets. Widget state persists on page changes.
with st.container(key='topbar'):
    brand, lang = st.columns([1.2,1])
    with brand:
        st.markdown('### 📱 앱잘알')
    with lang:
        S.lang=st.selectbox('Language · 언어', [v[0] for v in LANGUAGES],
            index=[v[0] for v in LANGUAGES].index(S.lang),format_func=lambda code:dict(LANGUAGES)[code], key='lang_picker')
with st.spinner('언어 준비 중 · Preparing language…'):
    UI, translated=translate_ui(S.lang)
def t(key): return UI[key]
if not translated:
    st.warning('Translation unavailable. 한국어로 표시 중입니다. 잠시 후 언어를 다시 선택해 주세요.')
rtl=S.lang in ('ar','iw','ur','fa') and translated
size=23 if S.big else 20
st.markdown(f'''<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
:root {{color-scheme:light;}}
.stApp {{background:#FBF8F0;color:#202D49;}}
html,body,[class*="css"],.stApp,button,input,textarea,select {{font-family:'Pretendard',sans-serif!important;}}
.block-container {{max-width:1020px;padding:1.8rem 1.3rem 4rem;}}
h1,h2,h3,p,label {{color:#202D49!important;}}
h1 {{font-size:clamp(32px,5.7vw,52px)!important;font-weight:850!important;letter-spacing:-.045em;line-height:1.25!important;}}
h2 {{font-size:30px!important;font-weight:800!important;}}
p,.stMarkdown li,label,[data-testid="stWidgetLabel"] p {{font-size:{size}px!important;line-height:1.65!important;}}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button {{min-height:64px;border-radius:15px;border:1px solid #CDD3DF;background:#FFFDF8;color:#202D49!important;box-shadow:0 3px 9px #202D4909;padding:14px 20px;transition:transform .15s,box-shadow .15s;}}
.stButton>button p,.stDownloadButton>button p,.stFormSubmitButton>button p {{font-size:{size}px!important;font-weight:750!important;line-height:1.4!important;text-align:center;}}
.stButton>button:hover,.stDownloadButton>button:hover,.stFormSubmitButton>button:hover {{border-color:#647DA3;box-shadow:0 5px 14px #202D4914;transform:translateY(-2px);}}
.stButton>button:active {{transform:translateY(1px);}}
button:focus-visible,input:focus-visible,textarea:focus-visible {{outline:3px solid #426DB0!important;outline-offset:3px;}}
button:disabled {{background:#ECEBE7!important;color:#72757B!important;opacity:.65;box-shadow:none!important;transform:none!important;}}
button[kind="primary"],.stFormSubmitButton>button {{background:#DAE7F8!important;border-color:#B7CBE6!important;}}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea {{font-size:{size}px!important;background:#FFFFFF!important;color:#202D49!important;border-radius:12px;min-height:54px;}}
[data-testid="stSelectbox"] * {{color:#202D49;}}
.st-key-feature_learn button {{background:#DBE8F9!important;}}
.st-key-feature_photo button {{background:#EAE4F4!important;}}
.st-key-feature_chat button {{background:#E1EBDD!important;}}
.st-key-feature_record button {{background:#F2E8D7!important;}}
[class*="st-key-feature_"] button {{min-height:120px;width:100%;border:1px solid #202D4914;}}
[class*="st-key-feature_"] button p {{font-size:{size+2}px!important;font-weight:800!important;}}
.hero {{padding:30px 0 22px;}}
.eyebrow {{font-size:14px!important;font-weight:750;letter-spacing:.12em;color:#657A87!important;}}
.hero-sub {{font-size:clamp(27px,4vw,39px)!important;font-weight:750;line-height:1.35!important;margin:8px 0 18px;letter-spacing:-.04em;}}
.soft-panel {{background:#F2F0E8;border:1px solid #E4E1D7;border-radius:18px;padding:22px;margin:18px 0;}}
[data-testid="stVerticalBlockBorderWrapper"] {{border-radius:18px!important;}}
[data-testid="stHeader"] {{background:transparent;}}
[data-testid="stAppViewContainer"] > .main {{direction:{'rtl' if rtl else 'ltr'};}}
[data-testid="stMainBlockContainer"] {{direction:{'rtl' if rtl else 'ltr'};text-align:{'right' if rtl else 'left'};}}
@media(max-width:600px) {{.block-container {{padding:1rem .85rem 3rem;}} [class*="st-key-feature_"] button {{min-height:112px;padding:10px 6px;}} [class*="st-key-feature_"] button p {{font-size:19px!important;}} .st-key-featuregrid [data-testid="stHorizontalBlock"] {{flex-wrap:nowrap!important;gap:10px;}} .st-key-featuregrid [data-testid="stColumn"] {{min-width:0!important;width:calc(50% - 5px)!important;flex:1 1 0!important;}}}}
</style>''',unsafe_allow_html=True)


def nav():
    with st.container():
        a,b=st.columns(2)
        if a.button('⌂ '+t('home'),use_container_width=True):go('home')
        if b.button('⚙ '+t('settings'),use_container_width=True):go('settings')

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
            st.write('**'+html.escape(item['name'])+'**')
            st.caption(item['time'][:16].replace('T',' ')+' UTC')
            if item['text']: st.text(item['text'])
            if item['image']: st.image(base64.b64decode(item['image']),width=420)

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
                S.messages.append({'id':str(uuid.uuid4()),'name':name.strip(),'text':message.strip(),
                    'time':datetime.now(timezone.utc).isoformat(),'image':image})
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
            # Commit only after the entire file passes validation; local preferences never overwritten.
            merged={m['id']:m for m in messages}
            merged.update({m['id']:m for m in S.messages})
            S.messages=list(merged.values())
            for lesson,date in completed.items():
                S.completed[lesson]=max(date,S.completed.get(lesson,date))
            for lesson,step in steps.items():S.steps[lesson]=max(step,S.steps.get(lesson,0))
            st.success(t('import_ok'))
        except Exception as exc:
            st.error(t('limit') if str(exc)=='limit' else t('invalid'))

if S.page=='welcome':
    st.markdown('<div class="hero"><p class="eyebrow">APPJALAL</p><h1>앱잘알</h1></div>',unsafe_allow_html=True)
    st.write(t('welcome')); st.caption(t('brand')); show_assets()
    if st.button(t('start'),type='primary',use_container_width=True):go('home')
    st.info(t('csv_note'))
    if st.button(t('settings'),use_container_width=True):go('settings')
elif S.page=='home':
    st.markdown(f'<div class="hero"><p class="eyebrow">SMARTPHONE · FAMILY</p><h1>{html.escape(t("title"))}</h1><p class="hero-sub">{html.escape(t("subtitle"))}</p></div>',unsafe_allow_html=True)
    st.write(t('intro')); show_assets()
    query=st.text_input(t('search'),placeholder=t('search_hint'))
    if query.strip():
        matches=[key for key,(title,desc,steps) in LESSONS.items() if query.casefold() in (' '.join([title,desc]+steps)).casefold()]
        st.caption(t('content_note'))
        if not matches:st.info(t('none'))
        for key in matches:
            if st.button(LESSONS[key][0],key='search_'+key,use_container_width=True):S.lesson=key;go('learn')
    with st.container(key='featuregrid'):
        for row in [[('learn','📖'),('photo','📷')],[('chat','💬'),('record','✓')]]:
            columns=st.columns(2,gap='medium')
            for col,(page,icon) in zip(columns,row):
                with col:
                    with st.container(key='feature_'+page):
                        if st.button(icon+'  '+t(page),use_container_width=True):go(page)
    with st.container(border=True):
        progress()
        if st.button(t('continue'),use_container_width=True):go('learn')
    if st.button('⚙ '+t('settings'),use_container_width=True):go('settings')
elif S.page=='learn':
    nav();st.title(t('learn'));st.info(t('content_note'))
    lesson=st.selectbox(t('choose'),list(LESSONS),index=list(LESSONS).index(S.lesson),format_func=lambda k:LESSONS[k][0])
    S.lesson=lesson
    title,desc,steps=LESSONS[lesson]
    step=S.steps.get(lesson,0)
    st.subheader(title);st.write(desc)
    st.progress((step+1)/len(steps));st.caption(f"{t('step')} {step+1} / {len(steps)}")
    with st.container(border=True):st.write(steps[step])
    a,b=st.columns(2)
    if a.button('← '+t('prev'),disabled=step==0,use_container_width=True):S.steps[lesson]=step-1;st.rerun()
    if step<len(steps)-1:
        if b.button(t('next')+' →',type='primary',use_container_width=True):S.steps[lesson]=step+1;st.rerun()
    elif b.button(t('done'),type='primary',use_container_width=True):
        S.completed[lesson]=datetime.now(timezone.utc).isoformat();go('record')
    if st.button(t('reset'),use_container_width=True):S.steps[lesson]=0;st.rerun()
elif S.page=='photo':
    nav();st.title(t('photo'));st.write(t('photo_help'));st.info(t('photo_no_ai'))
    composer(True);st.info(t('csv_note'));backup()
elif S.page=='chat':
    nav();st.title(t('chat'));st.info(t('csv_note'))
    composer();st.subheader(t('recent'));thread();backup()
elif S.page=='record':
    nav();st.title(t('history'));progress();st.caption(t('content_note'))
    if not S.completed:st.info(t('not_started'))
    for key,(title,_,steps) in LESSONS.items():
        with st.container(border=True):
            st.write(('✓ ' if key in S.completed else '○ ')+title)
            st.caption(S.completed[key][:10] if key in S.completed else f"{t('step')} {S.steps.get(key,0)+1} / {len(steps)}")
            if st.button(t('open'),key='history_'+key,use_container_width=True):S.lesson=key;go('learn')
    st.caption(t('finish_note'));backup()
elif S.page=='settings':
    nav();st.title(t('settings'));st.info(t('auto_note'))
    st.write(t('language')+' · '+dict(LANGUAGES)[S.lang])
    big=st.toggle(t('font')+' · '+t('large'),value=S.big)
    if big!=S.big:S.big=big;st.rerun()
    st.subheader(t('assets'));st.caption(t('assets_note'))
    for key in ['cream','cat']:
        asset=st.file_uploader(t(key),type=['png','jpg','jpeg'],key='asset_'+key)
        if asset is not None:
            try:S.assets[key]=encode_image(asset.getvalue())
            except Exception:st.error(t('photo_bad'))
    show_assets();st.subheader(t('data'));backup()
st.divider();st.caption('앱잘알 · '+t('brand'))
