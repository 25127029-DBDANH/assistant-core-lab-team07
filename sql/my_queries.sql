-- Lab 5 Part F: write your queries for the assistant database here.
-- Q1 requests per intent

-- Q2 average latency per intent

-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)
SELECT i.topic, COUNT(*) AS thumbs_down_count
FROM feedback f
JOIN interaction i ON f.request_id = i.request_id
WHERE f.rating = -1 AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down_count DESC;

-- H2 (Homework): Degradation (fallback) rate and response reliability by intent
SELECT 
    intent,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) AS resolved_count,
    ROUND(100.0 * SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS resolved_rate_pct,
    SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) AS degraded_count,
    ROUND(100.0 * SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS degraded_rate_pct,
    ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY total_requests DESC;

-- H2 Extension: Impact of degraded responses on negative feedback (rating = -1)
SELECT 
    CASE WHEN i.degraded = 1 THEN 'Degraded (Fallback)' ELSE 'Normal' END AS answer_quality,
    COUNT(f.id) AS total_feedback,
    SUM(CASE WHEN f.rating = 1 THEN 1 ELSE 0 END) AS positive_count,
    SUM(CASE WHEN f.rating = -1 THEN 1 ELSE 0 END) AS negative_count,
    ROUND(100.0 * SUM(CASE WHEN f.rating = -1 THEN 1 ELSE 0 END) / COUNT(f.id), 2) AS negative_rate_pct
FROM interaction i
JOIN feedback f ON i.request_id = f.request_id
GROUP BY i.degraded;
