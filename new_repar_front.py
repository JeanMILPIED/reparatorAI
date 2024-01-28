import streamlit as st
import random
import time

st.title("ReparatorAI bot")

def bot_style(theResponse):
    # Simulate stream of response with milliseconds delay
    full_response = ""
    message_placeholder = st.empty()
    for chunk in theResponse.split():
        full_response += chunk + " "
        time.sleep(0.05)
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)

# # # Initialize chat history
# # if "messages" not in st.session_state:
# #     st.session_state.messages = []
# #
# # # Display chat messages from history on app rerun
# # for message in st.session_state.messages:
# #     with st.chat_message(message["role"]):
# #         st.markdown(message["content"])
# #
# # with st.chat_message("assistant"):
# #     assistant_response = random.choice(
# #         [
# #             "Hello there! I am ReparatorAI bot. Let me ask you questions to help you.",
# #             "Hi, human! I am ReparatorAI bot. Let me ask you questions to help you."
# #         ]
# #     )
# #     bot_style(assistant_response)
# # # Add assistant response to chat history
# # st.session_state.messages.append({"role": "assistant", "content": assistant_response})
# #
# # # Accept user input
# # if prompt := st.chat_input(""):
# #     # Add user message to chat history
# #     st.session_state.messages.append({"role": "user", "content": prompt})
# #     # Display user message in chat message container
# #     with st.chat_message("user"):
# #         st.markdown(prompt)
# #     # Add assistant response to chat history
# #     st.session_state.messages.append({"role": "user", "content": prompt})
#
# import streamlit as st
#
# questions_list = ['First - let me ask you What is your machine type',
#                   'Then - please tell me the brand',
#                   'Finally - how old is the broken machine ?',
#                   'Oh this may also hel provide you better results \n What is the suspected failure ?']
# def on_btn_click():
#     del st.session_state['messages']
#
# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#     st.session_state.questions=questions_list
#
# chat_placeholder = st.empty()
# st.button("Clear message", on_click=on_btn_click)
#
# for message in st.session_state.messages:
#     if message["role"]=="user":
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
#
# my_question=st.session_state.questions[0]
# with st.chat_message("assistant"):
#     bot_style(my_question)
#
# if prompt := st.chat_input("Your answer"):
#     #Add assistant response to chat history
#     st.session_state.messages.append({"role": "user", "content": my_question+": "+prompt})
#     #st.text_input("User Response:", on_change=on_input_change, key="user_input")
#     try:
#         questions_list = st.session_state.questions[1:]
#         st.session_state.questions = questions_list
#     except:
#         st.write("no more questions")
#
#
# st.write(st.session_state)
#
# import streamlit as st

# def on_text_input_change():
#     st.session_state.text_input_changed = True
#
#
# def main():
#     st.title("Interactive Questionnaire")
#
#     # Create a session_state to store user responses
#     if 'user_responses' not in st.session_state:
#         st.session_state.user_responses = {}
#
#     # Initialize text_input_changed attribute
#     if 'text_input_changed' not in st.session_state:
#         st.session_state.text_input_changed = False
#
#     # Define your list of questions
#     question_list = [
#         "What is your name?",
#         "How old are you?",
#         "Where do you live?",
#         "What is your favorite color?"
#     ]
#
#     # Ask questions and collect user responses one at a time
#     if 'current_question_index' not in st.session_state:
#         st.session_state.current_question_index = 0
#
#     with st.container():
#         try:
#             st.session_state.text_input_changed = False
#             current_question = question_list[st.session_state.current_question_index]
#             st.write(current_question)
#             user_input = st.text_input("Your Answer:", on_change=on_text_input_change)
#             if st.session_state.text_input_changed==true:
#                 st.session_state.current_question_index += 1
#                 st.session_state.user_responses[st.session_state.current_question_index - 1] = user_input
#
#             st.write(user_input)
#         except:
#             st.success("Thank you for completing the questionnaire!")
#             # Display collected responses
#             st.write("\n\n**User Responses:**")
#             for index, response in st.session_state.user_responses.items():
#                 st.write(f"{index}: {response}")
# st.write(st.session_state)
# if __name__ == "__main__":
#     main()

import streamlit as st
import re

# Predefined list of machines
machines_list_uk = ["coffee maker", "toaster","fridge", "refrigerator", "dishwasher", "washing machine", "blender", "vacuum cleaner", "tablet", "computer"]
brands_list=["nespresso","ikea","philips","apple","samsung","dell"]


def closest_word_with_re(input_word, word_list, min_similarity_threshold=0.5):
    valid_words = [word for word in word_list if re_similarity(input_word, word) >= min_similarity_threshold]

    if not valid_words:
        return ''  # No words meet the minimum similarity threshold

    closest_word = min(valid_words, key=lambda word: re_similarity(input_word, word))
    return closest_word

def re_similarity(word1, word2):
    pattern = re.compile(f"^{re.escape(word1)}$", re.IGNORECASE)
    match = pattern.match(word2)
    return match.span()[1] if match else 0

def extract_numbers(input_string):
    numbers = re.findall(r'\b\d+\b', input_string)
    return [int(number) for number in numbers]

def extract_attributes(text, machines_list=machines_list_uk):

    nums=extract_numbers(text)

    words = text.lower().split()
    # Find the closest matching machine from the predefined list using Jaccard similarity
    closest_match_machine=[closest_word_with_re(input_word, machines_list) for input_word in words]
    closest_match_machine = [the_word for the_word in closest_match_machine if the_word!='']
    # closest_match_machine = max(machines_list, key=lambda machine: len(set(nouns) & set(machine.split())) / len(set(nouns) | set(machine.split())))

    # Find the closest matching machine from the predefined list using Jaccard similarity
    closest_match_brand=[closest_word_with_re(input_word, brands_list) for input_word in words]
    closest_match_brand = [the_word for the_word in closest_match_brand if the_word!='']
    #extract age
    age=[]
    for theNum in nums:
        if len(str(theNum))==4:
            if int(theNum)>1900:
                age.append(2024-int(theNum))
            else:
                pass
        elif len(str(theNum))<=2:
            age.append(int(theNum))
        else:
            pass
    try:
        attributes = {"machine": closest_match_machine[0],
                      "brand": closest_match_brand[0],
                      "age": age[0],
                      "error":False}
    except:
        attributes = {"machine": "",
                      "brand": "",
                      "age":"",
                      "error":True}

    return attributes

def build_response(attributes):
    response="your {} from {} that is {} years old has a problem. Is it correct ?".format(attributes["machine"],attributes["brand"],attributes["age"])
    return response

# Streamlit UI
st.title("Machine Problem Analyzer")

user_input = st.text_input("Tell me all about your problem (machine, brand, age)", "")

if user_input:
    attributes = extract_attributes(user_input)
    if attributes["error"]:
        response="Oups - something went wrong, can you try with a new sentence please ?"
    else:
        response=build_response(attributes)
    with st.chat_message("assistant"):
        bot_style(response)

    if st.button('YES'):
        st.write("yeahh")