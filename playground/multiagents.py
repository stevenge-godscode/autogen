import autogen
from autogen.coding import LocalCommandLineCodeExecutor

# 从JSON文件中获取配置列表，文件路径为"playground/OAI_CONFIG_LIST"
# filter_dict用于过滤需要的tags（可选）。这里注释掉了过滤条件，表示获取全部配置
config_list = autogen.config_list_from_json(
    "playground/OAI_CONFIG_LIST",
    # filter_dict={"tags": ["gpt-4o"]},  # comment out to get all
)

# 定义GPT-4模型的配置，包括缓存种子、温度、配置列表和超时时间
# cache_seed用于控制结果的一致性，temperature控制生成的随机性，timeout设置超时时间
# config_list参数是从上一步得到的配置列表
gpt4_config = {
    "cache_seed": 44,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}

# 创建用户代理（UserProxyAgent），其代表人类用户与其他代理交互
# code_execution_config设置为False，表示此代理不执行代码
user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
    code_execution_config=False,
)

# 创建工程师代理（AssistantAgent），负责编写代码来完成任务
# 使用gpt4_config配置，代码块中明确工程师只能编写完整的代码，并且不能让用户修改代码
engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=gpt4_config,
    system_message="""Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
""",
)

# 创建科学家代理（AssistantAgent），负责分类论文，但不编写代码
scientist = autogen.AssistantAgent(
    name="Scientist",
    llm_config=gpt4_config,
    system_message="""Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code.""",
)

# 创建计划制定者代理（AssistantAgent），负责制定并优化计划
# 计划可能涉及工程师和科学家，并在管理员批准前不断修订
planner = autogen.AssistantAgent(
    name="Planner",
    system_message="""Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
""",
    llm_config=gpt4_config,
)

# 创建执行者代理（UserProxyAgent），其执行由工程师编写的代码，并报告结果
executor = autogen.UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="NEVER",
    code_execution_config={
        "last_n_messages": 100,
        "work_dir": "paper",
        "use_docker": False,  # 设置use_docker=True以使用Docker来运行代码，Docker更安全
    },
)

# 创建批判者代理（AssistantAgent），负责检查计划、声明和代码，并提供反馈
critic = autogen.AssistantAgent(
    name="Critic",
    llm_config=gpt4_config,
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL."
)


# 创建一个群聊，包含所有代理，包括用户代理、工程师、科学家、计划制定者、执行者和批判者
# messages初始化为空列表，max_round设置为50表示最多允许50轮对话
groupchat = autogen.GroupChat(
    agents=[user_proxy, engineer, scientist, planner, executor, critic], messages=[], max_round=200
)

# 创建群聊管理器（GroupChatManager），用于管理该群聊会话
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

# 用户代理发起聊天，向群聊管理器发送初始消息
# 消息内容是查找最近一周内Arxiv上关于LLM应用的论文，并创建一个不同领域的Markdown表格
user_proxy.initiate_chat(
    manager,
    message="""
find papers on LLM applications from arxiv in the last week, create a markdown table of different domains.
""",
)