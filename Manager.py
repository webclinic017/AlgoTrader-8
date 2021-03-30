import datetime
from AlpacaData import AlpacaData
from Broker import BacktestBroker, AlpacaBroker
from Util import next_runtime, equals_runtime
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger


class Manager:

	def __init__(self, data):
		self.data = data
		self.algos = []
		self.broker = None
		self.datetime = datetime.datetime.now()
	

	def init_broker(self, backtest=False, **kwargs):
		if backtest:
			self.broker = BacktestBroker(**kwargs)
		else:
			self.broker = AlpacaBroker(**kwargs)
		for algo in self.algos:
			algo.set_broker(self.broker)


	def add_algo(self, algo):
		algo.set_data_source(self.data)
		algo.set_broker(self.broker)
		self.algos.append(algo)


	def backtest(self, start=datetime.datetime(2021,3,1), end=datetime.datetime.now(), logschedule=["31 9 * * *"]):
		self.init_broker(backtest=True, data=self.data)
		log_trigger = OrTrigger([CronTrigger.from_crontab(cron) for cron in logschedule])
		algo_trigger = OrTrigger([algo.trigger for algo in self.algos])
		trigger = OrTrigger([algo_trigger, log_trigger])
		self.datetime = start
		while self.datetime < end:
			for algo in self.algos:
				if equals_runtime(algo.trigger, self.datetime):
					algo.datetime = self.datetime
					algo.run()
			if equals_runtime(log_trigger, self.datetime):
				self.log_state()
			self.datetime = next_runtime(trigger, self.datetime)


	def log_state(self):
		self.broker.update_value(self.datetime)
		print("{date} Value: ${value:.2f}".format(date=str(self.datetime.date()), value=self.broker.value))




