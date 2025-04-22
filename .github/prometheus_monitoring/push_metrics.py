#!/usr/bin/env python3
import os
import json
import time
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Load metrics from previous step
with open('github_metrics.json', 'r') as f:
    metrics = json.load(f)

# Set up registry and metrics
registry = CollectorRegistry()

# Define metrics
workflow_runs = Gauge('leetcode_sync_workflow_runs_total', 
                     'Total number of workflow runs', 
                     registry=registry)

workflow_success = Gauge('leetcode_sync_workflow_success_total', 
                        'Number of successful workflow runs', 
                        registry=registry)

workflow_failure = Gauge('leetcode_sync_workflow_failure_total', 
                        'Number of failed workflow runs', 
                        registry=registry)

avg_duration = Gauge('leetcode_sync_average_duration_seconds', 
                    'Average duration of workflow runs in seconds', 
                    registry=registry)

last_execution = Gauge('leetcode_sync_last_execution_timestamp', 
                      'Timestamp of last workflow execution', 
                      registry=registry)

commits_last_week = Gauge('leetcode_sync_commit_count_last_week', 
                         'Number of commits in the last week', 
                         registry=registry)

# Set metric values
workflow_runs.set(metrics['workflow_runs_total'])
workflow_success.set(metrics['workflow_success_total'])
workflow_failure.set(metrics['workflow_failure_total'])
avg_duration.set(metrics['average_duration_seconds'])
last_execution.set(metrics['last_execution_timestamp'])
commits_last_week.set(metrics['commit_count_last_week'])

# Push to gateway
pushgateway_url = os.environ.get('PUSHGATEWAY_URL')
if not pushgateway_url:
    print("Error: PUSHGATEWAY_URL environment variable not set")
    exit(1)

try:
    push_to_gateway(pushgateway_url, job='leetcode_sync_metrics', registry=registry)
    print(f"Successfully pushed metrics to {pushgateway_url}")
except Exception as e:
    print(f"Error pushing metrics to Pushgateway: {e}")
    exit(1)
