import os
import requests
from langchain.tools import Tool
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# --- 密钥配置 ---
# !! 重要 !! 请确保所有密钥都已正确填写
# 1. 大语言模型 (豆包)
os.environ["OPENAI_API_BASE"] = "https://ark.cn-beijing.volces.com/api/v3"
os.environ["OPENAI_API_KEY"] = "7f834f73-3d93-485c-b323-8bd3c5672494"
MODEL_NAME = "deepseek-v3-1-250821"

# 2. OpenWeatherMap API Key
os.environ["OPENWEATHERMAP_API_KEY"] = "4c376f1bc1cc4f84cf26f5a06b519b4f"

# 3. 高德地图 API Key
AMAP_API_KEY = "e21489bcb6097854af766e06d52db046"
# ----------------------------------------------------


# --- 工具一：天气查询工具 ---
openweathermap = OpenWeatherMapAPIWrapper()
weather_tool = Tool(
    name="WeatherChecker",
    func=openweathermap.run,
    description="非常有用，当你需要查询指定城市当前的天气时，你应该使用它。输入必须是一个城市名称，例如 'beijing'。"
)


# --- 工具二：景点查询工具 ---
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


# --- 整合所有工具 ---
tools = [weather_tool, attractions_tool]

# --- 创建 Agent ---
# 1. 初始化 LLM
llm = ChatOpenAI(model_name=MODEL_NAME, temperature=0.0)

# 2. 初始化 AgentExecutor
# 我们使用 ZERO_SHOT_REACT_DESCRIPTION 类型的 Agent，它会根据工具的描述来决定使用哪个工具
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True  # 设置为 True，可以看到 Agent 的完整思考过程
)

# --- 运行 Agent ---
print("\n--- Agent 已准备就绪，开始执行任务 ---")
# 提出一个需要多步思考和多个工具协作才能解决的问题
query = "我想去北京旅游，周末天气怎么样？推荐几个景点。"
response = agent.run(query)

print("\n--- Agent 最终回答 ---")
print(response)
print("---------------------\n")