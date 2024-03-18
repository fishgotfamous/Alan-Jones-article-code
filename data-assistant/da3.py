import streamlit as st
import pandas
import vega_datasets as data
from openai import OpenAI

#### Utilities

import time
# This utility function waits for a rum to complete. The code is copied directly from the OpenAI Cookbook.

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = st.session_state.client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def create_assistant_and_thread(client):
    # Create the assistant
    # Upload a file
    file = client.files.create(
        file=st.session_state.data_file,
        purpose="assistants",
    )

    st.session_state.assistant = client.beta.assistants.create(
        name = "Data Assistant 3",
        instructions="You are a data analyst and an expert in interpreting csv files and creating charts.",
        model="gpt-4-1106-preview",
        tools=[{"type": "code_interpreter"}],
        file_ids=[file.id],
    )

    st.session_state.thread = client.beta.threads.create()
    
### initialise session state
 
if 'key' not in st.session_state:
    st.session_state.key = ""
if 'data_file' not in st.session_state:
    st.write("You need to upload a csv file")
    if data_file := st.file_uploader("Upload a file"):
        st.session_state.data_file = data_file

# Check if the key has been set
if st.session_state.key != "":
    # We have a key so create a client and an assistant
    if 'client' not in st.session_state: st.session_state.client = OpenAI(api_key = st.session_state.key)
    if 'assistant' not in st.session_state: create_assistant_and_thread(st.session_state.client)

### Header

header = st.container()
with header:
    st.header("Data Assistant 3")
    
instructions = st.expander("Instructions", expanded = True)
with instructions:  
    st.write("""Instructions... TBA.
             You must enter a valid OpenAI API key before you do so and this means that OpenAI will charge your
             account for the usage. This should not be a lot, perhaps a few 10s of cents for a couple of questions.
             When you have finished, you should log on to your OpenAI account and delete any assistants 
             and files that you no longer want (otherwise you will be charged)
             """)
    st.session_state.key = st.text_input("API key")


### 

if prompt := st.chat_input():
    if "thread" in st.session_state:
        message = st.session_state.client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content=prompt
        )
        run = st.session_state.client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id=st.session_state.assistant.id,
            )
        run = wait_on_run(run, st.session_state.thread)
        messages = st.session_state.client.beta.threads.messages.list(thread_id=st.session_state.thread.id)

        for m in messages:
            with st.chat_message(f"{m.role}"):
                #st.markdown(f"{m.content[0].text.value}")
                st.markdown(f"{m.content[0]}")

    else:
        st.info("You need to provide an OpenAI API key to continue")




