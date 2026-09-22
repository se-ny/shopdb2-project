from typing import Any, Optional, TypedDict

from langgraph.graph import StateGraph, END

from app.services import sql_agent_service as svc


class SqlAgentState(TypedDict, total=False):
    question: str
    provider_code: str
    generated_sql: str
    execution_status: str  # SUCCESS | BLOCKED | ERROR
    error_message: Optional[str]
    columns: list[str]
    rows: list[dict[str, Any]]
    result_summary: str


def _node_generate_sql(state: SqlAgentState) -> SqlAgentState:
    state["generated_sql"] = svc.generate_sql(state["question"], state["provider_code"])
    return state


def _node_validate_sql(state: SqlAgentState) -> SqlAgentState:
    ok, cleaned_or_error = svc.validate_sql(state["generated_sql"])
    if ok:
        state["generated_sql"] = cleaned_or_error
        state["execution_status"] = "PENDING"
    else:
        state["execution_status"] = "BLOCKED"
        state["error_message"] = cleaned_or_error
    return state


def _node_execute_sql(state: SqlAgentState) -> SqlAgentState:
    try:
        columns, rows = svc.execute_readonly_sql(state["generated_sql"])
        state["columns"] = columns
        state["rows"] = rows
        state["execution_status"] = "SUCCESS"
    except Exception as exc:
        state["execution_status"] = "ERROR"
        state["error_message"] = str(exc)
    return state


def _node_summarize(state: SqlAgentState) -> SqlAgentState:
    if state["execution_status"] == "SUCCESS":
        state["result_summary"] = svc.summarize_result(
            state["question"], state.get("rows", []), state["provider_code"]
        )
    elif state["execution_status"] == "BLOCKED":
        state["result_summary"] = f"허용되지 않은 쿼리라 실행하지 않았습니다: {state.get('error_message')}"
    else:
        state["result_summary"] = f"쿼리 실행 중 오류가 발생했습니다: {state.get('error_message')}"
    return state


def _route_after_validate(state: SqlAgentState) -> str:
    return "summarize" if state["execution_status"] == "BLOCKED" else "execute"


def build_graph():
    graph = StateGraph(SqlAgentState)
    graph.add_node("generate_sql", _node_generate_sql)
    graph.add_node("validate_sql", _node_validate_sql)
    graph.add_node("execute_sql", _node_execute_sql)
    graph.add_node("summarize", _node_summarize)

    graph.set_entry_point("generate_sql")
    graph.add_edge("generate_sql", "validate_sql")
    graph.add_conditional_edges(
        "validate_sql",
        _route_after_validate,
        {"execute": "execute_sql", "summarize": "summarize"},
    )
    graph.add_edge("execute_sql", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


sql_agent_app = build_graph()