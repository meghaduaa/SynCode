const express = require('express');
const client = require('prom-client');
const axios = require('axios');

// Create an express app
const app = express();
const port = 9798; // Port for Prometheus to scrape metrics from

// Create a custom Prometheus metric
const leetcodeSyncDuration = new client.Gauge({
  name: 'leetcode_sync_duration_seconds',
  help: 'Duration of LeetCode Sync',
});

// Expose the metrics on the /metrics endpoint
app.get('/metrics', async (req, res) => {
  try {
    // Example of a metric update (you could modify this as per your needs)
    leetcodeSyncDuration.set(Math.random() * 10); // Random value, replace with actual sync duration
    res.set('Content-Type', client.register.contentType);
    res.end(await client.register.metrics());
  } catch (error) {
    res.status(500).send(error.toString());
  }
});

app.listen(port, () => {
  console.log(`Metrics server listening at http://localhost:${port}`);
});
