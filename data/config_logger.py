config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'file_format': {
            'format': u'{asctime} - {name} - {levelname} - {filename}:{module}:{lineno} - {message}',
            'style': '{'
        }
    },
    'handlers': {
        'access_handler': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'file_format',
            'filename': 'log/access_and_error.log',
            'mode': 'a'
        },
        'error_handler': {
            'class': 'logging.FileHandler',
            'level': 'WARNING',
            'formatter': 'file_format',
            'filename': 'log/error.log',
            'mode': 'a'
        }
    },
    'loggers': {
        'file_logger': {
            'level': 'INFO',
            'handlers': [
                'access_handler',
                'error_handler'
            ]
        }
    }
}
