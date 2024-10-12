import streamlit as st
import requests
import json

def extract_json_from_stream(response_content):
    extracted_jsons = []
    json_start_idx = response_content.find(b'{"id"')
    while json_start_idx != -1:
        # 找到下一个JSON对象的结束位置
        json_end_idx = response_content.find(b'}]}', json_start_idx)
        if json_end_idx != -1:
            json_data = response_content[json_start_idx:json_end_idx+3]
            # print(json_data.decode('utf-8'))
            # json_str = json_data.decode('utf-8')
            # print(json.loads(json_str))
            extracted_jsons.append(json.loads(json_data.decode('utf-8')))
            json_start_idx = response_content.find(b'{"id"', json_end_idx + 1)
        else:
            return None
    docs = ''
    if extracted_jsons[0]['docs'] != '':
        docs = ''.join(extracted_jsons[0]['docs'])
    answer = []
    for item in extracted_jsons:
        answer.append(item['choices'][0]['delta']['content'])
    result = {"answer": ''.join(answer),'docs': docs}
    return result
def query_knowledge_base(question):
    # url = 'https://453642-proxy-7861.dsw-gateway-cn-shanghai.data.aliyun.com/chat/kb_chat'
    url = 'http://127.0.0.1:7861/chat/kb_chat'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "query": "你好",
        "mode": "local_kb",
        "kb_name": "samples",
        "top_k": 3,
        "score_threshold": 2,
        "history": st.session_state.history,
        "stream": True,
        "model": "glm4-chat",
        "temperature": 0.7,
        "max_tokens": 0,
        "prompt_name": "default",
        "return_direct": False
    }
    response = requests.post(url, headers=headers, json=data)
    # print('*'*45)
    # print("Response content:", response.content)  # Add this line for debugging
    # print('*'*45)
    # print(response.status_code)
    # print('*'*45)
    # print(response.headers)
    # print('*'*45)
    # print(response.encoding)
    # print('*'*45)
    # print(response.url)
    # print('*'*45)
    # print(response.history)
    # print('*'*45)
    # print(response.cookies)
    # print('*'*45)
    try:
        if response.status_code == 200:
            # 提取有效 JSON 部分并解析
            json_response = extract_json_from_stream(response.content)
            print(json_response)
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
st.title("Langchain-RAG-GLM4")
st.write("医疗对话聊天机器人基于Langchain+GLM4")
st.write("知识来源：丁香医生")
question = st.text_input("请输入您的问题：")

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
            if result['docs'] != '':
                st.write("相关文档：")
                # for doc in result["docs"]:
                #     st.write(doc)
                st.write(result["docs"])
            else:
                st.write("没有相关文档。")
    else:
        st.warning("请输入一个问题。")