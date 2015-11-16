_iter_methods = (
	map,
	filter
)
_iter_methods = {
	fn.__name__:
		(lambda *args: tuple(fn(*args))) if __debug__ else fn
	for fn in _iter_methods
}
globals().update(_iter_methods)
del _iter_methods
