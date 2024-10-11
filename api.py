import streamlit as st
import requests
import json

def extract_json_from_stream(response_content):
    # 找到有效 JSON 起始位置的索引
    json_start_idx = response_content.find(b'{"')
    if json_start_idx != -1:
        # 截取有效 JSON 部分
        json_data = response_content[json_start_idx:]
        # 解码并返回 JSON 对象
        return json.loads(json_data.decode('utf-8'))
    else:
        return None

def query_knowledge_base(question):
    url = 'https://453642-proxy-7861.dsw-gateway-cn-shanghai.data.aliyun.com/chat/kb_chat'    #修改IP地址
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        "query": question,
        "knowledge_base_name": "samples",
        "top_k": 3,
        "score_threshold": 1,
        #"history": [],
        #保留历史会话
        "history": st.session_state.history,
        "stream": False,
        "model_name": "zhipu-api",
        "temperature": 0.05,
        "max_tokens": 0,
        "prompt_name": "default"
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Response content:", response.content)  # Add this line for debugging
    try:
        if response.status_code == 200:
            # 提取有效 JSON 部分并解析
            json_response = extract_json_from_stream(response.content)
            if json_response is not None:
                return json_response
            else:
                print('*'*30)
                print('error')
                print('*'*30)
                return {"error": "Failed to extract JSON from response."}
        else:
            return {"error": "Failed to query knowledge base."}
    except Exception as e:
        print("Error:", e)
        return {"error": "Failed to parse response as JSON."}

# Streamlit UI
st.title("基于本地知识库的ChatMP-FAQ")
st.write("本密评FAQ聊天机器人基于Langchain-Chatchat+GLM4")
st.write("知识来源：丁香医生")
question = st.text_input("请输入您的问题：")

# if st.button("提交"):
#     if question:
#         result = query_knowledge_base(question)
#         if "error" in result:
#             st.error("查询知识库时出错。")
#         else:
#             st.write("回答：")
#             st.write(result["answer"])
#             if result.get("docs"):
#                 st.write("相关文档：")
#                 for doc in result["docs"]:
#                     st.write(doc)
#             else:
#                 st.write("没有相关文档。")
#     else:
#         st.warning("请输入一个问题。")

#定义历史会话轮数
num = 3
if 'history' not in st.session_state:
    st.session_state.history = []   
user = {'role': 'user', 'content': ''}
assistant = {'role': 'assistant', 'content': ''}
if st.button("提交"):
    if question:
        # st.write(st.session_state.history)
        result = query_knowledge_base(question)
        if "error" in result:
            st.error("查询知识库时出错。")
        else:
            user = {'role': 'user', 'content': question}
            assistant = {'role': 'assistant', 'content': result["answer"]}
            st.session_state.history.append(user)
            st.session_state.history.append(assistant)
            if len(st.session_state.history) > 2 * num:
                st.session_state.history = st.session_state.history[-(2 * num):]
            st.write(len(st.session_state.history))
            st.write(st.session_state.history)
            st.write("回答：")
            st.write(result["answer"])
            if result.get("docs"):
                st.write("相关文档：")
                for doc in result["docs"]:
                    st.write(doc)
            else:
                st.write("没有相关文档。")
    else:
        st.warning("请输入一个问题。")