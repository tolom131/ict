import os
import time
import streamlit as st

from openai import OpenAI
USE_OPENAI = True
openai_key = ""
os.environ["OPENAI_API_KEY"] = openai_key
temperature = 0.1  # 응답의 창의성 정도 (0~1)
model = "gpt-4o"

st.set_page_config(page_title="Streamlit Chatbot", page_icon="💬", layout="centered")
st.title("💬 Streamlit Chatbot (Minimal)")

with st.sidebar:
    st.subheader("⚙️ 설정")
    system_prompt = st.text_area(
        "Professional Unity Engineer",
        value="You are a helpful unity engineer assistant. Keep answers precisely. Use code examples if applicable. Answer in Korean. Codes must be in C# and available in Unity.",
        height=120,
    )
    
    api_key = st.text_input("OpenAI API Key (옵션)", type="password", help="환경변수 OPENAI_API_KEY로도 설정 가능")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 히스토리 초기화"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        demo_fill = st.checkbox("데모 질문 채우기!!", value=False)

st.caption("09/2024 기준 ICT 교육 예제")

# ---------------------------
# 세션 상태 초기화
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# 메시지 렌더링
# ---------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---------------------------
# OpenAI 호출 함수 (있으면)
# ---------------------------
def call_openai(messages, model_name, temperature_value, sys_prompt, key, url):
    """
    OpenAI Python SDK (>=1.0) 기준.
    환경변수 OPENAI_API_KEY 또는 인자로 받은 key 사용.
    """
    if not key:
        key = os.environ.get("OPENAI_API_KEY", "")

    if not key:
        return None  # 키 없으면 폴백 사용

    # 클라이언트 생성
    client = OpenAI(api_key=key)

    # 시스템 프롬프트 삽입
    _messages = [{"role": "system", "content": sys_prompt}] + messages

    # Chat Completions API 호출
    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=_messages,
            temperature=temperature_value,
            stream=True,  # 스트리밍으로 부드럽게 출력
        )
        return resp
    except Exception as e:
        st.error(f"OpenAI 호출 실패: {e}")
        return None

# ---------------------------
# 폴백 규칙 기반 응답기
# ---------------------------
def fallback_reply(user_text: str) -> str:
    user_text_strip = (user_text or "").strip().lower()
    if not user_text_strip:
        return "무엇을 도와드릴까요?"

    # 아주 간단한 규칙 몇 가지
    if any(k in user_text_strip for k in ["hello", "hi", "안녕", "안녕하세요"]):
        return "안녕하세요! 무엇을 도와드릴까요?"
    if "help" in user_text_strip or "도움" in user_text_strip:
        return "원하시는 기능이나 질문을 구체적으로 알려주시면 간단한 예제나 설명을 드리겠습니다."
    if "streamlit" in user_text_strip:
        return "Streamlit은 파이썬 기반의 대시보드/웹앱 프레임워크입니다. `streamlit run app.py`로 실행합니다."
    # 기본: 짧은 에코
    return f"말씀하신 내용 요약: {user_text[:200]}"


# ---------------------------
# 입력창 (데모 프롬프트)
# ---------------------------
placeholder = "메시지를 입력하세요…"
if demo_fill:
    placeholder = "예) Unity에서 두 오브젝트를 충돌시키는 방법은? (C# 코드 예제 포함)"

user_input = st.chat_input(placeholder)

# ---------------------------
# 입력 처리
# ---------------------------
if user_input:
    # 사용자 메시지 추가/표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 어시스턴트 영역
    with st.chat_message("assistant"):
        # OpenAI 시도
        resp = None
        if USE_OPENAI:
            resp = call_openai(st.session_state.messages, model, temperature, system_prompt, api_key, None)

        if resp is not None:
            # 스트리밍 출력
            full_text = ""
            msg_container = st.empty()
            for chunk in resp:
                delta = chunk.choices[0].delta.content or ""
                full_text += delta
                msg_container.markdown(full_text)
                # 살짝 템포(선택)
                time.sleep(0.005)
        else:
            # 폴백 규칙 기반
            full_text = fallback_reply(user_input)
            st.markdown(full_text)

    # 히스토리에 어시스턴트 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": full_text})