# 引用自你提供的文档

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# --- 第1步：加载文档 ---
# 将 "llm_paper.pdf" 替换为你自己的PDF文件名
loader = PyPDFLoader("2106.01881v1.pdf")
documents = loader.load()
print(f"成功加载了 {len(documents)} 页文档。")

# --- 第2步：文档分割 ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = text_splitter.split_documents(documents)
print(f"文档被成功分割成 {len(splits)} 个片段。")

# --- 第3步：文本向量化与存储 ---
# 初始化向量化模型
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("向量化模型加载成功。")

# 将文本片段向量化并存入FAISS数据库
db = FAISS.from_documents(splits, embeddings)
print("文本已成功向量化并存入FAISS。")

# 保存到本地
db.save_local("faiss_index")
print("FAISS索引已成功保存到本地文件夹 'faiss_index'。")