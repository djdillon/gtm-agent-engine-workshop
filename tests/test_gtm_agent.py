import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from langchain.tools import ToolRuntime
from langchain_core.messages import AIMessage

from gtm_agent import gtm_agent as agent_module


def make_runtime(metadata):
    return ToolRuntime(
        state={},
        context={},
        config={"metadata": metadata},
        stream_writer=lambda _: None,
        tool_call_id=None,
        store=None,
    )


def test_scoring_request_carries_configured_rep_without_tool_call(monkeypatch):
    captured = {}

    def fake_invoke(input_data, config):
        captured["input"] = input_data
        captured["config"] = config
        return {"messages": [AIMessage(content="scored")]}

    monkeypatch.setattr(agent_module.gtm_agent, "invoke", fake_invoke)

    user_id = agent_module.REP_IDS[0]["rep_id"]
    result = agent_module.run_agent("Score LEAD-12853 for OFFER-10001", user_id=user_id)

    rep = agent_module.data_service.get_rep(user_id)
    assert result["reply"] == "scored"
    assert captured["config"]["metadata"]["rep"] == rep
    assert captured["input"]["messages"][0]["role"] == "system"
    assert rep["name"] in captured["input"]["messages"][0]["content"]
    assert agent_module.get_current_rep.func(
        make_runtime(captured["config"]["metadata"])
    ) == {"rep": rep, "found": True}


def test_email_uses_configured_rep_without_current_rep_tool(monkeypatch):
    user_id = agent_module.REP_IDS[0]["rep_id"]
    rep = agent_module.data_service.get_rep(user_id)
    runtime = make_runtime({"user_id": user_id, "rep": rep})

    def fail_get_rep(_):
        raise AssertionError("email sender should use the resolved rep")

    monkeypatch.setattr(agent_module.data_service, "get_rep", fail_get_rep)

    result = agent_module.send_prospect_email.func(
        {"name": "Prospect", "email": "prospect@example.com"},
        "Hello",
        "Body",
        runtime,
    )

    assert result["from"] == rep["email"]
    assert result["from_name"] == rep["name"]
