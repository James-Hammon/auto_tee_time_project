from jcg_tee_time_driver import JCGolfTeeTimeDriver
import logging
import sys

logging.basicConfig(level=logging.DEBUG,
	filename='JCGolfDriver.log',
	filemode='w',
	format="[%(asctime)s][%(name)-12.12s][%(levelname)-6.6s] %(message)s")
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

jcg_driver = JCGolfTeeTimeDriver()
jcg_driver.setup()
jcg_driver.login(user_type='resident')
jcg_driver.change_date()
tee_times = jcg_driver.get_available_tee_times()
filtered_tee_times = jcg_driver.filter_tee_times(tee_times)
target_time = "9:00 AM"
best_tee_time_element = jcg_driver.find_best_tee_time(filtered_tee_times, target_time)
jcg_driver.select_tee_time(best_tee_time_element)
jcg_driver.select_agreement_next()
jcg_driver.finalize_reservation()
# logger.info("🏌️reservation finalized!🏌️")
logger.info("reservation finalized")