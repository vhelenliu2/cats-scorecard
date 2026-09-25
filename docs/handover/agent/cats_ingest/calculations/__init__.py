"""Metric calculation modules. Registry maps calc name -> compute(ctx)."""

from __future__ import annotations

from . import (
    operational_excellence,
    cloud_savings,
    model_velocity,
    experimentation_velocity,
    ads_sota_ml,
    revenue_fte,
    sm_fte,
    shopping_revenue,
)

REGISTRY = {
    "operational_excellence": operational_excellence.compute,
    "cloud_savings": cloud_savings.compute,
    "model_velocity": model_velocity.compute,
    "experimentation_velocity": experimentation_velocity.compute,
    "ads_sota_ml": ads_sota_ml.compute,
    "revenue_fte": revenue_fte.compute,
    "sm_fte": sm_fte.compute,
    "shopping_revenue": shopping_revenue.compute,
}
