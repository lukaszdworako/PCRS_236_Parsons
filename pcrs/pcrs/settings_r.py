from datetime import timedelta

# Period between file deletes of user uploads
FILE_DELETE_FREQUENCY = 1440 #24 hrs

# Default lifespan of files on the system
FILE_LIFESPAN = timedelta(days=1)
