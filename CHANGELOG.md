# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial extraction from valence core
- `DimensionalConfidence` class with multi-dimensional belief scoring
- `ConfidenceDimension` enum for core dimension names
- `DimensionRegistry` for schema-based dimension validation
- `DimensionSchema` and `ValidationResult` data classes
- `aggregate_confidence()` for combining multiple confidence scores
- `confidence_label()` for human-readable confidence descriptions
- Built-in schemas: v1.confidence.core, v1.trust.core, v1.trust.extended
