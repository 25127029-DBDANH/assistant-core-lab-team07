-- Lab 5 Part F: write your queries for the assistant database here.
-- F1 requests per intent: count questions grouped by intent in descending order
SELECT intent, COUNT(*) AS requests
FROM interaction
GROUP BY intent
ORDER BY requests DESC;
