from pathlib import Path

from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor

config_list = [
    {
        # Let's choose the Meta's Llama 3.1 model (model names must match Ollama exactly)
        # "model": "qwen2.5:7b",
        # "model": "llama3.2:3b",
        "model": "mistral:latest",
        # We specify the API Type as 'ollama' so it uses the Ollama client class
        "api_type": "ollama",
        'api_key': "NULL",
        "stream": False,
        "base_url": "http://127.0.0.1:11434/v1",
        "price" : [0, 0]
    }
]

# Setting up the code executor
workdir = Path("coding")
workdir.mkdir(exist_ok=True)
code_executor = LocalCommandLineCodeExecutor(work_dir=workdir)

# Setting up the agents

# The UserProxyAgent will execute the code that the AssistantAgent provides
user_proxy_agent = UserProxyAgent(
    name="User",
    code_execution_config={"executor": code_executor},
    is_termination_msg=lambda msg: "FINISH" in msg.get("content"),
)

system_message = """你是一位帮助用户编写并执行代码的AI助手。
在以下情况下，建议用户执行Python代码（使用Python代码块）。在代码块中必须表明代码的类型。
你只需要创建一个可以运行的示例。
不要建议需要用户修改的未完成代码。
如果代码不是打算给用户执行的，就不要使用代码块。如果没有多段代码，不要包含多个代码块。
不要要求用户复制和粘贴结果，而是使用 print 函数输出相关结果。
检查用户返回的执行结果。
对于每一行代码都要给出中文注释，对于关键的代码要展开描述。

如果结果显示有错误，修正错误。

重要提示：如果执行成功，只输出“FINISH”。"""

# The AssistantAgent, using the Ollama config, will take the coding request and return code
assistant_agent = AssistantAgent(
    name="Ollama Assistant",
    system_message=system_message,
    llm_config={"config_list": config_list},
)

# Start the chat, with the UserProxyAgent asking the AssistantAgent the message
chat_result = user_proxy_agent.initiate_chat(
    assistant_agent,
    message="写一段代码，计算从1到10000中质数的数量.",
)