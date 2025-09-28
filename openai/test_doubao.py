from langchain.chat_models import ChatOpenAI

# !! 重要 !!
# 请将下面的占位符替换为你从豆包方舟平台获取的真实信息
# 1. API Base URL (来自你的文档)
OPENAI_API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
# 2. 你的 ARK_API_KEY
OPENAI_API_KEY = "7f834f73-3d93-485c-b323-8bd3c5672494"
# 3. 你想使用的模型名称 (来自你的文档)
MODEL_NAME = "doubao-1-5-pro-32k-250115"
# ----------------------------------------------------

print("正在初始化豆包 LLM (方舟平台)...")

try:
    # 使用 ChatOpenAI 类来连接豆包的 OpenAI 兼容接口
    llm = ChatOpenAI(
        openai_api_base=OPENAI_API_BASE,
        openai_api_key=OPENAI_API_KEY,
        model_name=MODEL_NAME,
        temperature=0.0,
        request_timeout=60
    )

    print("LLM 初始化成功，正在发送测试请求...")

    # 发送一个最简单的请求
    response = llm.predict("你好")

    print("成功从豆包收到回复：")
    print(response)

except Exception as e:
    print("\n--- 出错了 ---")
    print("错误类型:", type(e).__name__)
    print("错误信息:", e)