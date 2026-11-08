-- Lab 5 Part F: write your queries for the assistant database here.
-- F1 requests per intent: count questions grouped by intent in descending order
SELECT intent, COUNT(*) AS requests
FROM interaction
GROUP BY intent
ORDER BY requests DESC;

-- F2 average latency per intent: compute average response latency rounded to 1 decimal place
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC;
