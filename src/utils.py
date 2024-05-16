import os
from langchain_openai import ChatOpenAI
from langchain_community.llms import Tongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.transform import BaseTransformOutputParser
from typing import List


class MyStrOutputParser(BaseTransformOutputParser[str]):
    """OutputParser that parses LLMResult into the top likely string."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "schema", "output_parser"]

    @property
    def _type(self) -> str:
        """Return the output parser type for serialization."""
        return "default"

    def parse(self, text: str) -> str:
        """Returns the input text with no changes."""
        if text in ["Thought", "Question", "Answer", "Given", "When", "Then"]:
            text = '\n' + text
        return text


def get_response(template, is_interactive=True, **kwargs):
    if "DASHSCOPE_API_KEY" in os.environ:
        llm_chat = Tongyi
        llm_model_name = "qwen1.5-0.5b-chat"  # 通义千问1.5对外开源的0.5B规模参数量是经过人类指令对齐的chat模型
        # llm_model_name = "qwen1.5-110b-chat"  # 通义千问1.5对外开源的110B规模参数量是经过人类指令对齐的chat模型
        # llm_model_name = "baichuan-7b-v1"  # 由百川智能开发的一个开源的大规模预训练模型，70亿参数，支持中英双语，上下文窗口长度为4096。
        # llm_model_name = "baichuan2-13b-chat-v1"  # 由百川智能开发的一个开源的大规模预训练模型，130亿参数，支持中英双语，上下文窗口长度为4096。
        # llm_model_name = "llama3-8b-instruct"  # Llama3系列是Meta在2024年4月18日公开发布的大型语言模型（LLMs），llama3-8B拥有80亿参数，模型最大输入为6500，最大输出为1500，仅支持message格式，限时免费调用。
        # llm_model_name = "ziya-llama-13b-v1"  # 姜子牙通用大模型由IDEA研究院认知计算与自然语言研究中心主导开源，具备翻译、编程、文本分类、信息抽取、摘要、文案生成、常识问答和数学计算等能力。
        # llm_model_name = "chatyuan-large-v2"  # ChatYuan模型是由元语智能出品的大规模语言模型，它在灵积平台上的模型名称为"chatyuan-large-v2"。ChatYuan-large-v2是一个支持中英双语的功能型对话语言大模型，是继ChatYuan系列中ChatYuan-large-v1开源后的又一个开源模型。

        # llm_model_name = st.session_state.llm_model_name

    # elif "OPENAI_API_KEY" in os.environ:
    else:
        llm_chat = ChatOpenAI
        llm_model_name = "gpt-4-turbo-preview"

    if is_interactive:
        llm = llm_chat(temperature=0.0, model=llm_model_name, model_kwargs={"stop": "\nAnswer"})
    else:
        llm = llm_chat(temperature=0.0, model=llm_model_name)
    # output_parser = StrOutputParser()
    output_parser = MyStrOutputParser()
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | output_parser

    stream = chain.stream(kwargs)
    return stream
