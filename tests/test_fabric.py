from mcp_cortex import ContextCell, ContextFabric, Provenance


def test_publish_query_materialize_context_cell():
    fabric = ContextFabric()
    cell = ContextCell(
        id="ctx://repo/demo/build/1",
        schema="demo.build.v1",
        summary="Build failed because import is missing.",
        labels=["code", "untrusted_text"],
        provenance=Provenance(source="capability://sandbox/pytest", actor="agent://debugger"),
        trust_level="verified",
    )

    fabric.publish(cell)

    assert fabric.get(cell.id) is cell
    assert [c.id for c in fabric.query(labels=["code"], text="import")] == [cell.id]

    materialized = fabric.materialize([cell.id])
    assert materialized[0]["summary"] == cell.summary
    assert "payload" not in materialized[0]
