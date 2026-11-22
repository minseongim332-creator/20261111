앱잘알 수정본

1. 압축을 푼 뒤 안의 파일과 폴더 전체를 GitHub 저장소에 올리세요. 기존 app.py만 교체하지 말고 courseware.py, features.py, services.py, design.py, assets 폴더, requirements.txt, .streamlit 폴더도 함께 올려야 합니다.
2. Streamlit Community Cloud에서 기존 앱의 Reboot를 누르거나 앱을 재배포하세요. Main file path는 app.py입니다.
3. Supabase Secrets가 없어도 '로그인 없이 체험하기'로 학습·퀴즈·연습 기능을 사용할 수 있습니다. Supabase가 설정된 경우에는 기존 로그인/학습기록 기능을 사용합니다.
4. 가족 사진/채팅은 현재 실시간 공유가 아닙니다. CSV를 내려받아 가족에게 전달하고, 받은 CSV를 불러오는 방식입니다. 실시간 공유를 구현하려면 Supabase에 별도 가족방/메시지/사진 저장 테이블과 권한 정책을 추가로 설정해야 합니다. 이 수정본은 실시간 공유라고 거짓 안내하지 않습니다.
5. Supabase 키가 있다면 GitHub에 올리지 말고 Streamlit 앱의 Settings > Secrets에만 입력하세요. service_role 키는 사용하지 마세요.

이번 수정: 2.7MB 이상의 이미지/모듈 문자열을 app.py 안에 직접 넣던 구조를 일반 파일로 분리했습니다. 코드 확인과 배포 오류 추적이 쉬워지고, 흰색·차분한 초록색 중심으로 테마를 정리했습니다. 기능은 기존 구조를 최대한 유지했습니다.
