import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from database import save_plan,get_plan,init_db,update_plan
import os
import json

load_dotenv()

# 聊天客户端（DeepSeek）
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

# 向量化客户端（智谱）
embed_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL")
)   

MODEL_CHAT = os.getenv("MODEL_CHAT", "deepseek-flash")
MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING", "embedding-3")
init_db()

st.set_page_config(page_title="课程复习助手Agent")
st.title("课程复习助手Agent")
st.write("当前已接入工具:算剩余天数、查课表、生成复习计划、查历史计划、修改计划。")

def calculate_days(exam_date: str) -> str:
    """计算距离考试日期还有多少天。exam_date 格式:YYYY-MM-DD"""
    try:
        exam = datetime.strptime(exam_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        delta = (exam - today).days
        if delta<0:
            return f"考试日期已过，已经过去{abs(delta)}天."
        return f"距离{exam_date}还有{delta}天."
    except Exception as e:
        return f"日期解析失败:{e}"

def get_schedule(day: str) -> str:
    """查询指定星期几的课表。day格式:周一,周二....周日"""
    schedule = {
        "周一": "高等数学、大学英语",
        "周二": "数据结构、体育",
        "周三": "计算机网络、操作系统",
        "周四": "高等数学、概率论",
        "周五": "大学英语、毛概",
        "周六": "无课",
        "周日": "无课"
    }
    if day in schedule:
        return f"{day}的课程:{schedule[day]}"
    return f"没有找到{day}的课表,请用周一,周二...周日这样的格式。"

def generate_plan(subject: str,days_left: int,hours_per_day: float) -> str:
    """根据科目、剩余天数、每天可用小时数生成复习计划"""
    total_hours = days_left*hours_per_day
    per_day = round(hours_per_day,1)

    plan_text = (
        f"科目：{subject}，剩余 {days_left} 天，"
        f"每天 {per_day} 小时，总复习 {total_hours} 小时。"
    )
    save_msg = save_plan(subject,days_left,hours_per_day,plan_text)
    return f"{plan_text}\n{save_msg}"



tools = [
    {
        "type": "function",
        "function":{
            "name": "calculate_days",
            "description":"计算距离考试日期还有多少天。当用户询问考试还剩几天时调用。",
            "parameters":{
                "type": "object",
                "properties": {
                    "exam_date": {
                        "type":"string",
                        "description":"考试日期，格式 YYYY-MM-DD，例如 2026-10-01"
                    }
                },
                "required": ["exam_date"]
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name":"get_schedule",
            "description":"查询指定星期几的课表。当用户询问某天上什么课时调用",
            "parameters": {
                "type": "object",
                "properties":{
                    "day":{
                        "type":"string",
                        "description":"星期几，格式:周一，周二，周三，周四，周五，周六，周日"
                    }
                },
                "required":["day"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"generate_plan",
            "description":"根据科目、剩余天数、每天可用小时数生成复习计划。当用户要求制定复习计划时调用",
            "parameters":{
                "type":"object",
                "properties":{
                    "subject":{
                        "type":"string",
                        "description":"学科名称，例如高等数学、数据结构"
                    },
                    "days_left":{
                        "type":"integer",
                        "description":"距离考试还剩多少天"
                    },
                    "hours_per_day":{
                        "type":"number",
                        "description":"每天可用于复习的小时数，例如 2 或 1.5"
                    }
                },
                "required":["subject","days_left","hours_per_day"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_plan",
            "description":"查询已保存的计划。当用户询问历史计划,查看之前排的计划时调用",
            "parameters":{
                "type":"object",
                "properties":{
                    "plan_id":{
                        "type":"integer",
                        "description":"计划编号。传 0 或不传，表示查询全部计划"    
                    }
                },
                "required":[]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"update_plan",
            "description":"修改已保存计划的剩余天数或每天复习小时数。当用户要求更改某条已保存的计划时调用",
            "parameters":{
                "type":"object",
                "properties":{
                    "plan_id":{
                        "type":"integer",
                        "description":"要修改的计划编号，必填"    
                    },
                    "days_left":{
                        "type":"integer",
                        "description":"新的剩余天数。传 0 或不传表示不修改天数"
                    },
                    "hours_per_day":{
                        "type":"number",
                        "description":"新的每天复习小时数。传 0 或不传表示不修改小时数"
                    }
                },
                "required":["plan_id"]
            }
        }
    }
]

available_functions = {
    "calculate_days": calculate_days,
    "get_schedule" : get_schedule,
    "generate_plan":generate_plan,
    "get_plan": get_plan,
    "update_plan":update_plan
}

if "history" not in st.session_state:
    st.session_state.history = []

for role,text in st.session_state.history:
    st.write(f"**{role}**: {text}")

user_input = st.text_input("请输入你的问题: ")

if st.button("发送") and user_input:
    messages = [{"role": r,"content": t} for r,t in st.session_state.history]
    messages.append({"role": "user","content": user_input})
    try:
        with st.spinner("头脑风暴中..."):
            resp = client.chat.completions.create(
                model=MODEL_CHAT,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        msg = resp.choices[0].message
        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                fn = available_functions.get(fn_name)
                result = fn(**fn_args) if fn else "工具不存在"
                messages.append({
                    "role":"tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
                st.info(f"调用工具：{fn_name}({fn_args})")
            with st.spinner("正在整理结果..."):
                resp2 = client.chat.completions.create(
                    model=MODEL_CHAT,
                    messages=messages
                )
            answer = resp2.choices[0].message.content
        else:
            answer = msg.content

        st.session_state.history.append(("user",user_input))
        st.session_state.history.append(("assistant",answer))
        st.success(answer)

    except Exception as e:
        st.error(f"出错了:{e}")