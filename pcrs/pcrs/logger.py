import logging
from django.utils.timezone import localtime

def log_request(logger, request, message):
	logger.info('[{}:{}:{}] {}'.format(localtime(), request.user, request.META.get('REMOTE_ADDR'), message))