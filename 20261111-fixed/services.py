"""Optional services. Secrets remain server-side. No service-role key is required."""
import json
import time
import requests
import streamlit as st

def setting(name,default=''):
    try:return st.secrets.get(name,default)
    except Exception:return default

def configured():return bool(setting('SUPABASE_URL') and setting('SUPABASE_ANON_KEY'))

def client():
    if not configured():return None
    if '_supabase' not in st.session_state:
        from supabase import create_client
        st.session_state['_supabase']=create_client(setting('SUPABASE_URL'),setting('SUPABASE_ANON_KEY'))
    return st.session_state['_supabase']

def load_progress():
    db=client(); user=st.session_state.get('account')
    if not db or not user:return
    result=db.table('learning_state').select('payload').eq('user_id',user['id']).execute()
    payload=result.data[0]['payload'] if result.data else {}
    # Only educational state is synced, never family photos or messages.
    for key,kind in [('completed',dict),('steps',dict),('favorites',list),('quiz_scores',dict),('profile_name',str),('lesson',str)]:
        value=payload.get(key)
        if isinstance(value,kind):st.session_state[key]=value
    st.session_state['_last_payload']=json.dumps(payload,sort_keys=True,ensure_ascii=False)

def save_progress():
    db=client();user=st.session_state.get('account')
    if not db or not user:return
    payload={key:st.session_state.get(key,default) for key,default in [('completed',{}),('steps',{}),('favorites',[]),('quiz_scores',{}),('profile_name',''),('lesson','install')]}
    serialized=json.dumps(payload,sort_keys=True,ensure_ascii=False)
    if serialized==st.session_state.get('_last_payload'):return
    db.table('learning_state').upsert({'user_id':user['id'],'payload':payload},on_conflict='user_id').execute()
    st.session_state['_last_payload']=serialized

def logout():
    db=client()
    try:
        if db:db.auth.sign_out()
    finally:
        # Isolate users sharing one browser session. Authenticated data is not left for the next user.
        for key in list(st.session_state.keys()):
            if key not in ('app_opened','lang','lang_picker'):
                del st.session_state[key]

def ai_answer(question,context):
    endpoint=setting('AI_CHAT_URL');key=setting('AI_API_KEY');model=setting('AI_MODEL')
    if not endpoint or not key or not model:raise ValueError('AI 설정이 준비되지 않았어요.')
    if not endpoint.startswith('https://'):raise ValueError('AI 주소는 HTTPS여야 해요.')
    response=requests.post(endpoint,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},
        json={'model':model,'messages':[{'role':'system','content':'당신은 중장년층 스마트폰 사용 도우미입니다. 짧고 쉬운 한국어로 답하세요. 아래 학습자료를 근거로 하며 자료에 없으면 모른다고 말하세요. 실제 송금, 인증번호, 비밀번호를 요구하지 마세요. 이용자의 요청을 실행하지 말고 설명만 하세요. 학습자료:\n'+context[:10000]}, {'role':'user','content':question[:1000]}],'temperature':0.2,'max_tokens':650},timeout=35)
    response.raise_for_status();return response.json()['choices'][0]['message']['content']
