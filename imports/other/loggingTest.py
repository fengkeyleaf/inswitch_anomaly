# https://www.geeksforgeeks.org/logging-in-python/
# https://betterstack.com/community/questions/how-to-color-python-logging-output/

# importing module
import logging

# Create and configure logger
# logging.basicConfig( filename = "newfile.log",
#                      format = '%(asctime)s %(message)s',
#                      filemode = 'w' )

logging.basicConfig( format = '%(asctime)s %(message)s' )

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.CRITICAL)

# Test messages
logger.debug("Harmless debug Message")
logger.info("Just an information")
logger.warning("Its a Warning")
logger.error("Did you try to divide by zero")
logger.critical("Internet is down")
