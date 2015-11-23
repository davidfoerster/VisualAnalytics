import numpy


class DataSelection(set):

	def __init__(self, dataset=None):
		super().__init__()
		self._as_list = []
		self._dataset = dataset
		self._stats = dict()
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
		self._as_list.clear()
		self._stats.clear()
		for cl in self.change_listeners:
			cl(self)


	"""
	Never modify the returned list!
	"""
	def as_list(self):
		if self and not self._as_list:
			self._as_list.extend(self)
		return self._as_list


	def values(self):
		return self._dataset[self.as_list()]


	def flip(self, item):
		has_item = item in self
		if has_item:
			super().remove(item)
		else:
			super().add(item)
		self.invalidate()
		return not has_item


	def get_stat(self, func, name=None):
		if name is None:
			if isinstance(func, str):
				name = func
			else:
				name = func.__name__

		stat = self._stats.get(name)
		if stat is None:
			if isinstance(func, str):
				stat = getattr(numpy, func)(self.values(), 0)
			else:
				stat = func(self.values())
			self._stats[name] = stat
		return stat


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
