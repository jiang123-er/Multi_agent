from util.logger_handler import logger
from model.factory import chat_model
from rag.retriever import RagSummarize
import json
from typing import Dict, Any
from util.prompt_loader import (
    load_parse_prompt, 
    load_verify_prompt, 
    load_score_prompt, 
    load_interview_prompt,
    load_score_education_prompt,
    load_score_skill_match_prompt,
    load_score_experience_prompt,
    load_score_project_prompt,
    load_score_overall_prompt
)

def clean_json_response(content: str) -> str:
    content = content.strip()
    if not content:
        return "{}"
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
        self.prompt_template = load_parse_prompt()
    
    def run(self, resume_text: str) -> Dict[str, Any]:
        logger.info(f'[{self.name}] 开始解析简历...')
        prompt = self.prompt_template.format(resume_text=resume_text)
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            result = json.loads(content)
            logger.info(f'[{self.name}] 解析完成')
            return result
        except json.JSONDecodeError as e:
            logger.error(f'[{self.name}] JSON解析失败: {str(e)}')
            return {"error": "parse_failed", "raw_text": content}


class EducationAgent(BaseAgent):
    def __init__(self):
        super().__init__("EducationAgent")
        self.prompt_template = load_score_education_prompt()

    def run(self, parser_info: Dict[str, Any], verify_info: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f'[{self.name}] 开始分析教育背景')
        verify_issues = ""
        if verify_info:
            verify_issues = f"验证问题：\n{json.dumps(verify_info.get('issues', []), ensure_ascii=False, indent=2)}"
        prompt = self.prompt_template.format(
            resume_json=json.dumps(parser_info, ensure_ascii=False, indent=2),
            verify_issues=verify_issues
        )
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            result = json.loads(content)
            if "error" not in result:
                logger.info(f'[{self.name}] 解析完成')
            return result
        except json.JSONDecodeError as e:
            logger.error(f'[{self.name}] JSON解析失败: {str(e)}')
            logger.error(f'[{self.name}] 原始内容: {content[:500]}')
            return {"score": 0, "reason": "解析失败", "error": "education_failed"}


class SkillMatchAgent(BaseAgent):
    def __init__(self):
        super().__init__("SkillMatchAgent")
        self.prompt_template = load_score_skill_match_prompt()

    def run(self, parser_info: Dict[str, Any], job_requirements: str = "", verify_info: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f'[{self.name}] 开始分析技能匹配')
        verify_issues = ""
        if verify_info:
            verify_issues = f"验证问题：\n{json.dumps(verify_info.get('issues', []), ensure_ascii=False, indent=2)}"
        prompt = self.prompt_template.format(
            resume_json=json.dumps(parser_info, ensure_ascii=False, indent=2),
            job_requirements=job_requirements or "无",
            verify_issues=verify_issues
        )
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            result = json.loads(content)
            if "error" not in result:
                logger.info(f'[{self.name}] 解析完成')
            return result
        except json.JSONDecodeError as e:
            logger.error(f'[{self.name}] JSON解析失败: {str(e)}')
            logger.error(f'[{self.name}] 原始内容: {content[:500]}')
            return {"score": 0, "reason": "解析失败", "error": "skillmatch_failed"}


class ExperienceAgent(BaseAgent):
    def __init__(self):
        super().__init__("ExperienceAgent")
        self.prompt_template = load_score_experience_prompt()

    def run(self, parser_info: Dict[str, Any], job_requirements: str = "", verify_info: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f'[{self.name}] 开始分析工作经验')
        verify_issues = ""
        if verify_info:
            verify_issues = f"验证问题：\n{json.dumps(verify_info.get('issues', []), ensure_ascii=False, indent=2)}"
        prompt = self.prompt_template.format(
            resume_json=json.dumps(parser_info, ensure_ascii=False, indent=2),
            job_requirements=job_requirements or "无",
            verify_issues=verify_issues
        )
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            result = json.loads(content)
            if "error" not in result:
                logger.info(f'[{self.name}] 解析完成')
            return result
        except json.JSONDecodeError as e:
            logger.error(f'[{self.name}] JSON解析失败: {str(e)}')
            logger.error(f'[{self.name}] 原始内容: {content[:500]}')
            return {"score": 0, "reason": "解析失败", "error": "experience_failed"}


class ProjectAgent(BaseAgent):
    def __init__(self):
        super().__init__("ProjectAgent")
        self.prompt_template = load_score_project_prompt()

    def run(self, parser_info: Dict[str, Any], job_requirements: str = "", verify_info: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f'[{self.name}] 开始分析项目经验')
        verify_issues = ""
        if verify_info:
            verify_issues = f"验证问题：\n{json.dumps(verify_info.get('issues', []), ensure_ascii=False, indent=2)}"
        prompt = self.prompt_template.format(
            resume_json=json.dumps(parser_info, ensure_ascii=False, indent=2),
            job_requirements=job_requirements or "无",
            verify_issues=verify_issues
        )
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            result = json.loads(content)
            if "error" not in result:
                logger.info(f'[{self.name}] 解析完成')
            return result
        except json.JSONDecodeError as e:
            logger.error(f'[{self.name}] JSON解析失败: {str(e)}')
            logger.error(f'[{self.name}] 原始内容: {content[:500]}')
            return {"score": 0, "reason": "解析失败", "error": "project_failed"}


class OverallAgent(BaseAgent):
    def __init__(self):
        super().__init__("OverallAgent")
        self.prompt_template = load_score_overall_prompt()

    def run(self, parser_info: Dict[str, Any], verify_info: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f'[{self.name}] 开始整体评估')
        verify_issues = ""
        if verify_info:
            verify_issues = f"验证问题：\n{json.dumps(verify_info.get('issues', []), ensure_ascii=False, indent=2)}"
        prompt = self.prompt_template.format(
            resume_json=json.dumps(parser_info, ensure_ascii=False, indent=2),
            verify_issues=verify_issues
        )
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            result = json.loads(content)
            if "error" not in result:
                logger.info(f'[{self.name}] 解析完成')
            return result
        except json.JSONDecodeError as e:
            logger.error(f'[{self.name}] JSON解析失败: {str(e)}')
            logger.error(f'[{self.name}] 原始内容: {content[:500]}')
            return {"score": 0, "reason": "解析失败", "error": "overall_failed"}


class ScoreAgent(BaseAgent):
    def __init__(self):
        super().__init__("ScoreAgent")
        self.prompt_template = load_score_prompt()
    
    def run(self, 
        education_score: Dict,      
        skill_match_score: Dict,    
        experience_score: Dict,     
        project_score: Dict,        
        overall_score: Dict,        
        verify_info: Dict = None     
    ):
        if verify_info:
            logger.info(f'[{self.name}] 开始复评汇总...')
        else:
            logger.info(f'[{self.name}] 开始初评汇总...')
        prompt = self.prompt_template.format(
            education_score=json.dumps(education_score, ensure_ascii=False, indent=2),
            skill_match_score=json.dumps(skill_match_score, ensure_ascii=False, indent=2),
            experience_score=json.dumps(experience_score, ensure_ascii=False, indent=2),
            project_score=json.dumps(project_score, ensure_ascii=False, indent=2),
            overall_score=json.dumps(overall_score, ensure_ascii=False, indent=2),
            verify_info=json.dumps(verify_info, ensure_ascii=False, indent=2) if verify_info else "无"
        )
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            result = json.loads(content)
            logger.info(f"[{self.name}] 汇总完成")
            return result
        except json.JSONDecodeError as e:
            logger.error(f'[{self.name}] JSON解析失败: {str(e)}')
            return {"error": "score_failed", "raw_text": content}


class VerifyAgent(BaseAgent):
    def __init__(self):
        super().__init__("VerifyAgent")
        self.prompt_template = load_verify_prompt()
    
    def run(self, parser_info: Dict[str, Any], initial_score: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f'[{self.name}] 开始验证真实性')
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
            logger.error(f'[{self.name}] JSON解析失败: {str(e)}')
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
                    all_skills.extend([str(s) for s in skill_list])
                elif isinstance(skill_list, str):
                    all_skills.append(skill_list)
        elif isinstance(skills_dict, list):
            all_skills = [str(s) for s in skills_dict]
        
        query = ", ".join(all_skills) if all_skills else str(parser_info)[:300]
        
        context = self.rag.retriever_docs(query)
        if not context:
            context = "无相关参考资料"
            logger.warning(f'[{self.name}] 未检索到相关参考资料')
        
        prompt = self.prompt_template.format(
            resume_json=json.dumps(parser_info, ensure_ascii=False, indent=2),
            verify_issues=verify_issues,
            context=context
        )
        logger.info(f'[{self.name}] 生成面试题中（RAG增强）')
        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        try:
            content = clean_json_response(content)
            result = json.loads(content)
            if "error" not in result:
                logger.info(f'[{self.name}] 面试题生成完成')
            return result
        except json.JSONDecodeError as e:
            logger.error(f'[{self.name}] JSON解析失败: {str(e)}')
            logger.error(f'[{self.name}] 原始内容: {content[:500]}')
            return {
                "error": "interview_failed",
                "technical_questions": [],
                "project_questions": [],
                "behavioral_questions": [],
                "verification_questions": [],
                "interview_tips": ["面试题生成失败，请手动准备面试问题"]
            }

