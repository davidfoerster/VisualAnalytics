class DataSelection(set):

	def __init__(self, dataset=None, stat_keys=None):
		super().__init__()
		self._dataset = dataset
		self._stats = dict()
		self.stat_keys = stat_keys
		self.change_listeners = []


	@property
	def dataset(self):
		return self._dataset

	@dataset.setter
	def dataset(self, new_dataset):
		if new_dataset is not self._dataset:
			self._dataset = new_dataset
			self.invalidate()


	def invalidate(self):
		self._stats.clear()
		for cl in self.change_listeners:
			cl(self)


	def values(self):
		return map(self._dataset.__getitem__, self)


	def flip(self, item):
		has_item = item in self
		if has_item:
			super().remove(item)
		else:
			super().add(item)
		self.invalidate()
		return not has_item


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


def _invalide_on_change(method):
	def change_wrapper(self, *args):
		prev_size = len(self)
		rv = method(self, *args)
		if prev_size != len(self):
			self.invalidate()
		return rv

	return change_wrapper


for m in (
	'add', 'remove', 'discard', 'pop', 'clear',
	'update', 'intersection_update', 'difference_update', 'symmetric_difference_update',
	'__iand__', '__ior__', '__ixor__', '__isub__',
):
	setattr(DataSelection, m, _invalide_on_change(getattr(set, m)))
