# Scrapy settings for danawa_crawler project

BOT_NAME = "danawa_crawler"
SPIDER_MODULES = ["danawa_crawler.spiders"]
NEWSPIDER_MODULE = "danawa_crawler.spiders"

# Concurrent request settings for performance optimization
CONCURRENT_REQUESTS = 16              # Max concurrent requests across all domains
CONCURRENT_REQUESTS_PER_DOMAIN = 8    # Max concurrent requests per domain
DOWNLOAD_DELAY = 0.5                  # Delay between requests (seconds)
RANDOMIZE_DOWNLOAD_DELAY = 0.5        # Random factor for delay (0.5 * 0.3 to 1.5 * 0.3)

# Basic crawler policies
ROBOTSTXT_OBEY = True                 # Respect robots.txt
COOKIES_ENABLED = True                # Enable cookie handling

# HTTP headers to mimic real browser behavior
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
}

# Downloader middleware configuration
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# AutoThrottle extension for intelligent speed control
AUTOTHROTTLE_ENABLED = False

# Retry configuration for handling temporary failures
RETRY_TIMES = 2                                         # Number of retry attempts
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]       # HTTP codes to retry


# System resource settings
DNS_TIMEOUT = 5                      # DNS resolution timeout
DOWNLOAD_TIMEOUT = 15                 # Download timeout per request

# # Logging configuration
# LOG_LEVEL = 'ERROR'                    # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
# LOG_STDOUT = False
# LOG_SHORT_NAMES = True

# Item pipeline configuration (executed in order by priority number)
# Lower numbers = higher priority (executed first)
ITEM_PIPELINES = {
    'danawa_crawler.pipelines.PriceCleaningPipeline': 300,        # Clean price data
    'danawa_crawler.pipelines.NutrientExtractionPipeline': 400,   # Extract individual nutrients
    'danawa_crawler.pipelines.DuplicatesPipeline': 500,  # Remove duplicates
}

EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.corestats.CoreStats': None,
    'scrapy.extensions.logstats.LogStats': None,
    'scrapy.extensions.memusage.MemoryUsage': None,
}

# Memory usage monitoring disabled (small scale)
MEMUSAGE_ENABLED = False

# Feed export settings for output files
FEED_EXPORT_ENCODING = "utf-8"        # Character encoding for output

# Output configuration - JSON format only
# FEEDS = {
#     'nutrition_data.json': {
#         'format': 'json',              # Export format
#         'encoding': 'utf8',            # File encoding
#         'ensure_ascii': False,         # Allow non-ASCII characters (Korean)
#         'indent': 2,                   # Pretty print with 2-space indentation
#         'overwrite': True,             # Overwrite existing file
#     }
# }

DUPEFILTER_DEBUG = False
DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'

TELNETCONSOLE_ENABLED = False
STATS_CLASS = 'scrapy.statscollectors.DummyStatsCollector'

SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

HTTPCACHE_ENABLED = False

REACTOR_THREADPOOL_MAXSIZE = 4
SCRAPER_SLOT_MAX_ACTIVE_SIZE = 100000

LOGSTATS_INTERVAL = 0