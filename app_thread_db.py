from agentic_chatbot_db_backend import chatbot,get_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import streamlit as st
import uuid

# import sys
# import os

# print("App")
# print(sys.executable)
# print(os.getcwd())
# print(os.path.abspath("chatbot.db"))

# This method generates the unique thread ID for the new conversation
def generate_thread_id():
    return str(uuid.uuid4())



# This methods adds the new thread or conversation in our conversation history
def add_thread(thread_id):

    # for key,value in st.session_state['chat_threads']:
    #     if key == thread_id:
    #         return

    # config = create_configuration(thread_id)
    # heading = chatbot.invoke({'messages' : })
    # st.session_state["chat_threads"].append({'thread_id':})
      
        
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


def create_configuration(thread_id:str)->dict:
    config = {'configurable' : {'thread_id' : thread_id}}
    return config

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
    st.session_state['chat_threads'] = get_all_threads()


add_thread(st.session_state['thread_id'])

# ======================== sidebar converation history ===================================

# Display the sidebar title

st.sidebar.title("My Conversations")

#create a button for starting a new conversation

if st.sidebar.button("New Chat"):

    # Find an existing empty conversation
    curr_thread = st.session_state["chat_threads"][-1]


    if len(get_messages(curr_thread)) == 0:
        # Switch to the existing empty conversation
        st.session_state["thread_id"] = curr_thread
        st.session_state["message_history"] = []
    else:
        # No empty conversation exists, so create a new one
        reset_chat()

    st.rerun()
    
	# if len(get_messages(st.session_state['thread_id'])) > 0:
    #       reset_chat()
    #       st.rerun()



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

status_placeholder = st.empty()
user_input = st.chat_input("Enter the message: ")

if user_input:

    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.text(user_input)

    # Pass the current thread ID to LangGraph
    CONFIG = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        }
    }

    with st.chat_message("assistant"):

        def update_status(message):
            status_placeholder.markdown(
                f"""
                <div style="
                    font-size:0.82rem;
                    color:#8c8c8c;
                    padding-top:4px;
                    padding-bottom:4px;
                ">
                    {message}
                </div>
                """,
                unsafe_allow_html=True
            )

        def response_generator():

            update_status("🧠 Thinking...")

            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):

                # Detect the current LangGraph node
                if metadata and "langgraph_node" in metadata:

                    node = metadata["langgraph_node"]

                    if node == "chat_node":
                        update_status("🧠 Thinking...")

                    elif node == "tools":
                        update_status("🛠 Using tools...")

                    elif node == "search":
                        update_status("🌐 Searching the web...")

                    elif node == "weather":
                        update_status("🌤 Fetching weather...")

                    elif node == "stocks":
                        update_status("📈 Fetching stock price...")

                # Detect tool calls
                if hasattr(message_chunk, "tool_calls") and message_chunk.tool_calls:

                    tool_name = message_chunk.tool_calls[0]["name"]

                    update_status(f"🛠 Calling `{tool_name}`...")

                # Stream only AI response
                if isinstance(message_chunk, AIMessage):

                    if message_chunk.content:
                        yield message_chunk.content

            # Remove the status after the response is complete
            status_placeholder.empty()

        ai_message = st.write_stream(response_generator())

    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )