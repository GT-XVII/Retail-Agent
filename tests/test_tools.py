from app.tools import retail_tools


def test_retail_tools_have_names_and_descriptions():
    for langchain_tool in retail_tools:
        assert langchain_tool.name
        assert langchain_tool.description
