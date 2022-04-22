import logging
import sys

class User():

	def __init__(self, user_type: str) -> None:
		self.user_type = user_type
		self.sub_url = None
		self.date_sub_str = None
		self.date_offset = None
		self.logger = None
		self.setup()

	def setup(self) -> bool:
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.addHandler(logging.StreamHandler(sys.stdout))
		if self.user_type not in ['public', 'jcplayer', 'socal', 'resident']:
			self.logger.error("INVALID USER PROFILE")
			return False
		if self.user_type == 'resident':
			self.sub_url = 'gres'
			self.date_sub_str = 'c10-6'
			self.date_offset = 8
		elif self.user_type == 'jcplayer':
			self.sub_url = 'player'
			self.date_sub_str = 'c10-6'
			self.date_offset = 7
		elif self.user_type == 'public':
			self.sub_url = 'gpub'
			self.date_sub_str = 'c11-2'
			self.date_offset = 7
		self.logger.debug(f"user type: {self.user_type} "
			f"sub url: {self.sub_url} "
			f"date substring: {self.date_sub_str} "
			f"date offset: {self.date_offset}"
		)
		return True


class Course():

	def __init__(self, course_name: str) -> None:
		self.course_name = course_name
		self.url_number = None
		self.setup()

	def setup(self) -> bool:
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.addHandler(logging.StreamHandler(sys.stdout))
		if self.course_name not in ['Encinitas Ranch']:
			self.logger.error("INVALID COURSE")
			return False
		if self.course_name == 'Encinitas Ranch':
			self.url_number = '5'
		self.logger.debug(f"course: {self.course_name} "
			f"url number: {self.url_number}")
		return True
