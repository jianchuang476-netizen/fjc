# 引用自你提供的文档

import streamlit as st
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# --- 页面配置 ---
st.set_page_config(page_title="个人知识库问答系统", layout="wide")
st.title("个人知识库问答系统")

# --- 豆包方舟平台 LLM 配置 ---
# !! 重要 !! 替换为你自己的 ARK_API_KEY
OPENAI_API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
OPENAI_API_KEY = "7f834f73-3d93-485c-b323-8bd3c5672494"
MODEL_NAME = "doubao-1-5-pro-32k-250115"


# -----------------------------------------

# --- 后端处理函数 ---

@st.cache_resource
def load_embeddings():
    """加载向量化模型，使用缓存避免重复加载"""
    # 使用国内镜像加速模型下载
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def process_uploaded_file(uploaded_file):
    """处理上传的文件，进行分割和向量化，并创建FAISS索引"""
    if uploaded_file is not None:
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        loader = PyPDFLoader(file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(documents)

        embeddings = load_embeddings()
        db = FAISS.from_documents(splits, embeddings)
        return db
    return None


def create_qa_chain(db):
    """根据FAISS索引创建问答链"""
    llm = ChatOpenAI(
        openai_api_base=OPENAI_API_BASE,
        openai_api_key=OPENAI_API_KEY,
        model_name=MODEL_NAME,
        temperature=0.0
    )

    prompt_template = """你是一个基于知识库的问答助手，仅用以下提供的知识库内容回答问题，若知识库没有相关信息，直接说“抱歉，我无法回答这个问题”。
    知识库内容：{context}
    用户问题：{question}
    回答："""

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    retriever = db.as_retriever(search_kwargs={"k": 5})

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain


# --- Streamlit 界面 ---

if 'db' not in st.session_state:
    st.session_state.db = None
if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None

uploaded_file = st.file_uploader("上传你的PDF文档", type=["pdf"])

if uploaded_file:
    with st.spinner('正在处理文档...'):
        st.session_state.db = process_uploaded_file(uploaded_file)
        st.session_state.qa_chain = create_qa_chain(st.session_state.db)
    st.success("文档处理完成！现在可以开始提问了。")

question = st.text_input("请输入你的问题")

if st.button("获取答案") and question:
    if st.session_state.qa_chain:

        with st.spinner('正在思考...'):
            result = st.session_state.qa_chain.run(question)
            st.write("回答：", result)
    else:
        st.warning("请先上传文档。")