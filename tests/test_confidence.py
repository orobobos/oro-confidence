"""Tests for DimensionalConfidence."""

import pytest

from our_confidence import (
    DimensionalConfidence,
    aggregate_confidence,
    confidence_label,
)


class TestDimensionalConfidenceInit:
    def test_simple_creation(self) -> None:
        conf = DimensionalConfidence(overall=0.8)
        assert conf.overall == 0.8
        assert conf.dimensions == {}

    def test_with_dimensions(self) -> None:
        conf = DimensionalConfidence(
            overall=0.7,
            source_reliability=0.9,
            method_quality=0.6,
        )
        assert conf.source_reliability == 0.9
        assert conf.method_quality == 0.6

    def test_from_dimensions_dict(self) -> None:
        dims = {"source_reliability": 0.8, "corroboration": 0.6}
        conf = DimensionalConfidence(overall=0.7, dimensions=dims)
        assert conf.source_reliability == 0.8
        assert conf.corroboration == 0.6

    def test_overall_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="overall must be between 0 and 1"):
            DimensionalConfidence(overall=1.5)

    def test_dimension_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            DimensionalConfidence(overall=0.5, source_reliability=2.0)


class TestFactoryMethods:
    def test_simple(self) -> None:
        conf = DimensionalConfidence.simple(0.9)
        assert conf.overall == 0.9
        assert conf.dimensions == {}

    def test_full(self) -> None:
        conf = DimensionalConfidence.full(
            source_reliability=0.8,
            method_quality=0.7,
            internal_consistency=0.9,
            temporal_freshness=0.85,
            corroboration=0.6,
            domain_applicability=0.75,
        )
        assert 0.0 <= conf.overall <= 1.0
        assert conf.source_reliability == 0.8

    def test_from_dimensions(self) -> None:
        dims = {"source_reliability": 0.9, "method_quality": 0.8}
        conf = DimensionalConfidence.from_dimensions(dims)
        assert 0.0 <= conf.overall <= 1.0
        assert conf.source_reliability == 0.9


class TestSerialization:
    def test_to_dict(self) -> None:
        conf = DimensionalConfidence(overall=0.7, source_reliability=0.9)
        d = conf.to_dict()
        assert d["overall"] == 0.7
        assert d["source_reliability"] == 0.9
        assert "schema" not in d  # Default schema not included

    def test_to_dict_with_custom_schema(self) -> None:
        conf = DimensionalConfidence(overall=0.7, schema="custom.v1")
        d = conf.to_dict()
        assert d["schema"] == "custom.v1"

    def test_from_dict_roundtrip(self) -> None:
        original = DimensionalConfidence.full(
            source_reliability=0.8,
            method_quality=0.7,
            internal_consistency=0.9,
            temporal_freshness=0.85,
            corroboration=0.6,
            domain_applicability=0.75,
        )
        d = original.to_dict()
        restored = DimensionalConfidence.from_dict(d)
        assert abs(original.overall - restored.overall) < 0.0001
        assert original.dimensions == restored.dimensions


class TestManipulation:
    def test_with_dimension(self) -> None:
        conf = DimensionalConfidence(overall=0.7, source_reliability=0.5)
        updated = conf.with_dimension("source_reliability", 0.9)
        assert updated.source_reliability == 0.9
        # Original unchanged
        assert conf.source_reliability == 0.5

    def test_decay(self) -> None:
        conf = DimensionalConfidence(overall=0.8, temporal_freshness=1.0)
        decayed = conf.decay(factor=0.9)
        assert decayed.temporal_freshness == pytest.approx(0.9)

    def test_decay_no_temporal(self) -> None:
        conf = DimensionalConfidence(overall=0.8)
        decayed = conf.decay(factor=0.9)
        assert decayed.overall == pytest.approx(0.72)

    def test_boost_corroboration(self) -> None:
        conf = DimensionalConfidence(overall=0.7, corroboration=0.5)
        boosted = conf.boost_corroboration(0.2)
        assert boosted.corroboration == 0.7

    def test_recalculate_overall(self) -> None:
        conf = DimensionalConfidence(
            overall=0.5,
            dimensions={"source_reliability": 0.9, "method_quality": 0.9},
        )
        conf.recalculate_overall()
        assert conf.overall > 0.5


class TestConfidenceLabel:
    def test_labels(self) -> None:
        assert confidence_label(0.95) == "very high"
        assert confidence_label(0.8) == "high"
        assert confidence_label(0.6) == "moderate"
        assert confidence_label(0.3) == "low"
        assert confidence_label(0.1) == "very low"


class TestAggregation:
    def test_empty(self) -> None:
        result = aggregate_confidence([])
        assert result.overall == 0.5

    def test_single(self) -> None:
        conf = DimensionalConfidence.simple(0.8)
        result = aggregate_confidence([conf])
        assert result is conf

    def test_geometric(self) -> None:
        c1 = DimensionalConfidence(overall=0.8, source_reliability=0.9)
        c2 = DimensionalConfidence(overall=0.6, source_reliability=0.7)
        result = aggregate_confidence([c1, c2], method="geometric")
        assert 0.0 <= result.overall <= 1.0
        assert result.source_reliability is not None

    def test_minimum(self) -> None:
        c1 = DimensionalConfidence(overall=0.8, source_reliability=0.9)
        c2 = DimensionalConfidence(overall=0.6, source_reliability=0.7)
        result = aggregate_confidence([c1, c2], method="minimum")
        assert result.overall == 0.6
        assert result.source_reliability == 0.7

    def test_maximum(self) -> None:
        c1 = DimensionalConfidence(overall=0.8, source_reliability=0.5)
        c2 = DimensionalConfidence(overall=0.6, source_reliability=0.9)
        result = aggregate_confidence([c1, c2], method="maximum")
        assert result.overall == 0.8
        assert result.source_reliability == 0.9


class TestEquality:
    def test_equal(self) -> None:
        c1 = DimensionalConfidence(overall=0.7, source_reliability=0.8)
        c2 = DimensionalConfidence(overall=0.7, source_reliability=0.8)
        assert c1 == c2

    def test_not_equal(self) -> None:
        c1 = DimensionalConfidence(overall=0.7)
        c2 = DimensionalConfidence(overall=0.8)
        assert c1 != c2

    def test_not_equal_to_other_type(self) -> None:
        conf = DimensionalConfidence(overall=0.7)
        assert conf != "not a confidence"


class TestSetDimension:
    def test_set_new(self) -> None:
        conf = DimensionalConfidence(overall=0.7)
        conf.set_dimension("custom_dim", 0.5)
        assert conf.has_dimension("custom_dim")
        assert conf.get_dimension("custom_dim") == 0.5

    def test_set_none_removes(self) -> None:
        conf = DimensionalConfidence(overall=0.7, source_reliability=0.8)
        conf.set_dimension("source_reliability", None)
        assert not conf.has_dimension("source_reliability")

    def test_set_out_of_range(self) -> None:
        conf = DimensionalConfidence(overall=0.7)
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            conf.set_dimension("bad", 1.5)
