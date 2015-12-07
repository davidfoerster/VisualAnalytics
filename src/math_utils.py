import math
import numpy as np
import scipy.special


def fitLine(xs, ys):
	n = len(xs)
	if n <= 2:
		return None

	s_x = np.sum(xs, dtype=float)
	s_y = np.sum(ys, dtype=float)
	t_i = xs - s_x / n
	s_tt = np.sum(t_i * t_i)
	b = np.sum(t_i * ys) / s_tt
	a = (s_y - s_x * b) / n

	chi_2 = np.sum((ys - a - b * xs)**2) / (n - 2)
	q = scipy.special.gammainc(.5 * (n - 2), .5 * chi_2)
	sigma_a = math.sqrt((1 + s_x * s_x / (n * s_tt)) / n)
	sigma_b = math.sqrt(1 / s_tt)
	cov_ab = -s_x / (n * s_tt)
	r = cov_ab / (sigma_a * sigma_b)

	return a, b, q, r, sigma_a, sigma_b
