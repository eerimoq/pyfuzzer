release-to-pypi:
	python setup.py sdist
	twine upload dist/*
