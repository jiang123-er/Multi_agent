import os
from abc import ABC, abstractmethod
from typing import Optional
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.language_models import BaseChatModel
from util.config_handler import rag_conf


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[OllamaEmbeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[OllamaEmbeddings | BaseChatModel]:
        model_type = rag_conf.get('model_type', 'ollama')
        
        if model_type == 'openai':
            api_key = rag_conf.get('api_key') or os.getenv('NVIDIA_API_KEY') or os.getenv('OPENAI_API_KEY')
            return ChatOpenAI(
                model=rag_conf['chat_model_name'],
                api_key=api_key,
                base_url=rag_conf.get('base_url'),
                temperature=rag_conf.get('temperature', 0.3),
            )
        else:
            return ChatOllama(model=rag_conf['chat_model_name'])


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[OllamaEmbeddings | BaseChatModel]:
        model_type = rag_conf.get('model_type', 'ollama')
        
        if model_type == 'openai':
            api_key = rag_conf.get('api_key') or os.getenv('NVIDIA_API_KEY') or os.getenv('OPENAI_API_KEY')
            return OpenAIEmbeddings(
                model=rag_conf.get('embedding_model_name', 'text-embedding-ada-002'),
                api_key=api_key,
                base_url=rag_conf.get('base_url'),
            )
        else:
            return OllamaEmbeddings(model=rag_conf['embedding_model_name'])


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
