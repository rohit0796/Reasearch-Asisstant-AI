import traceback
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import BaseTool
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
lama = "llama3-70b-8192"
deep_seek = "deepseek-r1-distill-llama-70b"
llm = ChatGroq(temperature=0.1, model_name= lama)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000, chunk_overlap=200)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# --- Vector Store Manager ---


class VectorStoreManager:
    def __init__(self):
        self.store = None

    def get_store(self):
        if self.store is None:
            raise ValueError("No documents have been added yet.")
        return self.store

    def add_documents(self, docs):
        if not docs:
            return False
        if self.store is None:
            self.store = FAISS.from_documents(docs, embeddings)
        else:
            self.store.add_documents(docs)
        return True


vector_manager = VectorStoreManager()

# --- Input Schemas ---


class YouTubeInput(BaseModel):
    url: str = Field(description="Full YouTube URL including https://")


class PDFInput(BaseModel):
    path: str = Field(description="Local path to PDF file")


class WebInput(BaseModel):
    url: str = Field(description="Full web URL including https://")


class QnAInput(BaseModel):
    input: str = Field(
        description="Question to be answered from uploaded documents")

# --- Tools ---


class YouTubeTool(BaseTool):
    name: str = "youtube_processor"
    description: str = "Process YouTube video transcripts from URLs"
    args_schema: type = YouTubeInput

    def _run(self, url: str):
        try:
            video_id = url.split("v=")[-1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            print(transcript)
            text = " ".join([t['text'] for t in transcript])
            docs = text_splitter.create_documents([text])
            for doc in docs:
                doc.metadata["source"] = url
            vector_manager.add_documents(docs)
            return f"YouTube transcript processed: {url}"
        except Exception as e:
            return f"Error processing YouTube video: {str(e)}"


class PDFTool(BaseTool):
    name: str = "pdf_processor"
    description: str = "Process PDF documents from local file paths"
    args_schema: type = PDFInput

    def _run(self, path: str):
        if not os.path.isfile(path):
            return f"Error: File path {path} does not exist."
        try:
            loader = PyPDFLoader(path)
            docs = loader.load_and_split(text_splitter)
            for doc in docs:
                doc.metadata["source"] = path
            vector_manager.add_documents(docs)
            return "PDF processed successfully"
        except Exception as e:
            return f"Error processing PDF: {str(e)}"


class WebTool(BaseTool):
    name: str = "web_processor"
    description: str = "Process web articles from URLs"
    args_schema: type = WebInput

    def _run(self, url: str):
        try:
            loader = WebBaseLoader(url)
            docs = loader.load_and_split(text_splitter)
            for doc in docs:
                doc.metadata["source"] = url
            vector_manager.add_documents(docs)
            return f"Web article processed: {url}"
        except Exception as e:
            return f"Error processing web page: {str(e)}"


class RetrievalQATool(BaseTool):
    name: str = "retrieval_qa"
    description: str = "To Answer questions by the user"
    args_schema: type = QnAInput

    def _run(self, input: str):
        return retrieval_qa(input)


class DefaultResponderTool(BaseTool):
    name: str = "default_responder"
    description: str = "Use this to reply to general messages like greetings."

    def _run(self, input: str):
        return "Hello! I can process YouTube videos, PDFs, and web content. Ask me anything!"

# --- Retrieval Logic ---


def retrieval_qa(query: str) -> str:
    try:
        store = vector_manager.get_store()
        retriever = store.as_retriever(
            search_type="mmr", search_kwargs={"k": 3})
        docs = retriever.invoke(query)

        if not docs:
            return "No relevant documents found."

        context = "\n\n".join(
            [f"[{doc.metadata.get('source', 'unknown')}] {doc.page_content}" for doc in docs[:3]])
        prompt = f"""
                Use the following context to answer the question:
                {context}

                Question: {query}
                Answer:"""
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Retrieval error: {str(e)}"

# --- Agent Setup ---


def create_agent_executor():
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        memory_key='chat_history',
        max_token_limit=500,
        return_messages=True
    )

    tools = [
        YouTubeTool(),
        RetrievalQATool(),
        PDFTool(),
        WebTool(),
    ]

    prompt = PromptTemplate.from_template("""
                You are a highly capable AI research assistant designed to help users by using available tools. You MUST always use the correct tool to perform the task — DO NOT answer directly unless specified.

                You have access to the following tools:

                - **pdf_processor**: Use this to process content from a PDF file.
                - **youtube_processor**: Use this to extract and store transcripts from YouTube video URLs.
                - **web_processor**: Use this to scrape and store information from web articles.
                - **retrieval_qa**: Use this to answer questions using the information previously added via the other tools.

                Rules:
                1. **Do NOT answer a user’s question directly** unless it is a greeting, small talk, or generic AI conversation. For any question related to content from documents/videos/articles, always use the `retrieval_qa` tool.
                2. If a user shares a YouTube URL, process it using `youtube_processor`.
                3. If a user shares a web link, use the `web_processor`.
                4. If a user provides a PDF file path, use the `pdf_processor`.
                5. If a user asks a question after uploading any document, use `retrieval_qa`.

                You must always follow this format exactly:

                Question: the user’s input  
                Thought: think through what the user wants and choose the correct tool  
                Action: the tool name (one of: pdf_processor, youtube_processor, web_processor, retrieval_qa)  
                Action Input: the input passed to the tool  
                Observation: the result returned by the tool  
                ... (repeat Action/Observation as needed)  
                Final Answer: your response to the user based on the tool’s result

                Here is the conversation context:
                {chat_history}
                Here are your tools:
                {tools}
                Tool names you can use: {tool_names}

                Begin!

                Question: {input}
                {agent_scratchpad}
                """)

    agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iteration = 5
    )


# --- Main Function ---


agent = None


def process_input(user_input: str) -> str:
    global agent
    print("User input:", user_input)

    if agent is None:
        agent = create_agent_executor()

    try:
        # if user_input.startswith('ADD_PDF '):
        #     path = user_input.split(maxsplit=1)[1]
        #     tool = PDFTool()
        #     return tool.run({"path": path})
        result = agent.run(user_input)
        print("Agent result:", result)
        return result.get("output", result) if isinstance(result, dict) else result
    except Exception as e:
        print("Agent error:", e)
        traceback.print_exc()
        return f"Agent error: {str(e)}"
