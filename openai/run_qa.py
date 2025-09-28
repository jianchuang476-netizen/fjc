# 引用自你提供的文档

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# --- 第1步：加载我们昨天创建的FAISS索引 ---
print("正在加载向量化模型...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("正在加载FAISS索引...")
db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

# --- 第2步：加载LLM (DevAGI 版本) ---
# !! 重要 !!
# 请将下面的 'YOUR_DEVAGI_API_BASE_URL' 替换为 DevAGI 提供给你的 URL
# 请将下面的 'YOUR_DEVAGI_API_KEY' 替换为你的 DevAGI Key
# 请将下面的 'DEVAGI_MODEL_NAME' 替换为你想在 DevAGI 上使用的模型名称
print("正在加载LLM (DevAGI)...")
llm = ChatOpenAI(
    openai_api_base="https://api.fe8.cn/v1",  # 平台的URL
    openai_api_key="sk-VCxv6vtpakryhvcjo6DGJcXFejKHxVJRA68HFhUYT5aIxkXQ",      # 你的API Key
    model_name="text-embedding-3-large",            # 平台上的模型名称
    temperature=0.0                            # temperature设为0可以使模型输出更稳定和确定
)

# --- 第3步：创建并优化Prompt ---
prompt_template = """你是一个基于知识库的问答助手，仅用以下提供的知识库内容回答问题，若知识库没有相关信息，直接说“抱歉，我无法回答这个问题”。
知识库内容：{context}
用户问题：{question}
回答："""

prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# --- 第4步：构建最终的问答链 ---
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(),
    chain_type_kwargs={"prompt": prompt}
)

# --- 第5步：进行测试 ---
print("准备就绪，可以开始提问了。")
# 替换成你想问的问题
question = "论文的主要方法是什么？"
result = qa_chain.run(question)

print("="*20)
print("用户问题：", question)
print("模型回答：", result)
print("="*20)