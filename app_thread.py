from agentic_chatbot_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import streamlit as st
import uuid


# This method generates the unique thread ID for the new conversation
def generate_thread_id():
    return str(uuid.uuid4())



# This methods adds the new thread or conversation in our conversation history
def add_thread(thread_id):
    
    # if the thread id is not present then only add
	if thread_id not in st.session_state["chat_threads"]:
          st.session_state["chat_threads"].append(thread_id)



def reset_chat():

	 # Generate and assign a new thread ID
    st.session_state["thread_id"] = generate_thread_id()

	 # Clear the current chat messages from the UI
    st.session_state["message_history"] = []
    
    # Add the new thread to the conversation list
    add_thread(st.session_state["thread_id"])


def get_messages(thread_id):
    # get the saved state for the selected thread
    state = chatbot.get_state(
        config={
            "configurable": {"thread_id": thread_id}
        }
    )

    return state.values.get("messages", [])


def load_conversation(thread_id:str):


	config = {'configurable' : {'thread_id' : thread_id}}
	state = chatbot.get_state(config)

	return state.values.get("messages",[])

st.title("Agentic ChatBot")

# create condition executes when the application runs for the first time and there will be no message history then it will create that key
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


    
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()
    
    
# create condition executes when the application runs for the first time and there will be no chat threads then it will create that key
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []


add_thread(st.session_state['thread_id'])

# ======================== sidebar converation history ===================================


# Display the sidebar title

st.sidebar.title("My Conversations")

#create a button for starting a new conversation

if st.sidebar.button("New Chat"):

	# Reset the current chat and create a new thread
    
	reset_chat()

	# Rerun the streamlit app to update the interface
	st.rerun()



# Display all conversation threads in reverseOrder
# This shows the newest conversation first
for thread_id in st.session_state["chat_threads"][::-1]:

    if st.sidebar.button(str(thread_id), key=thread_id):
        st.session_state["thread_id"] = thread_id

        messages = load_conversation(thread_id)

        temp_messages = []

        for message in messages:
            if isinstance(message, HumanMessage):
                temp_messages.append(
                    {"role": "user", "content": message.content}
                )
            elif isinstance(message, AIMessage):
                temp_messages.append(
                    {"role": "assistant", "content": message.content}
                )

        st.session_state["message_history"] = temp_messages
        st.rerun()


# ====================================================================================
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])



# for message in st.session_state['chat_threads']:
#     with st.chat_message(message['role']):
#         st.text(message['content'])

user_input = st.chat_input("Enter the message: ")

if user_input:
        
    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    with st.chat_message("user"):
        st.text(user_input)


	# pass the current thread ID to LangGraph
    # Langgraph uses this ID to save and retrieve conversation memory
    
    CONFIG = {
          "configurable" : {"thread_id" : st.session_state['thread_id']}
	}
	
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
             message_chunk.content for message_chunk, metadata in chatbot.stream(
                 {'messages' : [HumanMessage(content=user_input)]},
                 config = CONFIG,
                 stream_mode = 'messages'
             )

			 # Display only AI messages
             # This prevents tool and user messages from appearing
			 if isinstance(message_chunk, AIMessage)
        )

    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})




