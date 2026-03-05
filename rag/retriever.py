"""
    RAG检索模块
    实现知识检索功能，用于增强面试题生成
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from util.prompt_loader import load_rag_prompt
from model.factory import chat_model, embed_model
from util.file_handler import get_file_md5_hex, logger
from util.file_handler import listdir_with_allowed_type, txt_loader, pdf_loader
from util.path_tool import get_abs_path
from langchain_chroma import Chroma
from util.config_handler import chroma_conf
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


class VectorStore:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf['collection_name'],
            persist_directory=chroma_conf['persist_directory'],
            embedding_function=embed_model
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf['chunk_size'],
            chunk_overlap=chroma_conf['chunk_overlap'],
            separators=chroma_conf['separators'],
            length_function=len
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={'k': chroma_conf['k']})

    def load_document(self):
        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(get_abs_path(chroma_conf['md5_hex_store'])):
                with open(get_abs_path(chroma_conf['md5_hex_store']), 'w', encoding='utf-8') as f:
                    pass
                return False

            with open(get_abs_path(chroma_conf['md5_hex_store']), 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True
                return False

        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(chroma_conf['md5_hex_store']), 'a', encoding='utf-8') as f:
                f.write(md5_for_check + '\n')

        def get_file_document(read_path):
            if read_path.endswith('txt'):
                return txt_loader(read_path)
            if read_path.endswith('pdf'):
                return pdf_loader(read_path)
            return []

        allowed_files_path = listdir_with_allowed_type(
            get_abs_path(chroma_conf['data_path']),
            tuple(chroma_conf['allow_knowledge_file_type'])
        )

        for path in allowed_files_path:
            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                logger.info(f'{path} 已存在，跳过')
                continue

            try:
                documents = get_file_document(path)
                if not documents:
                    logger.info(f'{path} 无有效文本，跳过')
                    continue

                split_document = self.spliter.split_documents(documents)
                if not split_document:
                    logger.warning(f'{path} 分块后没有有效文本，跳过')
                    continue

                self.vector_store.add_documents(split_document)
                save_md5_hex(md5_hex)
                logger.info(f'{path} 加载成功')

            except Exception as e:
                logger.error(f'{path} 加载失败: {str(e)}', exc_info=True)
                continue


class RagSummarize:
    def __init__(self):
        self.vector_store = VectorStore()
        self.model = chat_model
        self.prompt_text = load_rag_prompt()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.load_document = self.vector_store.load_document()
        self.retriever = self.vector_store.get_retriever()
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    def retriever_docs(self, query: str) -> str:
        try:
            docs = self.retriever.invoke(query)
            if not docs:
                logger.warning(f'未找到相关内容')
                return ''
            context = "\n\n---\n\n".join([doc.page_content for doc in docs])
            return context
        except Exception as e:
            logger.error(f'检索失败: {str(e)}', exc_info=True)
            return ''

    def retriever_for_interview(self, resume_text: str) -> str:
        query = resume_text[:300] if len(resume_text) > 300 else resume_text
        return self.retriever_docs(query)

    def summarize(self, query: str) -> str:
        context = self.retriever_docs(query)
        if not context:
            return '未找到相关内容'
        return self.chain.invoke({'input': query, 'context': context})


if __name__ == '__main__':
    rag = RagSummarize()
    print(rag.summarize('生成几道agent方向的面试题'))
