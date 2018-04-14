import os, logging, sys
import logging.handlers
from logging import raiseExceptions, Logger

LOG_PATH = os.getcwd()+'/logging'

class AppLogger(Logger):
	"""
	自定义logger
	如果handler名称为console表示在终端打印所有大于等于设置级别的日志
	其他handler则只记录等于设置级别的日志
	"""

	def __init__(self, name, level=logging.NOTSET):
		super(AppLogger, self).__init__(name, level)

	def callHandlers(self, record):
		c = self
		found = 0
		while c:
			for hdlr in c.handlers:
				found = found + 1
				if hdlr.name == 'console':
					if record.levelno >= hdlr.level:
						hdlr.handle(record)
				else:
					if record.levelno == hdlr.level:
						hdlr.handle(record)

			if not c.propagate:
				c = None
			else:
				c = c.parent

		if (found == 0) and raiseExceptions and not self.manager.emittedNoHandlerWarning:
			sys.stderr.write("No handlers could be found for logger \"%s\"\n" % self.name)
			self.manager.emittedNoHandlerWarning = 1



def get_logger(logfile_name=__name__, log_path=LOG_PATH):
	'''
	save log to diffrent file by deffirent log level into the log path
	and print all log in console
	'''

	logging.setLoggerClass(AppLogger)
	formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(lineno)s %(message)s', '%Y-%m-%d %H:%M:%S')
	log_files = {
		logging.DEBUG: os.path.join(log_path, logfile_name + '-debug.log'),\
		logging.INFO: os.path.join(log_path, logfile_name + '-info.log'),\
		logging.WARNING: os.path.join(log_path, logfile_name + '-warning.log'),\
		logging.ERROR: os.path.join(log_path, logfile_name + '-error.log'),\
		logging.CRITICAL:os.path.join(log_path, logfile_name + '-critical.log')\
	}

	# 和flask默认使用同一个logger
	logger = logging.getLogger('werkzeug')
	logger.setLevel(logging.DEBUG)

	for log_level, log_file in log_files.items():

		file_handler = logging.handlers.TimedRotatingFileHandler(log_file,'midnight')

		file_handler.setLevel(log_level)
		file_handler.setFormatter(formatter)
		logger.addHandler(file_handler)

	#控制台显示
	console_handler = logging.StreamHandler()
	console_handler.name = "console"
	console_handler.setLevel(logging.DEBUG)
	console_handler.setFormatter(formatter)
	logger.addHandler(console_handler)

	return logger

logger = get_logger()


# handler = logging.FileHandler('loggings.log', encoding='UTF-8')
# logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
# handler.setFormatter(logging_format)
# app.logger.addHandler(handler)




"""
logger.debug('----')
logger.info('----')
logger.error('----')
logger.warning('----')
"""



