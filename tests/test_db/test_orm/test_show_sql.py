import pytest
@pytest.mark.asyncio
async def test_show_sql(app1):
    from app1.models.depot import Depot
    sql = Depot.query().include('slots').sql()
    print("\n--- SLOTS SECONDARY SQL ---\n" + sql['slots'] + "\n")
    from app1.models.slot import Slot
    sql2 = Slot.query().include('depot').sql()
    print("--- DEPOT (BelongsTo) MAIN SQL ---\n" + sql2['main'] + "\n")
