from agentic_chatbot_db_backend import chatbot,get_all_threads
from rag_tool import ingest_rag_document
from langchain_core.messages import HumanMessage, AIMessage
import streamlit as st
import uuid
import os
import tempfile

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


if "last_uploaded_file" not in st.session_state:
    st.session_state["last_uploaded_file"] = None

add_thread(st.session_state['thread_id'])

# ========================= Sidebar =========================

# Sidebar title
st.sidebar.title("🤖 Agentic ChatBot")

# ==========================================================
# Document Upload
# ==========================================================

st.sidebar.subheader("📄 Knowledge Base")

if "last_uploaded_file" not in st.session_state:
    st.session_state["last_uploaded_file"] = None

uploaded_file = st.sidebar.file_uploader(
    label="Upload Document",
    type=["pdf"],
    help="Upload a document to add it to the chatbot's knowledge base."
)

if (
    uploaded_file is not None
    and (
        st.session_state["last_uploaded_file"] is None
        or uploaded_file.name != st.session_state["last_uploaded_file"]
    )
):

    import os
    import tempfile

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(uploaded_file.name)[1]
        ) as temp_file:

            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        with st.spinner("📚 Adding document to knowledge base..."):
            ingest_rag_document(temp_path)

        st.session_state["last_uploaded_file"] = uploaded_file.name

        st.sidebar.success("✅ Document uploaded successfully!")

    except Exception as e:

        st.sidebar.error(f"❌ {e}")

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

st.sidebar.divider()

# ==========================================================
# New Chat
# ==========================================================

if st.sidebar.button("➕ New Chat", use_container_width=True):

    # Find an existing empty conversation
    curr_thread = st.session_state["chat_threads"][-1]

    if len(get_messages(curr_thread)) == 0:
        st.session_state["thread_id"] = curr_thread
        st.session_state["message_history"] = []
    else:
        reset_chat()

    st.rerun()

st.sidebar.divider()

# ==========================================================
# Conversation History
# ==========================================================

st.sidebar.subheader("💬 Recent Conversations")


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
                    {
                        "role": "user",
                        "content": message.content
                    }
                )

            elif isinstance(message, AIMessage):

                if not message.content:
                    continue

                content = message.content

                # If the content is a JSON string, try to decode it
                if isinstance(content, str):
                    import json

                    try:
                        parsed = json.loads(content)

                        if isinstance(parsed, (dict, list)):
                            content = parsed

                    except Exception:
                        pass

                temp_messages.append(
                    {
                        "role": "assistant",
                        "content": content
                    }
                )

        st.session_state["message_history"] = temp_messages
        st.rerun()


# ====================================================================================
for message in st.session_state["message_history"]:

    with st.chat_message(message["role"]):

        content = message["content"]

        # Normal text message
        if isinstance(content, str):
            st.markdown(content)

        # Mixed content (text + images)
        elif isinstance(content, list):

            for item in content:

                if isinstance(item, str):
                    st.markdown(item)

                elif isinstance(item, dict):

                    if item.get("type") == "image":
                        st.image(item["path"])

                    elif item.get("type") == "text":
                        st.markdown(item["text"])

        # Single image
        elif isinstance(content, dict):

            if content.get("type") == "image":
                st.image(content["path"])

            elif content.get("type") == "text":
                st.markdown(content["text"])


# for message in st.session_state['chat_threads']:
#     with st.chat_message(message['role']):
#         st.text(message['content'])

#==================================================

# CHAT INPUT

# ===============================================
status_placeholder = st.empty()
user_input = st.chat_input("Enter the message: ")
if user_input:

    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.text(user_input)

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

            from langchain_core.messages import AIMessage, ToolMessage
            import json

            update_status("🧠 Thinking...")

            tool_status = {
                "search_tool": "🌐 Searching the web...",
                "WeatherTool": "🌤 Fetching weather information...",
                "calculator": "🧮 Calculating...",
                "get_stock_price": "📈 Fetching stock price...",
                "image_generation": "🎨 Generating image...",
                "video_generation": "🎬 Generating video...",
                "pdf_reader": "📄 Reading PDF...",
                "filesystem": "📁 Accessing files...",
                "email": "📧 Sending email...",
                "calendar": "📅 Accessing calendar..."
            }

            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):

                # Tool call started
                if (
                    isinstance(message_chunk, AIMessage)
                    and hasattr(message_chunk, "tool_calls")
                    and message_chunk.tool_calls
                ):

                    tool_name = message_chunk.tool_calls[0]["name"]

                    update_status(
                        tool_status.get(
                            tool_name,
                            f"🛠 Using {tool_name}..."
                        )
                    )

                # Tool finished
                elif isinstance(message_chunk, ToolMessage):

                    update_status("📄 Processing tool results...")

                    tool_output = message_chunk.content

                    # If tool returned JSON string
                    if isinstance(tool_output, str):
                        try:
                            tool_output = json.loads(tool_output)
                        except:
                            pass

                    # Image tool
                    if (
                        isinstance(tool_output, dict)
                        and tool_output.get("type") == "image"
                    ):
                        yield tool_output

                # Final LLM response
                elif isinstance(message_chunk, AIMessage):

                    if message_chunk.content:

                        update_status("✍️ Generating response...")

                        content = message_chunk.content

                        if isinstance(content, str):
                            yield content

                        elif isinstance(content, list):

                            for block in content:

                                if isinstance(block, dict):

                                    if block.get("type") == "text":
                                        yield block.get("text", "")

                                elif hasattr(block, "text"):
                                    yield block.text

                                elif isinstance(block, str):
                                    yield block

            status_placeholder.empty()

        # ----------------------------
        # Custom rendering
        # ----------------------------

        assistant_text = ""
        assistant_content = []

        text_placeholder = st.empty()

        for chunk in response_generator():

            # Stream text
            if isinstance(chunk, str):

                assistant_text += chunk

                text_placeholder.markdown(assistant_text)

                assistant_content.append(chunk)

            # Render image
            elif isinstance(chunk, dict):

                if chunk.get("type") == "image":

                    st.image(chunk["path"])

                    assistant_content.append(chunk)

        # Store chat history
        if assistant_content:

            if len(assistant_content) == 1 and isinstance(assistant_content[0], str):

                stored_content = assistant_text

            else:

                stored_content = assistant_content

            st.session_state["message_history"].append(
                {
                    "role": "assistant",
                    "content": stored_content
                }
            )