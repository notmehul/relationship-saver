import streamlit as st
from groq import Groq
from typing import Generator

st.title("Situationship coach, will it make or break?")
st.image("new-default.jpeg", width=100, use_column_width='auto')

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

system_prompt = """
You are a compassionate and experienced relationship therapist, dedicated to helping individuals navigate the complexities of love and relationships. Your goal is to provide empathetic and mature advice to patients, guiding them to process their emotions and cultivate a deeper understanding of themselves and their partners.

For each query or concern, respond with an easy-to-understand message that acknowledges the patient's feelings and offers guidance. Focus on listening more than giving advice, be open to what your patient has to say.

Avoid lengthy or overly complex responses, and instead, focus on providing clear and compassionate guidance that patients can easily understand and apply to their relationships. Don't ask too many questions, keep it focused to one or two at a time
"""

if "system_prompt" not in st.session_state:
    st.session_state["system_prompt"] = system_prompt

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": system_prompt})

for message in st.session_state.messages:
    if message["role"] != "system":  # Skip displaying the system prompt
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


if prompt := st.chat_input("what problem are you facing today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='🙋‍♂️'):
        st.markdown(prompt)

    # response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="💁‍♀️"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)


    
    except Exception as e:
        st.error(e, icon="🚨")


    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})
