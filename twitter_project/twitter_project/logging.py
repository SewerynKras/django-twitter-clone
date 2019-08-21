from .settings import BASE_DIR
import os
import logging

logger = logging.getLogger(__name__)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'compact': {
            'format': " %(asctime)s | %(levelname)s | %(message)s"
        },
        'complex': {
            'format': " %(asctime)s | %(levelname)s | %(module)s | %(process)d | %(thread)d | %(message)s"
        }
    },
    'handlers': {
        'logfile': {
            'level': logging.DEBUG,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs.log'),
            'maxBytes': 15 * 10**6,
            'backupCount': 5,
            'formatter': 'complex'
        },
        'console': {
            'level': logging.INFO,
            'class': 'logging.StreamHandler',
            'formatter': 'compact'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['logfile', 'console'],
            'propagate': False
        },
        '': {
            'handlers': ['logfile', 'console'],
            'level': logging.DEBUG
        },
    }
}
