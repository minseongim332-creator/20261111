"""Additional functional pages for APP잘알. All simulator actions remain in memory."""
import json
import html
import streamlit as st
import streamlit.components.v1 as components
from courseware import CATEGORIES,EXTRA,quizzes_for
import services

NEW_KO={'practice':'가상 스마트폰 연습','quiz':'학습 퀴즈','assistant':'질문 도우미','account':'마이페이지',
'practice_hint':'문자와 전화를 안전하게 연습해요','quiz_hint':'배운 내용을 가볍게 확인해요','assistant_hint':'학습 자료에서 답을 찾아봐요','account_hint':'로그인과 내 정보 관리',
'category':'학습 분야','favorite':'즐겨찾기','favorites':'즐겨찾는 학습','speak':'음성 안내','speak_note':'한국어 학습을 브라우저 음성으로 읽어요. 기기에 한국어 음성이 없으면 읽기가 제한될 수 있어요.',
'quiz_ko':'퀴즈와 가상 연습의 학습 문장은 현재 한국어로 제공됩니다.','sync_failed':'학습 기록을 서버에 저장하지 못했어요. 연결을 확인하고 CSV로도 백업해 주세요.',
'demo':'체험 모드','bottom_home':'홈','bottom_learn':'배우기','bottom_practice':'연습','bottom_record':'기록'}
NEW_EN={'practice':'Practice on a virtual phone','quiz':'Learning quiz','assistant':'Question helper','account':'My account',
'practice_hint':'Practice calls and messages safely','quiz_hint':'Check what you have learned','assistant_hint':'Find answers in the lessons','account_hint':'Sign in and manage your profile',
'category':'Learning category','favorite':'Favorite','favorites':'Favorite lessons','speak':'Voice guidance','speak_note':'Read Korean lessons using your browser voice. A Korean voice may not be available on every device.',
'quiz_ko':'Quiz and simulator learning text is currently available in Korean.','sync_failed':'Could not save your learning records online. Check your connection and download a CSV backup.',
'demo':'Demo mode','bottom_home':'Home','bottom_learn':'Learn','bottom_practice':'Practice','bottom_record':'History'}

def voice(text):
    enabled=st.toggle('음성 안내 켜기 · Voice',key='voice_enabled')
    if not enabled:return
    st.caption('기기 기본 음성 기능을 사용해요. 브라우저나 기기 설정에 따라 한국어 음성이 없을 수 있어요.')
    safe=json.dumps(text,ensure_ascii=True).replace('<','\\u003c')
    # Native browser speech; it may use platform-provided online voices. No paid TTS key.
    components.html('''<div style="display:flex;gap:12px"><button id="read">▶ 읽어주기 · 다시 듣기</button><button id="stop">■ 멈추기</button></div><p id="status" aria-live="polite"></p><style>button{font-size:20px;padding:14px;border:1px solid #8aa4bc;border-radius:12px;background:#e9f2fa;color:#26364a;cursor:pointer}p{font:16px sans-serif}</style><script>
const text='''+safe+'''; const status=document.getElementById('status');
if(!('speechSynthesis' in window)){status.textContent='이 브라우저는 음성 읽기를 지원하지 않아요.';document.getElementById('read').disabled=true;}
document.getElementById('read').onclick=()=>{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.lang='ko-KR';u.rate=.85;u.onerror=()=>{status.textContent='음성을 읽을 수 없어요. 기기 음성 설정을 확인해 주세요.'};speechSynthesis.speak(u);};
document.getElementById('stop').onclick=()=>speechSynthesis.cancel();window.addEventListener('pagehide',()=>speechSynthesis.cancel());
</script>''',height=150)

def account():
    st.title('마이페이지')
    st.subheader('지금까지 배운 내용')
    st.write(str(len(st.session_state.get('completed',{})))+'개 학습을 마쳤어요.')
    st.write('즐겨찾기 '+str(len(st.session_state.get('favorites',[])))+'개')
    a,b=st.columns(2)
    if a.button('배운 내용과 즐겨찾기 보기'):
        st.session_state.page='record';st.rerun()
    if b.button('글씨와 음성 설정'):
        st.session_state.page='settings';st.rerun()
    if st.session_state.get('account'):
        st.success('로그인 중: '+st.session_state.account['email'])
        name=st.text_input('부를 이름',value=st.session_state.get('profile_name',''),max_chars=30)
        if st.button('내 정보 저장'):
            st.session_state.profile_name=name
            try:services.save_progress();st.success('저장했어요.')
            except Exception:st.error('서버 저장에 실패했어요. 다시 시도해 주세요.')
        if st.button('로그아웃'):
            services.logout();st.rerun()
        return
    if not services.configured():
        st.info('현재는 체험 모드입니다. 계정 저장은 Supabase를 연결하면 사용할 수 있어요. 설정 방법은 README.md에 있어요. 학습·연습·CSV 백업은 지금 사용할 수 있어요.')
        if st.button('체험 시작하기',type='primary'):
            st.session_state.guest=True;st.session_state.page='home';st.rerun()
        return
    mode=st.radio('원하는 작업',['로그인','회원가입','비밀번호 찾기'],horizontal=True)
    st.caption('안전한 인증을 위해 아이디로 이메일을 사용해요. 비밀번호는 이 앱에 따로 저장하지 않고 Supabase 인증으로 처리해요.')
    with st.form('authentication'):
        email=st.text_input('아이디 · 이메일',max_chars=254)
        password=st.text_input('비밀번호 · Password',type='password',max_chars=128) if mode!='비밀번호 찾기' else ''
        confirm=st.text_input('비밀번호 확인',type='password') if mode=='회원가입' else password
        send=st.form_submit_button(mode,use_container_width=True)
    if send:
        if '@' not in email or (mode=='회원가입' and (len(password)<10 or password!=confirm)):
            st.error('이메일과 비밀번호를 확인해 주세요. 가입 비밀번호는 10자 이상이며 확인란과 같아야 해요.');return
        try:
            db=services.client()
            if mode=='비밀번호 찾기':
                db.auth.reset_password_email(email);st.session_state.recovery_email=email
                st.success('등록된 주소라면 복구 메일이 발송됩니다. 메일의 복구 코드를 아래에 입력하세요. 이메일 템플릿 설정은 배포 안내를 참고하세요.')
            elif mode=='회원가입':
                db.auth.sign_up({'email':email,'password':password});st.success('확인 메일을 보냈어요. 이메일 인증 후 로그인해 주세요.')
            else:
                result=db.auth.sign_in_with_password({'email':email,'password':password})
                if not result.user or not result.session:raise ValueError('no session')
                for key in ['completed','steps','quiz_scores']:st.session_state[key]={}
                st.session_state.favorites=[];st.session_state.profile_name='';st.session_state.lesson='install'
                st.session_state.messages=[]
                st.session_state.account={'id':str(result.user.id),'email':result.user.email}
                try:services.load_progress()
                except Exception:st.session_state['_load_warning']=True
                st.session_state.page='home';st.rerun()
        except Exception:st.error('처리하지 못했어요. 입력 정보와 인증 메일, 네트워크를 확인해 주세요. 잠시 뒤 다시 시도할 수 있어요.')
    if mode=='비밀번호 찾기':
        with st.form('recovery'):
            target=st.text_input('복구 이메일',value=st.session_state.get('recovery_email',''))
            code=st.text_input('메일에서 받은 복구 코드',max_chars=20)
            new=st.text_input('새 비밀번호 (10자 이상)',type='password')
            new2=st.text_input('새 비밀번호 확인',type='password')
            apply=st.form_submit_button('비밀번호 다시 설정')
        if apply:
            if len(new)<10 or new!=new2:st.error('새 비밀번호와 확인란을 확인해 주세요.')
            else:
                try:
                    db=services.client();db.auth.verify_otp({'email':target,'token':code,'type':'recovery'})
                    db.auth.update_user({'password':new});db.auth.sign_out()
                    st.success('비밀번호를 바꿨어요. 새 비밀번호로 로그인해 주세요.')
                except Exception:st.error('복구 코드가 올바르지 않거나 만료되었어요. 새 코드를 요청해 주세요.')
    if st.button('로그인 없이 체험하기'):
        st.session_state.guest=True;st.session_state.page='home';st.rerun()

def practice():
    st.title('직접 연습해 보기')
    if st.button('연습 내용 지우고 다시 하기'):
        for key in list(st.session_state.keys()):
            if key.startswith('sim_'):del st.session_state[key]
        st.rerun()
    st.info('안전한 모의 체험입니다. 실제 전화·문자·송금·예약은 발생하지 않아요. 실제 개인정보 대신 가상의 이름과 번호만 입력하세요.')
    mode=st.selectbox('연습할 기능',['문자와 사진','연락처','전화','가상 앱 화면','송금·결제 확인'])
    with st.container(border=True):
        st.caption('APP잘알 · 연습용 휴대폰')
        if mode=='문자와 사진':
            with st.form('sim_message',clear_on_submit=True):
                number=st.text_input('받는 사람 (가상 이름)',placeholder='예: 연습 친구')
                text=st.text_area('보낼 말',max_chars=500)
                photo=st.selectbox('연습용 사진 첨부',['사진 없음','🌷 꽃 사진','🌊 바다 사진','🍎 사과 사진'])
                send=st.form_submit_button('가상 문자 보내기')
            if send:
                if not number.strip() or not text.strip():st.error('받는 사람과 내용을 적어 주세요.')
                else:
                    st.session_state.setdefault('sim_messages',[]).append({'name':number,'text':text,'photo':photo})
                    st.success('연습 성공! 실제로 보내지 않았어요.')
            for m in st.session_state.get('sim_messages',[])[-5:]:
                st.text(m['name']+' ← '+m['text']+' '+m['photo'])
        elif mode=='연락처':
            with st.form('sim_contact'):
                name=st.text_input('가상 이름');number=st.text_input('가상 전화번호',value='010-0000-0000')
                save=st.form_submit_button('연습 연락처 저장')
            if save:
                if name.strip():st.session_state.setdefault('sim_contacts',{})[name]=number;st.success('연습용 연락처에 저장했어요.')
                else:st.error('이름을 적어 주세요.')
            for name,number in st.session_state.get('sim_contacts',{}).items():
                a,b=st.columns([3,1]);a.text(name+' · '+number)
                if b.button('삭제',key='contact_'+name):del st.session_state.sim_contacts[name];st.rerun()
        elif mode=='전화':
            number=st.text_input('연습 번호',value='010-0000-0000')
            a,b=st.columns(2)
            if a.button('☎ 가상 전화 걸기'):
                st.session_state.sim_call=True
            if b.button('통화 끝내기'):st.session_state.sim_call=False
            if st.session_state.get('sim_call'):st.success('가상 통화 중입니다. 실제 전화는 연결되지 않았어요.')
            else:st.write('통화가 끝난 상태예요.')
        elif mode=='가상 앱 화면':
            for title,target in [('⚙ 설정','settings'),('✉ 문자','messages'),('▧ 사진','gallery')]:
                if st.button(title,key='fake_'+target):st.session_state.sim_screen=target
            screen=st.session_state.get('sim_screen','settings')
            if screen=='settings':
                st.slider('연습 화면 밝기',10,100,70);st.slider('연습 글자 크기',16,32,22)
                st.caption('연습용 조절값이며 실제 기기 설정은 바뀌지 않아요.')
            elif screen=='messages':st.info('문자와 사진 연습 메뉴에서 작성해 볼 수 있어요.')
            else:st.write('🌷   🌊   🍎\n연습용 사진 목록이에요.')
        else:
            st.write('가상 받는 사람: 연습 친구 · 연습은행 · 000-0000')
            amount=st.number_input('연습 금액',min_value=1000,max_value=1000000,value=10000,step=1000)
            confirm=st.checkbox('받는 사람과 금액을 확인했어요')
            if st.button('가상 확인 완료',disabled=not confirm):st.success(f'{amount:,}원 확인 연습을 마쳤어요. 돈은 이동하지 않았어요.')

def quiz():
    st.title('학습 퀴즈')
    category=st.selectbox('분야 선택',CATEGORIES[1:])
    questions=quizzes_for(category)
    index=st.session_state.get('quiz_index_'+category,0)%len(questions)
    key,q=questions[index]
    st.caption(f'{index+1} / {len(questions)} · 실제 서비스 화면과는 다를 수 있어요.')
    st.subheader(q['question'])
    answer=st.radio('답을 골라 주세요',q['options'],index=None,key='answer_'+key)
    if st.button('정답 확인',disabled=answer is None):
        correct=q['options'].index(answer)==q['answer']
        old=st.session_state.quiz_scores.get(key,{'attempts':0,'correct':False})
        st.session_state.quiz_scores[key]={'attempts':old['attempts']+1,'correct':correct}
        st.session_state['feedback_'+key]=correct
    if 'feedback_'+key in st.session_state:
        correct=st.session_state['feedback_'+key]
        (st.success if correct else st.warning)(('정답이에요! ' if correct else '다시 생각해 보세요. ')+q['feedback'])
        if not correct:st.caption('답을 바꾸고 정답 확인을 다시 눌러 보세요.')
    if st.button('다음 문제'):
        st.session_state['quiz_index_'+category]=index+1;st.rerun()
    scores=st.session_state.quiz_scores
    st.write(f'현재 맞힌 문제: {sum(bool(v.get("correct")) for v in scores.values())} / {len(EXTRA)}')
    if st.button('틀린 문제 다시 풀기'):
        wrong=next((i for i,(k,_) in enumerate(questions) if k in scores and not scores[k]['correct']),None)
        if wrong is None:st.info('이 분야에 기록된 오답이 없어요.')
        else:
            wrongkey=questions[wrong][0]
            st.session_state['quiz_index_'+category]=wrong
            st.session_state.pop('answer_'+wrongkey,None);st.session_state.pop('feedback_'+wrongkey,None);st.rerun()

def assistant(lessons):
    st.title('질문 도우미')
    st.info('기본 모드는 학습 자료 검색 안내입니다. 생성형 AI가 답변한 것처럼 표시하지 않아요. 비밀번호·인증번호·개인정보는 적지 마세요.')
    faq=st.selectbox('자주 묻는 질문',['직접 질문하기','사진을 문자로 보내고 싶어요','와이파이가 연결되지 않아요','카카오톡 친구를 추가하고 싶어요'])
    question=st.text_input('궁금한 점을 적어 주세요',value='' if faq=='직접 질문하기' else faq,placeholder='예: 사진을 문자로 보내고 싶어요',max_chars=1000)
    use_ai=st.checkbox('외부 AI 사용 (관리자가 연결한 경우)',disabled=not bool(services.setting('AI_CHAT_URL') and services.setting('AI_API_KEY') and services.setting('AI_MODEL')))
    if use_ai:st.warning('질문과 관련 학습 자료가 설정된 외부 AI 제공자에게 전송됩니다. 제공자 요금이 발생할 수 있어요. AI 답변은 틀릴 수 있어요.')
    more=st.checkbox('더 자세히, 한 단계씩 설명해 주세요')
    if st.button('도움 찾기',disabled=not question.strip()):
        tokens=question.replace('?','').split()
        ranked=sorted(lessons,key=lambda k:sum(token in ' '.join([lessons[k][0],lessons[k][1]]+lessons[k][2]) for token in tokens),reverse=True)
        # Korean topics often occur with postpositions; add stable topic keywords.
        topics={'문자':'sms','사진':'sms','와이파이':'wifi','로그인':'login','가입':'signup','카카오':'kakao','전화':'calls','연락처':'contacts','스미싱':'smishing','링크':'links','블루투스':'bluetooth'}
        matches=[v for k,v in topics.items() if k in question and v in lessons]
        selected=list(dict.fromkeys(matches+ranked[:2]))[:3]
        context='\n'.join(lessons[k][0]+': '+' '.join(lessons[k][2]) for k in selected)
        if use_ai:
            try:st.write(services.ai_answer(question+(' 아주 쉬운 말로 단계를 나누고 자세히 설명해 주세요.' if more else ''),context));st.caption('외부 AI 생성 답변 · 금융·신원 관련 안내는 공식 경로에서도 확인하세요.')
            except Exception:st.error('AI 연결에 실패했어요. 아래 학습 자료를 대신 확인해 주세요.')
        if not use_ai:st.caption('학습 자료에서 찾은 관련 안내 · 정확히 일치하는 답이 아닐 수도 있어요.')
        for key in selected:
            title,desc,steps=lessons[key]
            with st.expander(title,expanded=True):
                st.write(desc)
                for index,step in enumerate(steps,1):st.write(f'{index}. {step}')
                if st.button('이 학습 열기',key='help_'+key):st.session_state.lesson=key;st.session_state.page='learn';st.rerun()
        st.caption('자료로 해결되지 않으면 사진 도움에서 개인정보를 가린 화면을 가족에게 전달해 보세요.')
