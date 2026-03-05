"""
    配置文件处理器
    支持 YAML 格式配置文件的读取
    包含：RAG配置、ChromaDB配置、提示词配置、智能体配置
"""
import yaml
from util.path_tool import get_abs_path


def load_config(config_path: str, encoding: str = "utf-8") -> dict:
    """
    通用配置读取函数
    
    Args:
        config_path: 配置文件相对路径
        encoding: 文件编码，默认utf-8
    
    Returns:
        配置字典
    """
    abs_path = get_abs_path(config_path)
    with open(abs_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_rag_config(config_path: str = "config/rag.yml", encoding: str = "utf-8") -> dict:
    """读取RAG配置（检索参数、分片设置等）"""
    return load_config(config_path, encoding)


def load_chroma_config(config_path: str = "config/chroma.yml", encoding: str = "utf-8") -> dict:
    """读取ChromaDB配置（向量数据库连接参数）"""
    return load_config(config_path, encoding)


def load_prompts_config(config_path: str = "config/prompts.yml", encoding: str = "utf-8") -> dict:
    """读取提示词配置（提示词文件路径等）"""
    return load_config(config_path, encoding)


# 预加载配置实例（方便直接导入使用）
rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
prompts_conf = load_prompts_config()
