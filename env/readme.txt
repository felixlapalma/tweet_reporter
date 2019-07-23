Environment:
************
from:
	conda env export | grep -v "^prefix: " > environment.yml

to deploy

	conda env create -f environment.yml
