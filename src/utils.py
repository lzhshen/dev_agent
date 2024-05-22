import os
import re
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


def format_diagram(class_diagram):
    format_class_diagram = re.sub(r"<(.+?)>", r"~\1~", class_diagram)
    return format_class_diagram


# def show_diagram(class_diagram, iframe_index=2):
#     from time import sleep
#     import streamlit as st
#     from streamlit.logger import get_logger
#     from streamlit.components.v1 import html
#     from streamlit_js_eval import streamlit_js_eval
#     log = get_logger(__name__)
#
#     if "svg_height" not in st.session_state:
#         st.session_state["svg_height"] = 200
#
#     if "previous_mermaid" not in st.session_state:
#         st.session_state["previous_mermaid"] = ""
#
#     def mermaid(code: str) -> None:
#         html(
#             f"""
# <p id="mermaidError"></p>
# <!-- htmlmin:ignore -->
# <pre class="myMermaidClass">
#     {code}
# </pre>
# <!-- htmlmin:ignore -->
#
# <script type="module">
#     //import mermaid from '/app/static/mermaid@9.3.0.min.js';
#     import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
#     /*mermaid.initialize({{
#         startOnLoad: true,
#         logLevel: 5,
#         securityLevel: 'loose',
#         arrowMarkerAbsolute: true
#     }});*/
#     mermaid.initialize({{ logLevel: 5, startOnLoad: false }});
#     try {{
#         await mermaid.run({{
#           querySelector: '.myMermaidClass',
#         }});
#     }}
#     catch(err) {{
#         document.getElementById("mermaidError").innerHTML = err.message;
#     }}
# </script>
# """,
#             height=st.session_state["svg_height"] + 50,
#         )
#         # st.write(st.session_state["svg_height"])
#
#     format_class_diagram = format_diagram(class_diagram)
#     mermaid(format_class_diagram)
#
#     if format_class_diagram != st.session_state["previous_mermaid"] or True:
#         st.session_state["previous_mermaid"] = format_class_diagram
#         sleep(1)
#         streamlit_js_eval(
#             js_expressions=f'parent.document.getElementsByTagName("iframe")[{iframe_index}].contentDocument.getElementsByClassName("mermaid")[0].getElementsByTagName("svg")[0].getBBox().height',
#             key="svg_height",
#         )
#         # st.toast(st.session_state["svg_height"])
#         log.info(f'svg_height={st.session_state["svg_height"]}')


def show_diagram(class_diagram):
    import streamlit as st
    from streamlit.components.v1 import html

    pre_class = "mermaid"
    # pre_class = "myMermaidClass"
    format_class_diagram = format_diagram(class_diagram)

    if "svg_height" not in st.session_state:
        st.session_state["svg_height"] = 200

    if "previous_mermaid" not in st.session_state:
        st.session_state["previous_mermaid"] = ""
    font_size = st.slider("Mermaid font size", 10, 30, 18)
    html(
        """<p id="mermaidError"></p>
        <!-- htmlmin:ignore -->
        <pre class="%s">
            %s
        </pre>
        <!-- htmlmin:ignore -->
        
        <script type="module">
            //import mermaid from '/app/static/mermaid@9.3.0.min.js';
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({
                startOnLoad: true,
                logLevel: 5,
                securityLevel: 'loose',
                arrowMarkerAbsolute: true,
                themeVariables: { fontSize: "%spx" }
            });
            try {
                await mermaid.run({
                  querySelector: '.%s',
                });
            }
            catch(err) {
                document.getElementById("mermaidError").innerHTML = err.message;
            }
        
        function adjustIframeHeight(iframe) {
            try {
                var iframeDoc = iframe.contentDocument;
                var mermaidElement = iframeDoc.getElementsByClassName("%s")[0];
        
                if (mermaidElement) {
                    var svgElement = mermaidElement.getElementsByTagName("svg")[0];
                    if (svgElement) {
                        var bbox = svgElement.getBBox();
                        iframe.style.height = (bbox.height + 50) + "px";
                    }
                }
            } catch (e) {
                console.error("Error adjusting iframe height: ", e);
            }
        }
        
        function observeIframe(iframe) {
            var observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    adjustIframeHeight(iframe);
                });
            });
        
            try {
                var config = { attributes: true, childList: true, subtree: true };
                observer.observe(iframe.contentDocument, config);
            } catch (e) {
                console.error("Error observing iframe: ", e);
            }
        }
        
        var iframes = parent.document.getElementsByTagName("iframe");
        for (var i = 0; i < iframes.length; i++) {
            observeIframe(iframes[i]);
        }
        </script>
        """ % (pre_class, format_class_diagram, font_size, pre_class, pre_class)
    )
    return
