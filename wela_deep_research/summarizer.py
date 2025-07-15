
import json
import logging
import html2text

from readability import Document
from playwright.sync_api import sync_playwright

from wela_agents.schema.template.openai_chat import ChatTemplate
from wela_agents.schema.template.openai_chat import UserMessageTemplate
from wela_agents.schema.template.prompt_template import StringPromptTemplate

from wela_deep_research.prompt import summarization_instructions
from wela_deep_research.adapter import Adapter

def split_text_by_paragraphs(text, max_chars=16000):
    # 分割段落并过滤空行
    paragraphs = []
    current_para = []
    
    for line in text.splitlines():
        # 跳过空行
        if not line.strip():
            continue
            
        # 非空行加入当前段落
        current_para.append(line)
        
        # 如果行以句号结束或长度超过50字符，视为段落结束
        if line.strip().endswith(('。', '!', '?', '.', '！', '？')) or len(line) > 50:
            if current_para:
                # 将段落内的多行连接为单个字符串
                paragraphs.append('\n'.join(current_para))
                current_para = []
    
    # 处理最后一个未结束的段落
    if current_para:
        paragraphs.append('\n'.join(current_para))
    
    # 如果没有检测到段落，则按每行处理
    if not paragraphs:
        paragraphs = [line for line in text.splitlines() if line.strip()]
    
    # 分组段落并连接为字符串
    result = []
    current_group = []
    current_count = 0

    for para in paragraphs:
        para_length = len(para)
        
        # 处理超长段落（单独成组）
        if para_length > max_chars:
            if current_group:
                result.append('\n'.join(current_group))
                current_group = []
                current_count = 0
            result.append(para)
            continue
        
        # 检查添加后是否超限
        if current_count + para_length <= max_chars:
            current_group.append(para)
            current_count += para_length
        else:
            if current_group:
                result.append('\n'.join(current_group))
            current_group = [para]
            current_count = para_length
    
    # 添加最后一组
    if current_group:
        result.append('\n'.join(current_group))
    
    return result

class Summarizer(Adapter):

    def __init__(self, *, model, state, proxy: str, input_key, output_key):
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    UserMessageTemplate(
                        StringPromptTemplate(summarization_instructions)
                    )
                ]
            ),
            state=state,
            input_key=input_key,
            output_key=output_key
        )
        self.__proxy = proxy
        self.__headless = True
        self.__converter = html2text.HTML2Text()
        self.__converter.ignore_links = False
        self.__converter.ignore_images = False
        self.__converter.body_width = 0

    def __fetch_html_with_playwright(self, url: str) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.__headless,
                args=["--start-maximized"],
                proxy={
                    "server": self.__proxy
                } if self.__proxy else None
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 800}
            )
            page = context.new_page()

            # 绕过 navigator.webdriver 检测
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            content = page.content()
            browser.close()
            return content

    def __extract_main_content(self, html: str) -> str:
        try:
            doc = Document(html)
            return doc.summary()
        except Exception:
            return html

    def __convert_to_markdown(self, html: str) -> str:
        return self.__converter.handle(html)

    def predict(self, **kwargs):
        search_results = self.state["search_results"]

        for search_result in search_results:
            url = search_result["link"]
            logging.info(f"> Reading page: {url}")
            try:
                html_content = self.__fetch_html_with_playwright(url)
                main_content = self.__extract_main_content(html_content)
                markdown_content = self.__convert_to_markdown(main_content).strip()

                if markdown_content:
                    paragraphs = split_text_by_paragraphs(markdown_content)
                    for idx, paragraph in enumerate(paragraphs):
                        logging.info(f"> Reading paragraph {idx+1} in {url}")
                        response = super().predict(webpage_content=paragraph)["content"]
                        web_summary = json.loads(response.lstrip("```json").rstrip("```"))
                        if "summary" not in search_result:
                            search_result.update(web_summary)
                        else:
                            search_result["summary"] += "\n" + web_summary["summary"]
                            search_result["key_excerpts"].extend(web_summary["key_excerpts"])
                    logging.info(f"> Successfully read page: {url}")
                else:
                    logging.error(f"> Get empty main content for: {url}")
            except Exception as e:
                logging.error(f"Failed to read page {url}: {e}")
