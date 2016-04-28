import qi
import zbar
import Image

import functools

"""BarcodeReader

Class implementing NAOqi service named BarcodeReader.
"""
class BarcodeReader:
	def __init__(self, qiapp):
		self.session = qiapp.session
		self.serviceName = self.__class__.__name__
		self.logger = stk.logging.get_logger(self.session, self.serviceName)
		self.scanning = False

		# Init services
		self._connect_services()
		# Set parameters
		self._set_parameters()
		# Init Signals
		self._create_signals()
		# Connect signals
		# self._connect_signals()

		self.logger.info("Ready!")

		# self.start()

	def _connect_services(self):
		"""Connect to all services required by BarcodeReader"""
		self.logger.info('Connecting services...')
		self.services_connected = qi.Promise()
		services_connected_fut = self.services_connected.future()

		def get_services():
			"""Attempt to get all services"""
			try:
				self.mem = self.session.service('ALMemory')
				self.vid = self.session.service("ALVideoDevice")
				# self.speech = self.session.service("ALTextToSpeech")

				self.logger.info('All services are now connected')
				self.services_connected.setValue(True)
			except RuntimeError as e:
				self.logger.warning('Missing service:\n {}'.format(e))

		get_services_task = qi.PeriodicTask()
		get_services_task.setCallback(get_services)
		get_services_task.setUsPeriod(int(2*1000000))  # check every 2s
		get_services_task.start(True)
		try:
			services_connected_fut.value(30*1000)  # timeout = 30s
			get_services_task.stop()
		except RuntimeError:
			get_services_task.stop()
			self.logger.error('Failed to reach all services after 30 seconds')
			raise RuntimeError

	def _set_parameters(self):
		self.logger.info('Setting parameters...')
		subscribers = self.vid.getSubscribers()
		for sub in subscribers:
			if "python_client" in sub:
				self.vid.unsubscribe(sub)
			elif "videoBuffer" in sub:
				self.vid.unsubscribe(sub)

		self.videoClient = self.vid.subscribe("python_client", 2, 11, 5)
		self.vid.setParam(40, 1) # force auto focus
		self.logger.info('Parameters have been set...')

	def _create_signals(self):
		self.logger.info('Creating required signals and events...')
		self.onBarcodeDetected = qi.Signal()
		# self.onBarcodeDetectedEvent = '{}/{}'.format(self.serviceName, 'BarcodeDetected')
		# self.mem.declareEvent(self.onBarcodeDetectedEvent, self.serviceName)
		self.logger.info('All signals have been created')

	def _connect_signals(self):
		self.logger.info('Binding signals and events...')
		# self.conID = self.onBarcodeDetected.connect(self._barcodeDetected)
		self.logger.info('All signals have been binded')


	@stk.logging.log_exceptions
	def _getImage(self):
		self.logger.info("Getting image...")
		pepperImage = self.vid.getImageRemote(self.videoClient)

		if pepperImage is not None:
			im = Image.fromstring("RGB", (pepperImage[0], pepperImage[1]), str(bytearray(pepperImage[6])))
			im = im.convert('L')

			self.logger.info("Analyzing image...")
			zImage = zbar.Image(im.size[0], im.size[1], 'Y800', im.tostring())
			# im = Image.open(os.path.join(sys.path[0], "barcode.png")).convert('L')
			# zImage = zbar.Image(im.size[0], im.size[1], 'Y800', im.tostring())

			scn = zbar.ImageScanner()

			if scn.scan(zImage) > 0:
				results = scn.get_results()
				for sym in results:
					sym_type = str(sym.type)
					sym_data = str(sym.data)

				self.logger.info("\tType : %s" % sym_type)
				self.logger.info("\tData : %s" % sym_data)
				self.onBarcodeDetected(sym_type, sym_data)

	# def _barcodeDetected(self, sym_type, sym_data):
	# 	# self.speech.say("I recognized it !")
	# 	self.logger.info("Barcode detected !")
	# 	self.logger.info("\tType : %s" % sym_type)
	# 	self.logger.info("\tData : %s" % sym_data)
	# 	# self.speech.say("The first 3 digits are : %s"%sym_data[0:3])
	# 	# self.speech.say("Show me another one !")

	def stop(self):
		if self.scanning:
			self.scanning = False
			self.logger.info("Cleaning...")

			self.getImageTask.stop()
			self.vid.unsubscribe(self.videoClient)
			# self.onBarcodeDetected.disconnect(self.conID)

			self.logger.info("End!")

	def start(self):
		if not self.scanning:
			self.scanning = True
			self.logger.info("Starting...")

			getImageCallable = functools.partial(self._getImage)

			self.getImageTask = qi.PeriodicTask()
			self.getImageTask.setCallback(getImageCallable)
			self.getImageTask.setUsPeriod(int(0.5*1000000)) # 0.5 sec
			self.getImageTask.start(True)

	def on_stop(self):
		self.stop() # should be stop_scanning


if __name__ == "__main__":
    """
    Registers BarcodeReader as a naoqi service.
    """
    stk.runner.run_service(BarcodeReader)
