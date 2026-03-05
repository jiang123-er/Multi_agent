from util.prompt_loader import load_parse_prompt, load_verify_prompt, load_score_prompt, load_interview_prompt
from util.logger_handler import logger
from model.factory import chat_model
from rag.retriever import RagSummarize
import json
from typing import Dict, Any


def clean_json_response(content: str) -> str:
    content = content.strip()
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end != -1:
        content = content[start:end+1]
    return content


class BaseAgent:
    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        self.model = chat_model
        logger.info(f'[{self.name}] 智能体加载成功')


class ParserAgent(BaseAgent):
    def __init__(self):
        super().__init__("ParserAgent")
        self.prompt = load_parse_prompt()
    
    def run(self, resume_text: str) -> Dict[str, Any]:
        logger.info(f'{self.name} 开始解析简历...')
        prompt = self.prompt.format(resume_text=resume_text)
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            result = json.loads(content)
            logger.info(f'{self.name} 解析完成')
            return result
        except json.JSONDecodeError as e:
            logger.error(f'{self.name} JSON解析失败: {str(e)}')
            return {"error": "parse_failed", "raw_text": content}


class ScoreAgent(BaseAgent):
    def __init__(self):
        super().__init__("ScoreAgent")
        self.prompt_template = load_score_prompt()
    
    def run(self, parser_info: Dict[str, Any], verify_info: Dict[str, Any] = None, job_requirements: str = None) -> Dict[str, Any]:
        if verify_info:
            logger.info(f'{self.name} 开始复评...')
        else:
            logger.info(f'{self.name} 开始初评...')
        
        prompt = self.prompt_template.format(
            resume_json=json.dumps(parser_info, ensure_ascii=False, indent=2),
            job_requirements=job_requirements or "未指定",
            verify_json=json.dumps(verify_info, ensure_ascii=False, indent=2) if verify_info else "无"
        )
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f'{self.name} JSON解析失败: {str(e)}')
            return {"error": "score_failed", "raw_text": content}


class VerifyAgent(BaseAgent):
    def __init__(self):
        super().__init__("VerifyAgent")
        self.prompt_template = load_verify_prompt()
    
    def run(self, parser_info: Dict[str, Any], initial_score: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f'{self.name} 开始验证真实性')
        prompt = self.prompt_template.format(
            resume_json=json.dumps(parser_info, ensure_ascii=False, indent=2),
            initial_score=json.dumps(initial_score, ensure_ascii=False, indent=2)
        )
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f'{self.name} JSON解析失败: {str(e)}')
            return {"error": "verify_failed", "raw_text": content}


class InterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("InterviewAgent")
        self.prompt_template = load_interview_prompt()
        self.rag = RagSummarize()
    
    def run(self, parser_info: Dict[str, Any], verify_info: Dict[str, Any] = None) -> Dict[str, Any]:
        if verify_info:
            verify_issues = json.dumps(verify_info.get("issues", []), ensure_ascii=False, indent=2)
        else:
            verify_issues = "无"
        
        skills_dict = parser_info.get("skills", {})
        all_skills = []
        if isinstance(skills_dict, dict):
            for skill_list in skills_dict.values():
                if isinstance(skill_list, list):
                    all_skills.extend(skill_list)
        query = ", ".join(all_skills) if all_skills else json.dumps(parser_info, ensure_ascii=False)[:300]
        
        context = self.rag.retriever_docs(query)
        if not context:
            context = "无相关参考资料"
            logger.warning(f'{self.name} 未检索到相关参考资料')
        
        prompt = self.prompt_template.format(
            resume_json=json.dumps(parser_info, ensure_ascii=False, indent=2),
            verify_issues=verify_issues,
            context=context
        )
        logger.info(f'{self.name} 生成面试题中（RAG增强）')
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f'{self.name} JSON解析失败: {str(e)}')
            return {"error": "interview_failed", "raw_text": content}
