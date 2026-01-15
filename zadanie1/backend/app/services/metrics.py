from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "Request latency", ["path"])
NEWS_CREATED = Counter("news_created_total", "Total news created")
USERS_CREATED = Counter("users_created_total", "Total users created")
NOTIFICATIONS_SENT = Counter("notifications_sent_total", "Total notifications sent")
