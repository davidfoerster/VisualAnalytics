class DataSelection(set):

	def __init__(self, dataset=None, stat_keys=None):
		super().__init__()
		self._dataset = dataset
		self._stats = dict()
		self.stat_keys = stat_keys


	@property
	def dataset(self):
		return self._dataset

	@dataset.setter
	def dataset(self, new_dataset):
		if new_dataset is not self._dataset:
			self.invalidate()
			self._dataset = new_dataset


	def invalidate(self):
		self._stats.clear()


	def values(self):
		return map(self._dataset.__getitem__, self)


	def get_stat(self, func, name=None):
		if isinstance(func, str):
			name = func
			func = None
		elif name is None and callable(func):
			name = func.__name__
		else:
			raise TypeError()

		stat = self._stats.get(name)
		if stat is None:
			if self.stat_keys is None:
				stat = func(self.values())
			else:
				stat = [func(map(self._dataset[k].__getitem__, self)) for k in self.stat_keys]
			self._stats[name] = stat
		return stat


	def mean(self):
		from statistics import mean
		return self.get_stat(mean)


	def discard(self, elem):
		if elem in self:
			super().discard(elem)
			self.invalidate()


	def intersection_update(self, *others):
		for o in others:
			self.__iand__(o)
		return self


	def __iand__(self, other):
		if not self.issubset(other):
			super().__iand__(other)
			self.invalidate()
		return self


	def pop(self):
		r = super().pop()
		self.invalidate()
		return r


	def add(self, elem):
		if elem not in self:
			super().add(elem)
			self.invalidate()


	def remove(self, elem):
		if elem in self:
			self.invalidate()
		super().remove(elem)


	def difference_update(self, *others):
		for o in others:
			self.__isub__(o)
		return self

	def __isub__(self, other):
		if not self.isdisjoint(other):
			super().__isub__(other)
			self.invalidate()
		return self


	def symmetric_difference_update(self, *others):
		for o in others:
			self.__ixor__(o)
		return self

	def __ixor__(self, other):
		if len(other):
			super().__ixor__(other)
			self.invalidate()
		return self


	def update(self, *others):
		for o in others:
			self.__ior__(o)
		return self

	def __ior__(self, other):
		if not self.issuperset(other):
			super().__ior__(other)
			self.invalidate()
		return self


	def clear(self):
		super().clear()
		self.invalidate()
