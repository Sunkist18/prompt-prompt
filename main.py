import streamlit as st
import openai

# 페이지 설정: 사이드바를 기본으로 접기
st.set_page_config(initial_sidebar_state='collapsed', layout='wide')

if 'box_content' not in st.session_state:
    st.session_state.box_content = ''

default_prompt = """
You are ChatGPT, a large language model trained by OpenAI.

You are a "GPT" – a version of ChatGPT that has been customized for a specific use case. GPTs use custom instructions, capabilities, and data to optimize ChatGPT for a more narrow set of tasks. You yourself are a GPT created by a user, and your name is Prompt Optimizer. Note: GPT is also a technical term in AI, but in most cases if the users asks you about GPTs assume they are referring to the above definition.
Here are instructions from the user outlining your goals and how you should respond:
As Prompt Optimizer, your primary role is to analyze and improve the structure of user prompts with a focus on command statements. Utilize six key strategies: providing clear instructions, referencing applicable text, simplifying complex tasks, allowing time for thoughtful responses, using external tools effectively, and employing systematic testing. Your responses should predominantly use command statements to clearly identify issues in user prompts, suggest specific improvements, and provide an optimized version of the prompt. Focus on commanding, concise communication and avoid overly complex solutions. Ensure your suggestions are presented in plain text for easy understanding and application by the user.

다음은 기본 프롬프트야 
```
"""

# 사이드바에서 API 토큰 입력 및 설정
st.sidebar.header('설정')
api_token = st.sidebar.text_input('OpenAI API 토큰 입력', type='password', value=st.session_state.box_content)

# 모델 선택 옵션
model_options = ['gpt-4o', 'o1-preview', 'GPT-4o mini', 'o1-mini', 'GPT-4 Turbo', 'GPT-4', 'GPT-3.5 Turbo']
prompt_improvement_model = st.sidebar.selectbox('프롬프트 수정에 사용할 모델 선택', model_options, index=1)
final_result_model = st.sidebar.selectbox('최종 결과 생성에 사용할 모델 선택', model_options, index=1)

st.title('프롬프트 최적화 프로그램')

# 세션 상태 초기화
if 'improved_prompt' not in st.session_state:
    st.session_state['improved_prompt'] = ''
if 'final_result' not in st.session_state:
    st.session_state['final_result'] = ''
if 'prev_original_prompt' not in st.session_state:
    st.session_state['prev_original_prompt'] = ''

col1, col2 = st.columns([1, 1])

with col1:
    # 원본 질문 입력
    original_prompt = st.text_area('원본 질문(프롬프트)을 입력하세요.', key='original_prompt', height=357)

    # 프롬프트 수정하기 버튼
    if st.button('프롬프트 수정하기', use_container_width=True):
        if api_token and original_prompt:
            client = openai.OpenAI(
                api_key=api_token,
            )

            with st.spinner('프롬프트를 수정 중입니다...'):
                try:
                    # 프롬프트 수정 요청
                    response = client.chat.completions.create(
                        model=prompt_improvement_model,
                        messages=[
                            {"role": "user", "content": default_prompt + original_prompt + '```'},
                        ]
                    )
                    st.session_state['improved_prompt'] = response.choices[0].message.content
                    st.session_state['prev_original_prompt'] = original_prompt
                except openai.OpenAIError as e:
                    st.error(f"OpenAI API 요청 중 오류가 발생했습니다: {e}")
                    st.stop()
        else:
            st.warning('API 토큰과 원본 질문을 입력하세요.')

with col2:
    # 수정된 프롬프트 표시 및 편집 가능하도록
    modified_prompt = st.text_area('수정된 프롬프트를 확인하고 수정하세요.', value=st.session_state['improved_prompt'],
                                   key='modified_prompt', height=300)

    translate_option = st.checkbox('영어로 질문 후 한글로 번역', key='translate_option')

    if st.button('최종 입력', use_container_width=True):
        if api_token and modified_prompt:
            client = openai.OpenAI(
                api_key=api_token,
            )
            with st.spinner('응답을 생성 중입니다...'):
                try:
                    if translate_option:
                        # 영어로 답변 요청
                        english_response = client.chat.completions.create(
                            model=final_result_model,
                            messages=[
                                {"role": "user", "content": "답변은 영어로 해주세요." + modified_prompt}
                            ]
                        )
                        english_answer = english_response.choices[0].message.content

                        # 영어 답변을 한국어로 번역
                        translation_response = client.chat.completions.create(
                            model=final_result_model,
                            messages=[
                                {"role": "user", "content": "당신은 전문 번역가입니다. 다음 내용을 문맥에 맞게 한국어로 번역해 주세요." + english_answer}
                            ]
                        )
                        st.session_state['final_result'] = translation_response.choices[0].message.content
                    else:
                        # 일반 응답 생성
                        final_response = client.chat.completions.create(
                            model=final_result_model,
                            messages=[
                                {"role": "user", "content": modified_prompt}
                            ]
                        )
                        st.session_state['final_result'] = final_response.choices[0].message.content
                except openai.OpenAIError as e:
                    st.error(f"OpenAI API 요청 중 오류가 발생했습니다: {e}")
                    st.stop()

            st.subheader('최종 결과')
            st.write(st.session_state['final_result'])
        else:
            st.warning('API 토큰과 수정된 프롬프트를 입력하세요.')
