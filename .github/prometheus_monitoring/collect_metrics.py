#!/usr/bin/env python3
import os
import json
import time
import requests
from datetime import datetime, timedelta

# Environment variables
token = os.environ['GITHUB_TOKEN']
owner = os.environ['REPO_OWNER']
repo = os.environ['REPO_NAME']
workflow_id = os.environ.get('WORKFLOW_ID', '')

# Initialize metrics dictionary
metrics = {
    'workflow_runs_total': 0,
    'workflow_success_total': 0,
    'workflow_failure_total': 0,
    'average_duration_seconds': 0,
    'last_execution_timestamp': 0,
    'commit_count_last_week': 0
}

# Headers for GitHub API
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Get workflow runs
def get_workflow_runs():
    url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows'
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching workflows: {response.status_code} - {response.text}")
        return []
    
    workflows = response.json()['workflows']
    leetcode_workflow = next((w for w in workflows if 'leetcode' in w['name'].lower()), None)
    
    if not leetcode_workflow:
        print("Could not find LeetCode workflow")
        return []
    
    runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{leetcode_workflow['id']}/runs"
    runs_response = requests.get(runs_url, headers=headers)
    
    if runs_response.status_code != 200:
        print(f"Error fetching workflow runs: {runs_response.status_code} - {runs_response.text}")
        return []
    
    return runs_response.json()['workflow_runs']

# Get commit count
def get_commit_count():
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    url = f'https://api.github.com/repos/{owner}/{repo}/commits?since={one_week_ago}'
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching commits: {response.status_code} - {response.text}")
        return 0
    
    return len(response.json())

# Process workflow runs
workflow_runs = get_workflow_runs()

# Count metrics
successful_runs = 0
failed_runs = 0
total_duration = 0
durations_count = 0
latest_timestamp = 0

for run in workflow_runs:
    metrics['workflow_runs_total'] += 1
    
    if run['conclusion'] == 'success':
        metrics['workflow_success_total'] += 1
        successful_runs += 1
    elif run['conclusion'] in ['failure', 'cancelled', 'timed_out']:
        metrics['workflow_failure_total'] += 1
        failed_runs += 1
    
    # Calculate duration if available
    if run['status'] == 'completed' and run['updated_at'] and run['created_at']:
        created = datetime.strptime(run['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        updated = datetime.strptime(run['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        duration = (updated - created).total_seconds()
        total_duration += duration
        durations_count += 1
    
    # Track latest run timestamp
    run_time = datetime.strptime(run['created_at'], '%Y-%m-%dT%H:%M:%SZ').timestamp()
    if run_time > latest_timestamp:
        latest_timestamp = run_time

# Calculate average duration
if durations_count > 0:
    metrics['average_duration_seconds'] = total_duration / durations_count

# Set last execution timestamp
metrics['last_execution_timestamp'] = latest_timestamp

# Get commit count for the last week
metrics['commit_count_last_week'] = get_commit_count()

# Save metrics to file for the next step
with open('github_metrics.json', 'w') as f:
    json.dump(metrics, f)

print("Metrics collection completed successfully")
