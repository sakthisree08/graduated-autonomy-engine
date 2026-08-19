"""
Metrics module - Prometheus metrics for monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from typing import Dict, Any
import time

# Action metrics
action_counter = Counter(
    'actions_total',
    'Total number of actions evaluated',
    ['autonomy_level', 'status']
)

action_duration = Histogram(
    'action_duration_seconds',
    'Time taken to evaluate an action',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# Risk metrics
risk_gauge = Gauge(
    'risk_score',
    'Current risk score distribution',
    ['operation']
)

# Review metrics
review_counter = Counter(
    'reviews_total',
    'Total number of reviews',
    ['decision']
)

# Rate limit metrics
rate_limit_counter = Counter(
    'rate_limit_hits',
    'Number of rate limit hits',
    ['api_key']
)

# Calibration metrics
calibration_gauge = Gauge(
    'calibration_adjustment',
    'Current calibration adjustment',
    ['operation']
)

# System metrics
request_counter = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active sessions'
)


def track_action(autonomy_level: str, status: str):
    """Track an action evaluation"""
    action_counter.labels(autonomy_level=autonomy_level, status=status).inc()


def track_duration(duration: float):
    """Track action evaluation duration"""
    action_duration.observe(duration)


def track_risk(operation: str, risk: int):
    """Track risk score"""
    risk_gauge.labels(operation=operation).set(risk)


def track_review(decision: str):
    """Track a review decision"""
    review_counter.labels(decision=decision).inc()


def track_rate_limit(api_key: str):
    """Track rate limit hit"""
    rate_limit_counter.labels(api_key=api_key[:8] + "...").inc()


def track_calibration(operation: str, adjustment: int):
    """Track calibration adjustment"""
    calibration_gauge.labels(operation=operation).set(adjustment)


def track_request(method: str, endpoint: str, status_code: int):
    """Track HTTP request"""
    request_counter.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()


def get_metrics():
    """Get all metrics"""
    return generate_latest(REGISTRY)