"""
Unit tests for Copernicus Sentinel-5P remote sensing pipeline and plume analyzer.
"""
from pathlib import Path
import pytest
from src.satellite.copernicus_client import (
    CopernicusSentinel5PClient,
    DATA_SOURCE_REAL,
    SatelliteObservation,
)
from src.satellite.plume_analyzer import SatellitePlumeAnalyzer


def test_copernicus_cache_provenance():
    """Verify that cached observations use 100% authentic data source tags."""
    client = CopernicusSentinel5PClient()
    df = client.load_cache(2023)
    if not df.empty:
        assert (df["data_source"] == DATA_SOURCE_REAL).all()
        assert "granule_id" in df.columns
        assert "orbit" in df.columns


def test_plume_analyzer_insufficient_overpasses():
    """Analyzer must report INSUFFICIENT_EVIDENCE when clear-sky observations are below threshold."""
    analyzer = SatellitePlumeAnalyzer(min_valid_overpasses=3)
    # Provide only 1 valid observation
    obs = [
        SatelliteObservation(
            facility_id="TEST_FAC",
            facility_name="Test Plant",
            latitude=50.0,
            longitude=10.0,
            observation_date="2023-06-02",
            observation_time_utc="2023-06-02T11:00:00Z",
            satellite_mission="Sentinel-5P TROPOMI",
            product_type="L2__NO2___",
            tropospheric_column_density_mol_m2=2.5e-5,
            regional_background_mol_m2=2.0e-5,
            background_std_mol_m2=0.5e-5,
            cloud_fraction=0.10,
            quality_flag_qa_value=0.85,
            is_cloud_obscured=False,
            is_valid_qa=True,
            data_source=DATA_SOURCE_REAL,
        )
    ]
    res = analyzer.analyze_facility_plumes(obs, claimed_production_tonnes=1000000.0)
    assert res.is_insufficient_evidence
    assert res.consistency_verdict == "INSUFFICIENT_EVIDENCE"


def test_plume_analyzer_activity_concordance():
    """Sufficient clear-sky observations should compute z-score and evidence confidence."""
    analyzer = SatellitePlumeAnalyzer(min_valid_overpasses=2)
    obs = [
        SatelliteObservation(
            facility_id="TEST_FAC",
            facility_name="Test Plant",
            latitude=50.0,
            longitude=10.0,
            observation_date=f"2023-06-{d:02d}",
            observation_time_utc=f"2023-06-{d:02d}T11:00:00Z",
            satellite_mission="Sentinel-5P TROPOMI",
            product_type="L2__NO2___",
            tropospheric_column_density_mol_m2=3.0e-5,
            regional_background_mol_m2=2.0e-5,
            background_std_mol_m2=0.5e-5,
            cloud_fraction=0.15,
            quality_flag_qa_value=0.90,
            is_cloud_obscured=False,
            is_valid_qa=True,
            data_source=DATA_SOURCE_REAL,
        )
        for d in [2, 15, 25]
    ]
    res = analyzer.analyze_facility_plumes(obs, claimed_production_tonnes=1000000.0)
    assert not res.is_insufficient_evidence
    assert res.valid_clear_sky_overpasses == 3
    assert res.plume_anomaly_zscore == 2.0  # (3.0e-5 - 2.0e-5) / 0.5e-5 = 2.0
    assert res.data_source == DATA_SOURCE_REAL
