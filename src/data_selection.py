import numpy
import collections
import time


class DataSelection(set):

	def __init__(self, dates, dataset=None):
		super().__init__()
		self._as_list = []
		self._dataset = dataset
		self.dates = dates
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


	def get_dates(self):
		return list(map(lambda x: time.strptime(x.decode('UTF-8'), '%Y-%m-%d %H:%M:%S'), self.dates[self.as_list()]))


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


	def symmetric_difference_update(self, *others):
		must_invalidate = False
		for o in others:
			if not isinstance(o, collections.Container):
				o = tuple(o)
			if o:
				must_invalidate = True
				super().symmetric_difference_update(o)
		if must_invalidate:
			self.invalidate()
		return self


	def __ixor__(self, other):
		if other:
			super().__ixor__(other)
			self.invalidate()
		elif not isinstance(other, collections.Set):
			raise TypeError('\'{}\' object is not a set'.format(type(other).__name__))
		return self


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
	'update', 'intersection_update', 'difference_update',
	'__ior__', '__iand__', '__isub__',
):
	setattr(DataSelection, m, _invalide_on_change(getattr(set, m)))
