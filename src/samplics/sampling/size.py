"""Sample size calculation module 

"""

from __future__ import annotations

import math

from typing import Optional, Union


import numpy as np
import pandas as pd

from scipy.stats import norm as normal
from scipy.stats import t as student

from dataclasses import InitVar, field
from pydantic.dataclasses import dataclass

from samplics.sampling.size_functions import (
    calculate_ss_fleiss_prop,
    calculate_ss_wald_prop,
    calculate_ss_wald_mean,
    calculate_ss_wald_mean_one_sample,
    calculate_ss_wald_mean_two_samples,
    calculate_ss_wald_prop_two_samples,
)
from samplics.sampling.power_functions import calculate_power, calculate_power_prop

from samplics.utils.formats import convert_numbers_to_dicts, dict_to_dataframe, numpy_array
from samplics.utils.types import Array, DictStrNum, Number, StringNumber, PopParam


def allocate(
    method: str,
    stratum: Array,
    pop_size: DictStrNum,
    samp_size: Optional[Number] = None,
    constant: Optional[Number] = None,
    rate: Optional[Union[DictStrNum, Number]] = None,
    stddev: Optional[DictStrNum] = None,
) -> tuple[DictStrNum, DictStrNum]:
    """Reference: Kish(1965), page 97"""

    stratum = list(numpy_array(stratum))

    if method.lower() == "equal":
        if isinstance(constant, (int, float)):
            sample_sizes = dict(zip(stratum, np.repeat(constant, len(stratum))))
        else:
            raise ValueError("param 'target_size' must be a valid integer!")
    elif method.lower() == "propal":
        if isinstance(pop_size, dict) and stddev is None and samp_size is not None:
            total_pop = sum(list(pop_size.values()))
            samp_size_h = [math.ceil((samp_size / total_pop) * pop_size[k]) for k in stratum]
            sample_sizes = dict(zip(stratum, samp_size_h))
        elif isinstance(pop_size, dict) and stddev is not None and samp_size is not None:
            total_pop = sum(list(pop_size.values()))
            samp_size_h = [
                math.ceil((samp_size / total_pop) * pop_size[k] * stddev[k]) for k in stratum
            ]
            sample_sizes = dict(zip(stratum, samp_size_h))
        else:
            raise ValueError("param 'pop_size' must be a dictionary and 'samp_size' an integer!")
    elif method.lower() == "fixed_rate":
        if isinstance(rate, (int, float)) and pop_size is not None:
            samp_size_h = [math.ceil(rate * pop_size[k]) for k in stratum]
        else:
            raise ValueError(
                "param 'pop_size' and 'rate' must be a dictionary and number respectively!"
            )
        sample_sizes = dict(zip(stratum, samp_size_h))
    elif method.lower() == "propal_rate":
        if isinstance(rate, (int, float)) and pop_size is not None:
            samp_size_h = [math.ceil(rate * pop_size[k] * pop_size[k]) for k in stratum]
        else:
            raise ValueError("param 'pop_size' must be a dictionary!")
        sample_sizes = dict(zip(stratum, samp_size_h))
    elif method.lower() == "equal_errors":
        if isinstance(constant, (int, float)) and stddev is not None:
            samp_size_h = [math.ceil(constant * stddev[k] * stddev[k]) for k in stratum]
        else:
            raise ValueError(
                "param 'stddev' and 'constant' must be a dictionary and number, respectively!"
            )
        sample_sizes = dict(zip(stratum, samp_size_h))
    elif method.lower() == "optimum_mean":
        if isinstance(rate, (int, float)) and pop_size is not None and stddev is not None:
            samp_size_h = [math.ceil(rate * pop_size[k] * stddev[k]) for k in stratum]
        else:
            raise ValueError(
                "param 'pop_size' and 'rate' must be a dictionary and number respectively!"
            )
        sample_sizes = dict(zip(stratum, samp_size_h))
    elif method.lower() == "optimum_comparison":
        if isinstance(rate, (int, float)) and stddev is not None:
            samp_size_h = [math.ceil(rate * stddev[k]) for k in stratum]
        else:
            raise ValueError(
                "param 'stddev' and 'rate' must be a dictionary and number respectively!"
            )
        sample_sizes = dict(zip(stratum, samp_size_h))
    elif method.lower() == "variable_rate" and isinstance(rate, dict) and pop_size is not None:
        samp_size_h = [math.ceil(rate[k] * pop_size[k]) for k in stratum]
        sample_sizes = dict(zip(stratum, samp_size_h))
    else:
        raise ValueError(
            "param 'method' is not valid. Options are 'equal', 'propal', 'fixed_rate', 'propal_rate', 'equal_errors', 'optimun_mean', and 'optimun_comparison'!"
        )

    if (list(sample_sizes.values()) > np.asarray(list(pop_size.values()))).any():
        raise ValueError(
            "Some of the constants, rates, or standard errors are too large, resulting in sample sizes larger than population sizes!"
        )

    sample_rates = {}
    if isinstance(pop_size, dict):
        for k in pop_size:
            sample_rates[k] = sample_sizes[k] / pop_size[k]

    return sample_sizes, sample_rates


def calculate_clusters() -> None:
    pass


@dataclass
class SampleSize:
    """*SampleSize* implements sample size calculation methods"""

    param: InitVar[str] = field(init=True, default="prop")
    method: InitVar[str] = field(init=True, default="wald")
    strat: InitVar[bool] = field(init=True, default=False)

    target: Union[DictStrNum, Number] = field(init=False, default_factory=dict)
    sigma: Union[DictStrNum, Number] = field(init=False, default_factory=dict)
    half_ci: Union[DictStrNum, Number] = field(init=False, default_factory=dict)

    # param: str = "prop"
    # method: str = "wald"
    # strat: bool = False

    # target: Union[DictStrNum, Number] = None
    # sigma: Union[DictStrNum, Number] = None
    # half_ci: Union[DictStrNum, Number] = None

    # param: PopParam = field(init=False, default=None)
    samp_size: Union[DictStrNum, Number] = 0
    deff_c: Union[DictStrNum, Number] = 1.0
    deff_w: Union[DictStrNum, Number] = 1.0
    resp_rate: Union[DictStrNum, Number] = 1.0
    # pop_size: Optional[Union[DictStrNum, Number]] = field(init=False, default_factory=None)
    pop_size: Optional[Union[DictStrNum, Number]] = None

    def __post_init__(
        self, param: str = "prop", method: str = "wald", strat: bool = False
    ) -> None:

        self.param = param.lower()
        self.method = method.lower()
        if self.param not in ("prop", "mean", "total"):
            raise AssertionError("param must be prop, mean, or total.")
        if self.param == "prop" and self.method not in ("wald", "fleiss"):
            raise AssertionError("For prop, the method must be wald or Fleiss.")
        if self.param == "mean" and self.method not in ("wald"):
            raise AssertionError("For mean and total, the method must be wald.")

        # if self.param == "mean":
        #     self.param = PopParam.mean
        # if self.param == "total":
        #     self.param = PopParam.total
        # if self.param == "prop":
        #     self.param = PopParam.prop

        self.strat = strat
        # self.target: Union[DictStrNum, Number]
        # self.sigma: Union[DictStrNum, Number]
        # self.half_ci: Union[DictStrNum, Number]
        # self.samp_size: Union[DictStrNum, Number] = 0
        # self.deff_c: Union[DictStrNum, Number] = 1.0
        # self.deff_w: Union[DictStrNum, Number] = 1.0
        # self.resp_rate: Union[DictStrNum, Number] = 1.0
        # self.pop_size: Optional[Union[DictStrNum, Number]] = None

    def icc(self) -> Union[DictStrNum, Number]:
        pass  # TODO

    def deff(
        self,
        cluster_size: Union[DictStrNum, Number],
        icc: Union[DictStrNum, Number],
    ) -> Union[DictStrNum, Number]:

        if isinstance(cluster_size, (int, float)) and isinstance(icc, (int, float)):
            return max(1 + (cluster_size - 1) * icc, 0)
        elif isinstance(cluster_size, dict) and isinstance(icc, dict):
            if cluster_size.keys() != icc.keys():
                raise AssertionError("params do not have the same dictionary keys.")
            deff_c: DictStrNum = {}
            for s in cluster_size:
                deff_c[s] = max(1 + (cluster_size[s] - 1) * icc[s], 0)
            return deff_c
        else:
            raise ValueError("Combination of types not supported.")

    def calculate(
        self,
        half_ci: Union[DictStrNum, Number],
        target: Optional[Union[DictStrNum, Number]] = None,
        sigma: Optional[Union[DictStrNum, Number]] = None,
        deff: Union[DictStrNum, Number, Number] = 1.0,
        resp_rate: Union[DictStrNum, Number] = 1.0,
        number_strata: Optional[int] = None,
        pop_size: Optional[Union[DictStrNum, Number]] = None,
        alpha: float = 0.05,
    ) -> None:

        if self.param == "prop" and target is None:
            raise AssertionError("target must be provided to calculate sample size for prop.")

        if self.param == "mean" and sigma is None:
            raise AssertionError("sigma must be provided to calculate sample size for mean.")

        if self.param == "prop":
            if isinstance(target, (int, float)) and not 0 <= target <= 1:
                raise ValueError("Target for props must be between 0 and 1.")
            if isinstance(target, dict):
                for s in target:
                    if not 0 <= target[s] <= 1:
                        raise ValueError("Target for props must be between 0 and 1.")

        if self.param == "prop" and sigma is None:
            if isinstance(target, (int, float)):
                sigma = target * (1 - target)
            if isinstance(target, dict):
                sigma = {}
                for s in target:
                    sigma[s] = target[s] * (1 - target[s])

        if self.strat:
            (
                self.half_ci,
                self.target,
                self.sigma,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
            ) = convert_numbers_to_dicts(
                number_strata, half_ci, target, sigma, deff, resp_rate, pop_size, alpha
            )
        else:
            (
                self.half_ci,
                self.target,
                self.sigma,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
            ) = (half_ci, target, sigma, deff, resp_rate, pop_size, alpha)

        samp_size: Union[DictStrNum, Number]
        if self.param == "prop" and self.method == "wald":
            self.samp_size = calculate_ss_wald_prop(
                half_ci=self.half_ci,
                target=self.target,
                pop_size=self.pop_size,
                deff_c=self.deff_c,
                resp_rate=self.resp_rate,
                alpha=self.alpha,
                strat=self.strat,
            )
        elif self.param == "prop" and self.method == "fleiss":
            self.samp_size = calculate_ss_fleiss_prop(
                half_ci=self.half_ci,
                target=self.target,
                deff_c=self.deff_c,
                resp_rate=self.resp_rate,
                alpha=self.alpha,
                strat=self.strat,
            )
        elif self.param in ("mean", "total") and self.method == "wald":
            self.samp_size = calculate_ss_wald_mean(
                half_ci=self.half_ci,
                sigma=self.sigma,
                pop_size=self.pop_size,
                deff_c=self.deff_c,
                resp_rate=self.resp_rate,
                alpha=self.alpha,
                strat=self.strat,
            )

    def to_dataframe(self, col_names: Optional[list[str]] = None) -> pd.DataFrame:
        """Coverts the dictionaries to a pandas dataframe

        Args:
            col_names (list[str], optional): column names for the dataframe. Defaults to
                ["_stratum", "_target", "_half_ci", "_samp_size"].

        Raises:
            AssertionError: when sample size is not calculated.

        Returns:
            pd.DataFrame: output pandas dataframe.
        """

        if self.samp_size is None:
            raise AssertionError("No sample size calculated.")
        elif col_names is None:
            col_names = [
                "_param",
                "_stratum",
                "_target",
                "_sigma",
                "_half_ci",
                "_samp_size",
            ]
            if not self.strat:
                col_names.pop(1)
        else:
            ncols = len(col_names)
            if (ncols != 6 and self.strat) or (ncols != 5 and not self.strat):
                raise AssertionError(
                    "col_names must have 6 values for stratified design and 5 for not stratified design."
                )
        est_df = dict_to_dataframe(
            col_names,
            self.target,
            self.sigma,
            self.half_ci,
            self.samp_size,
        )
        est_df.iloc[:, 0] = self.param

        return est_df


class SampleSizeMeanOneSample:
    """SampleSizeMeanOneSample implements sample size calculation for mean under one-sample design"""

    def __init__(
        self,
        method: str = "wald",
        strat: bool = False,
        two_sides: bool = True,
        params_estimated: bool = True,
    ) -> None:

        self.param = "mean"
        self.method = method.lower()
        if self.method not in ("wald"):
            raise AssertionError("The method must be wald.")

        self.strat = strat
        self.two_sides = two_sides
        self.params_estimated = params_estimated

        self.samp_size: Union[DictStrNum, Array, Number]
        self.actual_power: Union[DictStrNum, Array, Number]

        self.mean_0: Union[DictStrNum, Array, Number]
        self.mean_1: Union[DictStrNum, Array, Number]
        self.epsilon: Union[DictStrNum, Array, Number]
        self.delta: Union[DictStrNum, Array, Number]
        self.sigma: Union[DictStrNum, Array, Number]

        self.deff_c: Union[DictStrNum, Array, Number]
        self.deff_w: Union[DictStrNum, Array, Number]
        self.resp_rate: Union[DictStrNum, Array, Number]
        self.pop_size: Optional[Union[DictStrNum, Array, Number]] = None

        self.alpha: Union[DictStrNum, Array, Number]
        self.beta: Union[DictStrNum, Array, Number]
        self.power: Union[DictStrNum, Array, Number]

    def calculate(
        self,
        mean_0: Union[DictStrNum, Array, Number],
        mean_1: Union[DictStrNum, Array, Number],
        sigma: Union[DictStrNum, Array, Number],
        delta: Union[DictStrNum, Array, Number] = 0.0,
        deff: Union[DictStrNum, Array, Number] = 1.0,
        resp_rate: Union[DictStrNum, Array, Number] = 1.0,
        number_strata: Optional[int] = None,
        pop_size: Optional[Union[DictStrNum, Array, Number]] = None,
        alpha: Union[DictStrNum, Array, Number] = 0.05,
        power: Union[DictStrNum, Array, Number] = 0.80,
    ) -> None:

        if self.strat:
            (
                self.mean_0,
                self.mean_1,
                self.sigma,
                self.delta,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
                self.power,
            ) = convert_numbers_to_dicts(
                number_strata,
                mean_0,
                mean_1,
                sigma,
                delta,
                deff,
                resp_rate,
                pop_size,
                alpha,
                power,
            )
        else:
            (
                self.mean_0,
                self.mean_1,
                self.sigma,
                self.delta,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
                self.power,
            ) = (
                mean_0,
                mean_1,
                sigma,
                delta,
                deff,
                resp_rate,
                pop_size,
                alpha,
                power,
            )

        if self.strat:
            epsilon: DictStrNum = {}
            for s in mean_0:
                epsilon[s] = mean_1[s] - mean_0[s]
            self.epsilon = epsilon
        else:
            self.epsilon = mean_1 - mean_0

        self.samp_size = calculate_ss_wald_mean_one_sample(
            two_sides=self.two_sides,
            epsilon=self.epsilon,
            delta=self.delta,
            sigma=self.sigma,
            deff_c=self.deff_c,
            resp_rate=self.resp_rate,
            alpha=self.alpha,
            power=self.power,
            strat=self.strat,
        )

        if self.strat:
            actual_power: DictStrNum = {}
            for k in self.samp_size:
                actual_power[k] = calculate_power(
                    self.two_sides,
                    self.epsilon[k],
                    self.sigma[k],
                    self.samp_size[k],
                    self.alpha[k],
                )
            self.actual_power = actual_power
        else:
            self.actual_power = calculate_power(
                self.two_sides, self.epsilon, self.sigma, self.samp_size, self.alpha
            )


class SampleSizePropOneSample:
    """SampleSizePropOneSample implements sample size calculation for propoertion under one-sample design"""

    def __init__(
        self,
        method: str = "wald",
        strat: bool = False,
        two_sides: bool = True,
        params_estimated: bool = True,
    ) -> None:

        self.param = "prop"
        self.method = method.lower()
        if self.method not in ("wald"):
            raise AssertionError("The method must be wald.")

        self.strat = strat
        self.two_sides = two_sides
        self.params_estimated = params_estimated

        self.samp_size: Union[DictStrNum, Number]
        self.actual_power: Union[DictStrNum, Number]

        self.prop_0: Union[DictStrNum, Number]
        self.prop_1: Union[DictStrNum, Number]
        self.epsilon: Union[DictStrNum, Number]
        self.delta: Union[DictStrNum, Number]
        self.sigma: Union[DictStrNum, Number]

        self.deff_c: Union[DictStrNum, Number]
        self.deff_w: Union[DictStrNum, Number]
        self.resp_rate: Union[DictStrNum, Number]
        self.pop_size: Optional[Union[DictStrNum, Number]] = None

        self.alpha: Union[DictStrNum, Number]
        self.beta: Union[DictStrNum, Number]
        self.power: Union[DictStrNum, Number]

    def calculate(
        self,
        prop_0: Union[DictStrNum, Array, Number],
        prop_1: Union[DictStrNum, Array, Number],
        delta: Union[DictStrNum, Array, Number] = 0.0,
        arcsin: bool = False,
        continuity: bool = False,
        deff: Union[DictStrNum, Array, Number] = 1.0,
        resp_rate: Union[DictStrNum, Array, Number] = 1.0,
        number_strata: Optional[int] = None,
        pop_size: Optional[Union[DictStrNum, Array, Number]] = None,
        alpha: Union[DictStrNum, Array, Number] = 0.05,
        power: Union[DictStrNum, Array, Number] = 0.80,
    ) -> None:

        if self.strat:
            (
                self.prop_0,
                self.prop_1,
                self.delta,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
                self.power,
            ) = convert_numbers_to_dicts(
                number_strata,
                prop_0,
                prop_1,
                delta,
                deff,
                resp_rate,
                pop_size,
                alpha,
                power,
            )
        else:
            (
                self.prop_0,
                self.prop_1,
                self.delta,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
                self.power,
            ) = (
                prop_0,
                prop_1,
                delta,
                deff,
                resp_rate,
                pop_size,
                alpha,
                power,
            )

        if self.strat:
            epsilon: DictStrNum = {}
            sigma: DictStrNum = {}
            for s in prop_0:
                epsilon[s] = prop_1[s] - prop_0[s]
                sigma[s] = math.sqrt(prop_1[s] * (1 - prop_1[s]))
            self.epsilon = epsilon
            self.sigma = sigma
        else:
            self.epsilon = prop_1 - prop_0
            self.sigma = math.sqrt(prop_1 * (1 - prop_1))

        self.arcsin = arcsin
        self.continuity = continuity

        self.samp_size = calculate_ss_wald_mean_one_sample(
            two_sides=self.two_sides,
            epsilon=self.epsilon,
            delta=self.delta,
            sigma=self.sigma,
            deff_c=self.deff_c,
            resp_rate=self.resp_rate,
            alpha=self.alpha,
            power=self.power,
            strat=self.strat,
        )

        if self.strat:
            actual_power: DictStrNum = {}
            for k in self.samp_size:
                actual_power[k] = calculate_power(
                    self.two_sides,
                    self.epsilon[k],
                    self.sigma[k],
                    self.samp_size[k],
                    self.alpha[k],
                )
            self.actual_power = actual_power
        else:
            self.actual_power = calculate_power(
                self.two_sides, self.epsilon, self.sigma, self.samp_size, self.alpha
            )


class SampleSizeMeanTwoSample:
    """SampleSizeMeanTwoSample implements sample size calculation for mean under two-sample design"""

    def __init__(
        self,
        method: str = "wald",
        strat: bool = False,
        two_sides: bool = True,
        params_estimated: bool = True,
    ) -> None:

        self.param = "mean"
        self.method = method.lower()
        if self.method not in ("wald"):
            raise AssertionError("The method must be wald.")

        self.strat = strat
        self.two_sides = two_sides
        self.params_estimated = params_estimated

        self.samp_size: Union[DictStrNum, Array, Number]
        self.actual_power: Union[DictStrNum, Array, Number]

        self.mean_1: Union[DictStrNum, Array, Number]
        self.mean_2: Union[DictStrNum, Array, Number]
        self.epsilon: Union[DictStrNum, Array, Number]
        self.delta: Union[DictStrNum, Array, Number]
        self.sigma_1: Union[DictStrNum, Array, Number]
        self.sigma_2: Union[DictStrNum, Array, Number]
        self.equal_variance: Union[DictStrNum, Array, Number]

        self.deff_c: Union[DictStrNum, Array, Number]
        self.deff_w: Union[DictStrNum, Array, Number]
        self.resp_rate: Union[DictStrNum, Array, Number]
        self.pop_size: Optional[Union[DictStrNum, Array, Number]] = None

        self.alpha: Union[DictStrNum, Array, Number]
        self.beta: Union[DictStrNum, Array, Number]
        self.power: Union[DictStrNum, Array, Number]

    def calculate(
        self,
        mean_1: Union[DictStrNum, Array, Number],
        mean_2: Union[DictStrNum, Array, Number],
        sigma_1: Union[DictStrNum, Array, Number],
        sigma_2: Optional[Union[DictStrNum, Array, Number]] = None,
        equal_variance: Union[DictStrNum, Array, Number] = True,
        kappa: Optional[Union[DictStrNum, Array, Number]] = 1,
        delta: Union[DictStrNum, Array, Number] = 0.0,
        deff: Union[DictStrNum, Array, Number] = 1.0,
        resp_rate: Union[DictStrNum, Array, Number] = 1.0,
        number_strata: Optional[int] = None,
        pop_size: Optional[Union[DictStrNum, Array, Number]] = None,
        alpha: Union[DictStrNum, Array, Number] = 0.05,
        power: Union[DictStrNum, Array, Number] = 0.80,
    ) -> None:

        if self.strat:
            (
                self.mean_1,
                self.mean_2,
                self.sigma_1,
                self.sigma_2,
                self.equal_variance,
                self.kappa,
                self.delta,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
                self.power,
            ) = convert_numbers_to_dicts(
                number_strata,
                mean_1,
                mean_2,
                sigma_1,
                sigma_2,
                equal_variance,
                kappa,
                delta,
                deff,
                resp_rate,
                pop_size,
                alpha,
                power,
            )
        else:
            (
                self.mean_1,
                self.mean_2,
                self.sigma_1,
                self.sigma_2,
                self.equal_variance,
                self.kappa,
                self.delta,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
                self.power,
            ) = (
                mean_1,
                mean_2,
                sigma_1,
                sigma_2,
                equal_variance,
                kappa,
                delta,
                deff,
                resp_rate,
                pop_size,
                alpha,
                power,
            )

        if self.strat:
            epsilon: DictStrNum = {}
            for s in mean_1:
                epsilon[s] = mean_2[s] - mean_1[s]
            self.epsilon = epsilon
        else:
            self.epsilon = mean_2 - mean_1

        self.samp_size = calculate_ss_wald_mean_two_samples(
            two_sides=self.two_sides,
            epsilon=self.epsilon,
            delta=self.delta,
            sigma_1=self.sigma_1,
            sigma_2=self.sigma_2,
            equal_variance=self.equal_variance,
            kappa=kappa,
            deff_c=self.deff_c,
            resp_rate=self.resp_rate,
            alpha=self.alpha,
            power=self.power,
            strat=self.strat,
        )

        # if self.strat:
        #     for k in self.samp_size:
        #         self.actual_power[k] = calculate_power(
        #             self.two_sides,
        #             self.epsilon[k],
        #             self.sigma[k],
        #             self.samp_size[k],
        #             self.alpha[k],
        #         )
        # else:
        #     self.actual_power = calculate_power(
        #         self.two_sides, self.epsilon, self.sigma, self.samp_size, self.alpha
        #     )


class SampleSizePropTwoSample:
    """SampleSizeMeanTwoSample implements sample size calculation for mean under two-sample design"""

    def __init__(
        self,
        method: str = "wald",
        strat: bool = False,
        two_sides: bool = True,
        params_estimated: bool = True,
    ) -> None:

        self.param = "prop"
        self.method = method.lower()
        if self.method not in ("wald"):
            raise AssertionError("The method must be wald.")

        self.strat = strat
        self.two_sides = two_sides
        self.params_estimated = params_estimated

        self.samp_size: Union[DictStrNum, Array, Number]
        self.actual_power: Union[DictStrNum, Array, Number]

        self.prop_1: Union[DictStrNum, Array, Number]
        self.prop_2: Union[DictStrNum, Array, Number]
        self.epsilon: Union[DictStrNum, Array, Number]
        self.delta: Union[DictStrNum, Array, Number]

        self.deff_c: Union[DictStrNum, Array, Number]
        self.deff_w: Union[DictStrNum, Array, Number]
        self.resp_rate: Union[DictStrNum, Array, Number]
        self.pop_size: Optional[Union[DictStrNum, Array, Number]] = None

        self.alpha: Union[DictStrNum, Array, Number]
        self.beta: Union[DictStrNum, Array, Number]
        self.power: Union[DictStrNum, Array, Number]

    def calculate(
        self,
        prop_1: Union[DictStrNum, Array, Number],
        prop_2: Union[DictStrNum, Array, Number],
        kappa: Optional[Union[DictStrNum, Array, Number]] = 1,
        delta: Union[DictStrNum, Array, Number] = 0.0,
        deff: Union[DictStrNum, Array, Number] = 1.0,
        resp_rate: Union[DictStrNum, Array, Number] = 1.0,
        number_strata: Optional[int] = None,
        pop_size: Optional[Union[DictStrNum, Array, Number]] = None,
        alpha: Union[DictStrNum, Array, Number] = 0.05,
        power: Union[DictStrNum, Array, Number] = 0.80,
    ) -> None:

        if self.strat:
            (
                self.prop_1,
                self.prop_2,
                self.kappa,
                self.delta,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
                self.power,
            ) = convert_numbers_to_dicts(
                number_strata,
                prop_1,
                prop_2,
                kappa,
                delta,
                deff,
                resp_rate,
                pop_size,
                alpha,
                power,
            )
        else:
            (
                self.prop_1,
                self.prop_2,
                self.kappa,
                self.delta,
                self.deff_c,
                self.resp_rate,
                self.pop_size,
                self.alpha,
                self.power,
            ) = (
                prop_1,
                prop_2,
                kappa,
                delta,
                deff,
                resp_rate,
                pop_size,
                alpha,
                power,
            )

        if self.strat:
            epsilon: DictStrNum = {}
            for s in prop_1:
                epsilon[s] = prop_2[s] - prop_1[s]
            self.epsilon = epsilon
        else:
            self.epsilon = prop_2 - prop_1

        self.samp_size = calculate_ss_wald_prop_two_samples(
            two_sides=self.two_sides,
            epsilon=self.epsilon,
            delta=self.delta,
            prop_1=self.prop_1,
            prop_2=self.prop_2,
            kappa=kappa,
            deff_c=self.deff_c,
            resp_rate=self.resp_rate,
            alpha=self.alpha,
            power=self.power,
            strat=self.strat,
        )

        # if self.strat:
        #     for k in self.samp_size:
        #         self.actual_power[k] = calculate_power(
        #             self.two_sides,
        #             self.epsilon[k],
        #             self.sigma[k],
        #             self.samp_size[k],
        #             self.alpha[k],
        #         )
        # else:
        #     self.actual_power = calculate_power(
        #         self.two_sides, self.epsilon, self.sigma, self.samp_size, self.alpha
        #     )
