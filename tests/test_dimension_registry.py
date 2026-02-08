"""Tests for DimensionRegistry."""

import pytest

from oro_confidence import (
    DimensionRegistry,
    DimensionSchema,
    get_registry,
)


class TestDimensionSchema:
    def test_create(self) -> None:
        schema = DimensionSchema(
            name="test.v1",
            dimensions=["a", "b"],
            required=["a"],
        )
        assert schema.name == "test.v1"
        assert schema.dimensions == ["a", "b"]

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            DimensionSchema(name="")

    def test_bad_range_raises(self) -> None:
        with pytest.raises(ValueError, match="must be less than"):
            DimensionSchema(name="test", value_range=(1.0, 0.0))

    def test_required_not_in_dimensions_raises(self) -> None:
        with pytest.raises(ValueError, match="not in dimensions"):
            DimensionSchema(name="test", dimensions=["a"], required=["b"])


class TestDimensionRegistry:
    def test_register_and_get(self) -> None:
        reg = DimensionRegistry()
        schema = DimensionSchema(name="test.v1", dimensions=["a"])
        reg.register(schema)
        assert reg.get("test.v1") is schema

    def test_get_missing(self) -> None:
        reg = DimensionRegistry()
        assert reg.get("missing") is None

    def test_unregister(self) -> None:
        reg = DimensionRegistry()
        schema = DimensionSchema(name="test.v1", dimensions=["a"])
        reg.register(schema)
        assert reg.unregister("test.v1") is True
        assert reg.get("test.v1") is None
        assert reg.unregister("test.v1") is False

    def test_list_schemas(self) -> None:
        reg = DimensionRegistry()
        reg.register(DimensionSchema(name="b", dimensions=["x"]))
        reg.register(DimensionSchema(name="a", dimensions=["x"]))
        schemas = reg.list_schemas()
        assert [s.name for s in schemas] == ["a", "b"]


class TestValidation:
    def test_valid(self) -> None:
        reg = DimensionRegistry()
        reg.register(DimensionSchema(name="test", dimensions=["a", "b"], required=["a"]))
        result = reg.validate("test", {"a": 0.5, "b": 0.8})
        assert result.valid
        assert result.errors == []

    def test_missing_required(self) -> None:
        reg = DimensionRegistry()
        reg.register(DimensionSchema(name="test", dimensions=["a", "b"], required=["a"]))
        result = reg.validate("test", {"b": 0.5})
        assert not result.valid
        assert any("Missing required" in e for e in result.errors)

    def test_out_of_range(self) -> None:
        reg = DimensionRegistry()
        reg.register(DimensionSchema(name="test", dimensions=["a"]))
        result = reg.validate("test", {"a": 1.5})
        assert not result.valid
        assert any("out of range" in e for e in result.errors)

    def test_unknown_dimension(self) -> None:
        reg = DimensionRegistry()
        reg.register(DimensionSchema(name="test", dimensions=["a"]))
        result = reg.validate("test", {"a": 0.5, "unknown": 0.5})
        assert not result.valid
        assert any("Unknown dimension" in e for e in result.errors)

    def test_unknown_schema(self) -> None:
        reg = DimensionRegistry()
        result = reg.validate("missing", {"a": 0.5})
        assert not result.valid


class TestInheritance:
    def test_resolve(self) -> None:
        reg = DimensionRegistry()
        reg.register(DimensionSchema(name="parent", dimensions=["a", "b"], required=["a"]))
        reg.register(DimensionSchema(name="child", dimensions=["c"], inherits="parent"))
        resolved = reg.resolve("child")
        assert set(resolved.dimensions) == {"a", "b", "c"}
        assert "a" in resolved.required

    def test_resolve_no_parent(self) -> None:
        reg = DimensionRegistry()
        reg.register(DimensionSchema(name="standalone", dimensions=["x"]))
        resolved = reg.resolve("standalone")
        assert resolved.dimensions == ["x"]

    def test_circular_inheritance(self) -> None:
        reg = DimensionRegistry()
        reg.register(DimensionSchema(name="a", dimensions=["x"]))
        reg.register(DimensionSchema(name="b", dimensions=["y"], inherits="a"))
        # Manually create circular reference
        reg._schemas["a"] = DimensionSchema(name="a", dimensions=["x"], inherits="b")
        with pytest.raises(ValueError, match="Circular"):
            reg.resolve("a")

    def test_missing_parent_on_register(self) -> None:
        reg = DimensionRegistry()
        with pytest.raises(ValueError, match="not registered"):
            reg.register(DimensionSchema(name="child", dimensions=["x"], inherits="missing"))


class TestGlobalRegistry:
    def test_has_builtin_schemas(self) -> None:
        registry = get_registry()
        assert registry.get("v1.confidence.core") is not None
        assert registry.get("v1.trust.core") is not None
        assert registry.get("v1.trust.extended") is not None

    def test_core_schema_dimensions(self) -> None:
        registry = get_registry()
        core = registry.get("v1.confidence.core")
        assert core is not None
        assert "source_reliability" in core.dimensions
        assert "corroboration" in core.dimensions
        assert len(core.dimensions) == 6

    def test_extended_trust_inherits(self) -> None:
        registry = get_registry()
        resolved = registry.resolve("v1.trust.extended")
        # Should have both parent and child dimensions
        assert "conclusions" in resolved.dimensions
        assert "honesty" in resolved.dimensions
