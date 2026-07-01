import pytest, uvicore

@pytest.mark.asyncio
async def test_dbg(app1):
    app = uvicore.app.http
    print("DBG http type:", type(app), "routes:", len(getattr(app,'routes',[])))
    for r in getattr(app,'routes',[]):
        sub=getattr(r,'app',None)
        print("DBG route", type(r).__name__, getattr(r,'path',''), '->', type(sub).__name__ if sub else None,
              'cap=', callable(getattr(sub,'openapi',None)) and hasattr(sub,'separate_input_output_schemas'))
    assert True
