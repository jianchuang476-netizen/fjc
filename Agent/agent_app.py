import os
import requests
import streamlit as st
from langchain.tools import Tool
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# --- 页面配置 ---
st.set_page_config(page_title="旅游规划智能助手 (Agent)", layout="wide")
st.title("旅游规划智能助手 (Agent) 🤖")
st.info("请输入您的旅游需求，例如：“我想去杭州旅游，周末天气怎么样？推荐几个景点。”")

# --- 密钥配置 ---
# !! 重要 !! 请确保所有密钥都已正确填写
# 1. 大语言模型 (豆包)
os.environ["OPENAI_API_BASE"] = "https://ark.cn-beijing.volces.com/api/v3"
os.environ["OPENAI_API_KEY"] = ""
MODEL_NAME = "deepseek-v3-1-250821"

# 2. OpenWeatherMap API Key
os.environ["OPENWEATHERMAP_API_KEY"] = ""

# 3. 高德地图 API Key
AMAP_API_KEY = ""
# ----------------------------------------------------


# --- 工具定义 (和之前一样) ---
# 工具一：天气查询
openweathermap = OpenWeatherMapAPIWrapper()
weather_tool = Tool(
    name="WeatherChecker",
    func=openweathermap.run,
    description="非常有用，当你需要查询指定城市当前的天气时，你应该使用它。输入必须是城市的**英文名称或拼音**，例如 'beijing' 或 'shanghai'。如果用户用中文提问，请先将其翻译成英文或拼音。"
)


# 工具二：景点查询
def get_attractions(city: str) -> str:
    """根据城市名称，查询该城市的热门旅游景点。"""
    try:
        url = f"https://restapi.amap.com/v3/place/text?keywords=景点&city={city}&output=json&key={AMAP_API_KEY}&page=1&offset=5"
        response = requests.get(url)
        response.raise_for_status()
        attractions_data = response.json()['pois']
        if not attractions_data:
            return f"在{city}没有找到热门景点。"
        attraction_names = [poi['name'] for poi in attractions_data]
        return f"{city}的热门景点有：{', '.join(attraction_names)}。"
    except Exception as e:
        return f"查询景点失败，错误信息：{e}"


attractions_tool = Tool(
    name="AttractionFinder",
    func=get_attractions,
    description="非常有用，当你需要查询指定城市的热门旅游景点时，你应该使用它。输入必须是一个城市名称，例如 '上海'。"
)

tools = [weather_tool, attractions_tool]


# --- Agent 初始化 (使用缓存避免重复加载) ---
@st.cache_resource
def setup_agent():
    llm = ChatOpenAI(model_name=MODEL_NAME, temperature=0.0)
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True  # Agent的思考过程会打印在终端
    )
    return agent


agent = setup_agent()

# --- Streamlit 交互界面 ---
query = st.text_input("请输入您的问题：", key="query_input")

if st.button("开始规划"):
    if query:
        # VVVV --- 这里是修正后的代码 --- VVVV
        with st.spinner('智能助手正在思考中，请稍候... (详细思考过程请查看终端)'):
            try:
                # 直接运行 Agent
                response = agent.run(query)

                # 在网页上显示最终结果
                st.subheader("最终规划建议：")
                st.success(response)
            except Exception as e:
                st.error(f"执行过程中出现错误：{e}")
        # ^^^^ --- 这里是修正后的代码 --- ^^^^
    else:
        st.warning("请输入您的问题。")