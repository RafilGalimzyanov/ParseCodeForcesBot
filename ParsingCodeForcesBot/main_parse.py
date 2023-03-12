import time
import schedule
import database


schedule.every(1).hour.do(database.check)

while True:
    schedule.run_pending()
    time.sleep(1)