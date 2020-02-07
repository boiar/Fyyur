from app import create_app
from config import Config
from models import db
from datetime import datetime
import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler


print("--------------------------------")
print(Config)
print("=================================")

app = create_app(Config)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

if not app.debug:
  file_handler = FileHandler("error.log")
  file_handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
  app.logger.setLevel(logging.INFO)
  file_handler.setLevel(logging.INFO)
  app.logger.addHandler(file_handler)
  app.logger.info("errors")

if __name__ == '__main__':
  db.create_all(app=app)
  app.run()