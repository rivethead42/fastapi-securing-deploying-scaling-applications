"""
Prometheus metrics configuration
"""
from prometheus_client import Counter, Histogram, Gauge, Summary
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
)

# Database metrics
DB_QUERY_COUNT = Counter(
    'db_query_total', 
    'Total number of database queries',
    ['operation', 'collection']
)

DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds', 
    'Database query latency in seconds',
    ['operation', 'collection'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, float('inf'))
)

# Cache metrics
CACHE_HIT_COUNT = Counter(
    'cache_hit_total', 
    'Total number of cache hits',
    ['key_prefix']
)

CACHE_MISS_COUNT = Counter(
    'cache_miss_total', 
    'Total number of cache misses',
    ['key_prefix']
)

CACHE_OPERATION_LATENCY = Histogram(
    'cache_operation_duration_seconds', 
    'Cache operation latency in seconds',
    ['operation'],
    buckets=(0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, float('inf'))
)

# System metrics
ACTIVE_REQUESTS = Gauge(
    'http_requests_active', 
    'Number of currently active HTTP requests'
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes', 
    'Memory usage in bytes'
)

# Custom business metrics for widgets
WIDGET_OPERATION_COUNT = Counter(
    'widget_operation_total', 
    'Total number of widget operations',
    ['operation']
)

# Functions to record metrics

def record_request_metrics(method, endpoint, status_code, duration):
    """Record metrics for an HTTP request"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

def record_db_metrics(operation, collection, duration):
    """Record metrics for a database operation"""
    DB_QUERY_COUNT.labels(operation=operation, collection=collection).inc()
    DB_QUERY_LATENCY.labels(operation=operation, collection=collection).observe(duration)

def record_cache_hit(key_prefix):
    """Record a cache hit"""
    CACHE_HIT_COUNT.labels(key_prefix=key_prefix).inc()

def record_cache_miss(key_prefix):
    """Record a cache miss"""
    CACHE_MISS_COUNT.labels(key_prefix=key_prefix).inc()

def record_cache_operation(operation, duration):
    """Record metrics for a cache operation"""
    CACHE_OPERATION_LATENCY.labels(operation=operation).observe(duration)

def record_widget_operation(operation):
    """Record a widget operation"""
    WIDGET_OPERATION_COUNT.labels(operation=operation).inc()