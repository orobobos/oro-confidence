# our-confidence

Dimensional confidence system for belief scoring. Part of the [ourochronos](https://github.com/ourochronos) ecosystem.

## Installation

```bash
pip install our-confidence
```

## Usage

```python
from our_confidence import DimensionalConfidence, ConfidenceDimension

# Simple confidence
conf = DimensionalConfidence.simple(0.8)

# Full dimensional confidence
conf = DimensionalConfidence.full(
    source_reliability=0.9,
    method_quality=0.7,
    internal_consistency=0.8,
    temporal_freshness=0.95,
    corroboration=0.6,
    domain_applicability=0.85,
)

# Dimension registry for validation
from our_confidence import get_registry
registry = get_registry()
result = registry.validate("v1.confidence.core", {"source_reliability": 0.8})
```

## Development

```bash
make dev    # Install with dev dependencies
make test   # Run tests
make lint   # Run linters
```
