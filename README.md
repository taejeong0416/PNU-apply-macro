# PNU Apply Macro

<br>
부산대학교 수강신청 자동화 매크로입니다.  
설정된 시간에 로그인하고 희망과목담기 한 과목의 수강신청 버튼을 클릭합니다.
<br><br>

'macro.py' 파일에서 아래 항목 수정
- 수강신청 시작 시간 ('apply_day_str')
- 아이디 / 비밀번호 ('send_keys("ID")', 'send_keys("PWD")')
<br>

필요한 라이브러리 설치
```bash
pip install selenium webdriver-manager

