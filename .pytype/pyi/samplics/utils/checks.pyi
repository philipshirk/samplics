# (generated with --quick)

import numpy
from typing import Any, Dict, Type, Union

Array: Any
Number: Type[Union[float, int]]
StringNumber: Type[Union[float, int, str]]
formats: module
np: module
pd: module

def _assert_probabilities(probabilities) -> None: ...
def _assert_weights(weights) -> None: ...
def _check_brr_number_psus(psu: numpy.ndarray) -> None: ...
def _not_unique(array_unique_values) -> None: ...
def check_response_status(response_status, response_dict: dict) -> None: ...
def check_sample_size_dict(sample_size: Union[int, Dict[Any, int]], stratification: bool, stratum) -> Dict[Any, int]: ...
def check_sample_unit(all_units) -> numpy.ndarray: ...
