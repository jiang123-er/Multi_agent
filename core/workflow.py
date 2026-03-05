import operator
from typing import TypedDict, Annotated, Dict, Any
from core.agents import ParserAgent, ScoreAgent, VerifyAgent, InterviewAgent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.constants import START, END


class State(TypedDict):
    messages: Annotated[list, operator.add]
    resume_text: str
    job_requirements: str
    parsed_info: Dict[str, Any]
    initial_score: Dict[str, Any]
    verify_result: Dict[str, Any]
    final_score: Dict[str, Any]
    interview_questions: str


parser_agent = ParserAgent()
score_agent = ScoreAgent()
verify_agent = VerifyAgent()
interview_agent = InterviewAgent()


def parser_node(state: State) -> dict:
    parsed = parser_agent.run(state["resume_text"])
    return {"parsed_info": parsed}


def score_node(state: State) -> dict:
    score = score_agent.run(
        state["parsed_info"],
        job_requirements=state.get("job_requirements")
    )
    return {"initial_score": score}


def verify_node(state: State) -> dict:
    result = verify_agent.run(state["parsed_info"], state["initial_score"])
    return {"verify_result": result}


def rescore_node(state: State) -> dict:
    score = score_agent.run(
        state["parsed_info"],
        verify_info=state["verify_result"],
        job_requirements=state.get("job_requirements")
    )
    return {"final_score": score}


def interview_node(state: State) -> dict:
    questions = interview_agent.run(state["parsed_info"], state.get("verify_result"))
    return {"interview_questions": questions}


def routing_func(state: State) -> str:
    verify_result = state.get("verify_result", {})
    # 如果有任何问题或风险等级不是"低"，都进行复评
    issues = verify_result.get("issues", [])
    risk_level = verify_result.get("risk_level", "低")
    
    if not issues and risk_level == "低":
        return "interview_node"
    else:
        return "rescore_node"


workflow = StateGraph(State)
workflow.add_node("parser_node", parser_node)
workflow.add_node("score_node", score_node)
workflow.add_node("verify_node", verify_node)
workflow.add_node("rescore_node", rescore_node)
workflow.add_node("interview_node", interview_node)

workflow.add_edge(START, "parser_node")
workflow.add_edge("parser_node", "score_node")
workflow.add_edge("score_node", "verify_node")
workflow.add_conditional_edges("verify_node", routing_func, ["rescore_node", "interview_node"])
workflow.add_edge("rescore_node", "interview_node")
workflow.add_edge("interview_node", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
