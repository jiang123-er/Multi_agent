import operator
from typing import TypedDict, Annotated, Dict, Any
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.constants import START, END
from langgraph.types import Send
from core.agents import (
    ParserAgent, ScoreAgent, VerifyAgent, InterviewAgent,
    EducationAgent, SkillMatchAgent, ExperienceAgent, ProjectAgent, OverallAgent
)


class State(TypedDict):
    messages: Annotated[list, operator.add]
    resume_text: str
    job_requirements: str
    parsed_info: Dict[str, Any]
    education_score: Dict[str, Any]
    skill_match_score: Dict[str, Any]
    experience_score: Dict[str, Any]
    project_score: Dict[str, Any]
    overall_score: Dict[str, Any]
    initial_score: Dict[str, Any]
    verify_result: Dict[str, Any]
    final_score: Dict[str, Any]
    interview_questions: str
    is_rescore: bool
    agent_name: str


agents = {
    "education": EducationAgent(),
    "skill_match": SkillMatchAgent(),
    "experience": ExperienceAgent(),
    "project": ProjectAgent(),
    "overall": OverallAgent()
}
parser_agent = ParserAgent()
score_agent = ScoreAgent()
verify_agent = VerifyAgent()
interview_agent = InterviewAgent()


def parser_node(state: State) -> dict:
    return {"parsed_info": parser_agent.run(state["resume_text"])}


def fan_out_scores(state: State) -> list[Send]:
    verify_info = state.get("verify_result") if state.get("is_rescore") else None
    return [
        Send("score_worker", {
            "agent_name": name, 
            "parsed_info": state["parsed_info"],
            "job_requirements": state.get("job_requirements", ""),
            "verify_info": verify_info
        })
        for name in agents.keys()
    ]


def score_worker(state: State) -> dict:
    name = state["agent_name"]
    parsed = state["parsed_info"]
    job_req = state.get("job_requirements", "")
    verify = state.get("verify_info")
    
    if name == "education":
        return {"education_score": agents[name].run(parsed, verify)}
    elif name == "skill_match":
        return {"skill_match_score": agents[name].run(parsed, job_req, verify)}
    elif name == "experience":
        return {"experience_score": agents[name].run(parsed, job_req, verify)}
    elif name == "project":
        return {"project_score": agents[name].run(parsed, job_req, verify)}
    elif name == "overall":
        return {"overall_score": agents[name].run(parsed, verify)}
    return {}


def score_node(state: State) -> dict:
    verify = state.get("verify_result") if state.get("is_rescore") else None
    score = score_agent.run(
        state["education_score"],
        state["skill_match_score"],
        state["experience_score"],
        state["project_score"],
        state["overall_score"],
        verify_info=verify
    )
    return {"final_score": score} if state.get("is_rescore") else {"initial_score": score}


def verify_node(state: State) -> dict:
    return {"verify_result": verify_agent.run(state["parsed_info"], state["initial_score"])}


def routing_after_verify(state: State) -> str:
    result = state.get("verify_result", {})
    if result.get("issues") or result.get("risk_level") != "低":
        return "rescore_fan_out"
    return "interview_node"


def routing_after_aggregate(state: State) -> str:
    if state.get("is_rescore"):
        return "interview_node"
    return "verify_node"


def interview_node(state: State) -> dict:
    return {"interview_questions": interview_agent.run(state["parsed_info"], state.get("verify_result"))}


workflow = StateGraph(State)

workflow.add_node("parser_node", parser_node)
workflow.add_node("score_worker", score_worker)
workflow.add_node("score_node", score_node)
workflow.add_node("verify_node", verify_node)
workflow.add_node("interview_node", interview_node)
workflow.add_node("rescore_fan_out", lambda s: {"is_rescore": True})

workflow.add_edge(START, "parser_node")
workflow.add_conditional_edges("parser_node", fan_out_scores, ["score_worker"])
workflow.add_edge("score_worker", "score_node")
workflow.add_conditional_edges("score_node", routing_after_aggregate, ["verify_node", "interview_node"])
workflow.add_conditional_edges("verify_node", routing_after_verify, ["rescore_fan_out", "interview_node"])
workflow.add_conditional_edges("rescore_fan_out", fan_out_scores, ["score_worker"])
workflow.add_edge("interview_node", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
