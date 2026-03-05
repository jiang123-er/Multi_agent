"""
    文件处理工具库
    提供PDF读取、MD5计算、文件筛选等基础文件操作
    支持LangChain Document格式（用于RAG）
"""
import os
import hashlib
from util.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


def get_file_md5_hex(filepath: str) -> str:
    """
    计算文件的MD5哈希值（十六进制字符串）
    用于文件去重、缓存校验等场景
    
    Args:
        filepath: 文件绝对路径
    
    Returns:
        32位十六进制MD5字符串，失败返回None
    """
    if not os.path.exists(filepath):
        logger.error(f"[MD5计算] 文件不存在: {filepath}")
        return None
    
    if not os.path.isfile(filepath):
        logger.error(f"[MD5计算] 路径不是文件: {filepath}")
        return None
    
    md5_obj = hashlib.md5()
    chunk_size = 4096
    
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        return md5_obj.hexdigest()
    except Exception as e:
        logger.error(f"[MD5计算] 计算失败: {filepath}, 错误: {str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple) -> tuple:
    """
    获取指定文件夹内指定类型的文件列表
    
    Args:
        path: 文件夹路径
        allowed_types: 允许的文件后缀元组，如 ('.pdf', '.txt')
    
    Returns:
        文件路径元组
    """
    files = []
    
    if not os.path.isdir(path):
        logger.error(f"[文件筛选] 路径不是文件夹: {path}")
        return ()
    
    for f in os.listdir(path):
        if f.lower().endswith(allowed_types):
            files.append(os.path.join(path, f))
    
    return tuple(files)


def pdf_loader(filepath: str, password: str = None) -> list:
    """
    使用LangChain加载PDF文件
    
    Args:
        filepath: PDF文件路径
        password: PDF密码（如有）
    
    Returns:
        LangChain Document对象列表
    """
    try:
        return PyPDFLoader(filepath, password=password).load()
    except Exception as e:
        logger.error(f"[PDF加载] 加载失败: {filepath}, 错误: {str(e)}")
        raise


def txt_loader(filepath: str, encoding: str = "utf-8") -> list:
    """
    使用LangChain加载文本文件
    
    Args:
        filepath: 文本文件路径
        encoding: 文件编码，默认utf-8
    
    Returns:
        LangChain Document对象列表
    """
    try:
        return TextLoader(filepath, encoding=encoding).load()
    except Exception as e:
        logger.error(f"[文本加载] 加载失败: {filepath}, 错误: {str(e)}")
        raise


def extract_text_from_pdf(file_obj) -> str:
    """
    从PDF文件对象中提取纯文本（用于简历分析）
    使用PyPDF2直接提取
    
    Args:
        file_obj: 文件对象
    
    Returns:
        提取的文本内容
    """
    import PyPDF2
    
    try:
        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        logger.error(f"[PDF提取] 读取PDF失败: {str(e)}")
        raise
