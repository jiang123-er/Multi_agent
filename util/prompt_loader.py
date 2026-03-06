"""
    提示词加载器 - 简历分析专用
    负责加载3个智能体的提示词模板
"""
from util.config_handler import prompts_conf
from util.path_tool import get_abs_path
from util.logger_handler import logger


def _load_prompt_file(prompt_path_key: str, agent_name: str = "Unknown") -> str:
    """
    通用提示词文件加载函数
    
    Args:
        prompt_path_key: 配置文件中的路径键名
        agent_name: 智能体名称（用于日志），可选
    
    Returns:
        提示词文本内容
    """
    try:
        prompt_path = get_abs_path(prompts_conf[prompt_path_key])
    except KeyError:
        logger.error(f'[{agent_name}] 在prompts.yml中未找到 {prompt_path_key} 配置项')
        raise
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            logger.info(f'[{agent_name}] 加载提示词成功: {prompt_path_key}')
            return f.read()
    except Exception as e:
        logger.error(f"[{agent_name}] 加载提示词文件失败：{str(e)}")
        raise


def load_parse_prompt() -> str:
    """加载文档解析智能体提示词"""
    return _load_prompt_file('parse_prompt_path', 'ParserAgent')


def load_score_education_prompt() -> str:
    """加载教育背景评分提示词"""
    return _load_prompt_file('score_education_prompt_path', 'EducationAgent')


def load_score_skill_match_prompt() -> str:
    """加载技能匹配评分提示词"""
    return _load_prompt_file('score_skill_match_prompt_path', 'SkillMatchAgent')


def load_score_experience_prompt() -> str:
    """加载工作经验评分提示词"""
    return _load_prompt_file('score_experience_prompt_path', 'ExperienceAgent')


def load_score_project_prompt() -> str:
    """加载项目质量评分提示词"""
    return _load_prompt_file('score_project_prompt_path', 'ProjectAgent')


def load_score_overall_prompt() -> str:
    """加载整体印象评分提示词"""
    return _load_prompt_file('score_overall_prompt_path', 'OverallAgent')


def load_score_prompt() -> str:
    """加载评分汇总提示词"""
    return _load_prompt_file('score_prompt_path', 'ScoreAgent')


def load_interview_prompt() -> str:
    """加载面试题智能体提示词"""
    return _load_prompt_file('interview_prompt_path', 'InterviewAgent')


def load_verify_prompt() -> str:
    """加载校验智能体提示词"""
    return _load_prompt_file('verify_prompt_path','VerifyAgent')


def load_rag_prompt() -> str:
    return _load_prompt_file('rag_prompt_path','RAG')