import streamlit as st
import asyncio
from openai import AsyncOpenAI
import time, os
from dotenv import load_dotenv
from time import time

load_dotenv()

class LLMResponse:
    """
    LLM_Response class, define the llm client
    """
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=os.getenv("BASE_URL"), # LLM server url. if you use OpenAI API, you can leave it blank.
            api_key=os.getenv("API_KEY") # LLM server api key
        )
        
    async def model_completion(self, model_name, system_prompt, human_prompt, temperature, max_tokens=300):
        start_time = time()
        response = await self.client.chat.completions.create(
            model = model_name,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": human_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        get_response = response.choices[0].message.content.strip().lower()
        end_time = time()
        inference_time = round(end_time - start_time, 2)
        return get_response, inference_time


class PromptTester:
    """
    Prompt_Tester class, define the UI
    """
    def __init__(self):
        st.set_page_config(
            layout="wide",
            page_title="Prompt Tester",
            initial_sidebar_state="expanded"
        )
        #css 정의
        st.markdown("""
        <style>
        .css-1d391kg {
            padding: 0.5rem 1rem;
        }
        
        .stTextArea textarea {
            width: 100% !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.title("Prompt Comparing Tester")

        if 'system_prompt_saved' not in st.session_state:
            st.session_state['system_prompt_saved'] = ""
        if 'human_prompt_saved' not in st.session_state:
            st.session_state['human_prompt_saved'] = ""
        if 'system_prompt1_saved' not in st.session_state:
            st.session_state['system_prompt1_saved'] = ""
        if 'human_prompt1_saved' not in st.session_state:
            st.session_state['human_prompt1_saved'] = ""
        if 'system_prompt2_saved' not in st.session_state:
            st.session_state['system_prompt2_saved'] = ""
        if 'human_prompt2_saved' not in st.session_state:
            st.session_state['human_prompt2_saved'] = ""
        
        if 'compare_prompts' not in st.session_state:
            st.session_state['compare_prompts'] = False
        
        with st.sidebar:
            button_col1, button_col2 = st.columns([1, 1])
            
            with button_col1:
                def toggle_compare():
                    st.session_state['compare_prompts'] = not st.session_state['compare_prompts']
                st.button("Add Prompt", on_click=toggle_compare)
            with button_col2:   
                def clear_state():
                    st.session_state['compare_prompts'] = False
                st.button("Clear", on_click=clear_state)
            st.header("Prompt Settings")
            self.model_name = st.text_input("Model Name", value="./Qwen2.5-32B-Instruct-AWQ")
            
            st.header("")
            st.subheader("Execute Repetations")
            self.num_tests = st.slider("Repetations", min_value=1, max_value=10, value=1)
            self.temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.56, step=0.1)
            self.max_tokens = st.number_input("Max Tokens", min_value=100, max_value=1000, value=300, step=10)
            
    def main(self):

        if st.session_state['compare_prompts']:
            
            with st.sidebar :
                st.header("")
                st.subheader("Comparing Prompt Models")
                prompt1_model = st.text_input("Prompt1 Model name",  value="./Qwen2.5-32B-Instruct-AWQ")
                prompt2_model = st.text_input("Prompt2 Model name",  value="./Qwen2.5-32B-Instruct-AWQ")
            
            print(st.session_state)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Prompt Set 1**")
                system_prompt1 = st.text_area(
                    "SYSTEM 1",
                    value=st.session_state.system_prompt1_saved or st.session_state.system_prompt_saved,
                    height=68,
                    placeholder="Write the System Prompt...",
                    key="system_prompt1"
                )
                st.session_state.system_prompt1_saved = system_prompt1
                
                human_prompt1 = st.text_area(
                    "HUMAN 1",
                    value=st.session_state.human_prompt1_saved or st.session_state.human_prompt_saved,
                    height=300,
                    placeholder="Write the Human Prompt...",
                    key="human_prompt1"
                )
                st.session_state.human_prompt1_saved = human_prompt1
                
            with col2:
                st.markdown("**Prompt Set 2**")
                system_prompt2 = st.text_area(
                    "SYSTEM 2",
                    value=st.session_state.system_prompt2_saved or st.session_state.system_prompt_saved,
                    height=68,
                    placeholder="Write the System Prompt...",
                    key="system_prompt2"
                )
                st.session_state.system_prompt2_saved = system_prompt2
                human_prompt2 = st.text_area(
                    "HUMAN 2",
                    value=st.session_state.human_prompt2_saved or st.session_state.human_prompt_saved,  # 저장된 값 사용
                    height=300,
                    placeholder="Write the Human Prompt...",
                    key="human_prompt2"
                )
                st.session_state.human_prompt2_saved = human_prompt2
                
            if st.button("테스트 실행", key="run_test_double"):
                if not (system_prompt1 and human_prompt1) or not (system_prompt2 and human_prompt2):
                    st.warning("프롬프트를 모두 입력해주세요.")
                    return
                    
                # 결과 표시 섹션
                st.header("Model Responses")
                
                for i in range(self.num_tests):
                    col1, col2 = st.columns(2)
                    llm_response = LLMResponse()
                    
                    async def run_completions():
                        tasks = [
                            llm_response.model_completion(prompt1_model, system_prompt1, human_prompt1, self.temperature, self.max_tokens),   
                            llm_response.model_completion(prompt2_model, system_prompt2, human_prompt2, self.temperature, self.max_tokens)
                        ]
                        return await asyncio.gather(*tasks)
                    
                    results = asyncio.run(run_completions())
                    get_response1, inference_time1 = results[0]
                    get_response2, inference_time2 = results[1]
                    
                    with col1:
                        with st.expander(f"Prompt 1 #{i+1}", expanded=True):
                            st.markdown("**😊 Model Output:**")
                            st.write(get_response1)
                            st.write("-"*100)
                            st.markdown("**🕒 Inference Time:**")
                            st.write(inference_time1)
                                
                    with col2:
                        with st.expander(f"Prompt 2 #{i+1}", expanded=True):
                            st.markdown("**😊 Model Output:**")
                            st.write(get_response2)
                            st.write("-"*100)
                            st.markdown("**🕒 Inference Time:**")
                            st.write(inference_time2)

        else:
            # 기존의 단일 프롬프트 입력 UI
            system_prompt = st.text_area(
                "SYSTEM",
                height=68,
                placeholder="Write the System Prompt...",
                key="system_prompt"
            )
            
            human_prompt = st.text_area(
                "HUMAN(USER)",
                height=300,
                placeholder="Write the Human Prompt...",
                key="human_prompt"
            )
            
            # 입력값을 세션 상태에 저장
            st.session_state.system_prompt_saved = system_prompt
            st.session_state.human_prompt_saved = human_prompt
            
            if st.button("테스트 실행", key="run_test_single"):
                if not system_prompt or not human_prompt:
                    st.warning("프롬프트를 모두 입력해주세요.")
                    return
                    
                st.markdown("### Model Response")
                
                for i in range(self.num_tests):
                    with st.expander(f"✏ 테스트 #{i+1}", expanded=True):
                        llm_response = LLMResponse()
                        
                        async def run_completion():
                            return await llm_response.model_completion(
                                self.model_name, 
                                system_prompt, 
                                human_prompt, 
                                self.temperature, 
                                self.max_tokens
                            )
                        
                        get_response, inference_time = asyncio.run(run_completion())
                        st.markdown("**😊 Model Output:**")
                        st.write(get_response)
                        st.write("-"*100)
                        st.markdown("**🕒 Inference Time:**")
                        st.write(inference_time)
                                         
if __name__ == "__main__":
    prompt_tester = PromptTester()
    prompt_tester.main()