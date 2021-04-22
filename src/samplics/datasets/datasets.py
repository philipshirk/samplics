from __future__ import annotations

from typing import Optional

from os.path import dirname, join

import pandas as pd


def load_dataset(
    file_name: str,
    colnames: Optional[list],
    name: str,
    description: str,
    design: dict,
    source: str,
) -> None:

    module_path = dirname(__file__)
    file_path = join(module_path, "data", file_name)
    df = pd.read_csv(file_path)
    if colnames is not None:
        df = df[colnames]
    nrows, ncols = df.shape

    return {
        "name": name,
        "description": description,
        "ncols": ncols,
        "nrows": nrows,
        "data": df,
        "design": design,
        "source": source,
    }


def load_psu_frame():
    name = "PSU Frame"
    description = "A simulated census data."
    design = {}
    source = ""

    return load_dataset(
        "psu_frame.csv",
        colnames=None,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_psu_sample():
    name = "PSU Sample"
    description = "The PSU sample obtained from the simulated PSU frame."
    design = {}
    source = ""

    return load_dataset(
        "psu_sample.csv",
        colnames=None,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_ssu_sample():
    name = "SSU Sample"
    description = "The SSU sample obtained from the simulated SSU frame."
    design = {}
    source = ""

    return load_dataset(
        "ssu_sample.csv",
        colnames=None,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_nhanes2():
    colnames = [
        "stratid",
        "psuid",
        "race",
        "highbp",
        "highlead",
        "zinc",
        "diabetes",
        "finalwgt",
    ]
    name = "NHANES II Subsample"
    description = "A subset of NHANES II data. This file is not meant to be representative of NHANES II. It is just an subset to illustrate the syntax in this tutorial."
    design = {}
    source = ""

    return load_dataset(
        "nhanes2.csv",
        colnames=colnames,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_nhanes2brr():
    colnames = None
    name = "NHANES II Subsample with bootstrap weights"
    description = "A subset of NHANES II data with bootstrap weights. This file is not meant to be representative of NHANES II. It is just an subset to illustrate the syntax in this tutorial."
    design = {}
    source = ""

    return load_dataset(
        "nhanes2brr_subset.csv",
        colnames=colnames,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_nhanes2jk():
    colnames = None
    name = "NHANES II Subsample with jackknife weights"
    description = "A subset of NHANES II data with jackknife weights. This file is not meant to be representative of NHANES II. It is just an subset to illustrate the syntax in this tutorial."
    design = {}
    source = ""

    return load_dataset(
        "nhanes2jk_subset.csv",
        colnames=colnames,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_nmhis():
    colnames = None
    name = "NMIHS Subsample"
    description = "A subset of NMHIS data. This file is not meant to be representative of NMHIS. It is just an subset to illustrate the syntax in this tutorial."
    design = {}
    source = ""

    return load_dataset(
        "nmihs_subset.csv",
        colnames=colnames,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_auto():
    colnames = None
    name = "Birth Sample"
    description = "The Birth sample data."
    design = {}
    source = ""

    return load_dataset(
        "auto.csv",
        colnames=colnames,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_birth():
    colnames = None
    name = "Auto Sample"
    description = "The Auto sample data."
    design = {}
    source = ""

    return load_dataset(
        "birth.csv",
        colnames=colnames,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_county_crop():
    colnames = None
    name = "County Crop Sample"
    description = "The County Crop Areas sample data."
    design = {}
    source = ""

    return load_dataset(
        "countycrop.csv",
        colnames=colnames,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_county_crop_means():
    colnames = None
    name = "County Crop Area Means"
    description = "The County Crop Area Means data."
    design = {}
    source = ""

    return load_dataset(
        "countycrop_means.csv",
        colnames=colnames,
        name=name,
        description=description,
        design=design,
        source=source,
    )


def load_expenditure_milk():
    colnames = None
    name = "Expenditure on Milk"
    description = "The expenditure on milk data."
    design = {}
    source = ""

    return load_dataset(
        "expenditure_on_milk.csv",
        colnames=colnames,
        name=name,
        description=description,
        design=design,
        source=source,
    )


class _Dataset:
    """The base class for the datasets included on the library"""

    def __init__(self) -> None:
        self.name: str = ""
        self.description: str = ""
        self.ncols: int = 0
        self.nrows: int = 0
        self.design: dict = {}
        self.source: dict = {}
        self.data = pd.DataFrame

    def _load_data(self, file_name: str, colnames: Optional[list] = None) -> None:

        module_path = dirname(__file__)
        file_path = join(module_path, "data", file_name)
        df = pd.read_csv(file_path)
        if colnames is not None:
            df = df[colnames]
        self.nrows, self.ncols = df.shape

        self.data = df


class PSUFrame(_Dataset):
    """A class to represent the PSU frame dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "PSU Frame"
        self.description = "A simulated census data."

    def load_data(self) -> None:
        """Load psu_frame.csv file to create the data member"""

        self._load_data("psu_frame.csv")


class PSUSample(_Dataset):
    """A class to represent the PSU sample dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "PSU Sample"
        self.description = "The PSU sample obtained from the simulated PSU frame."

    def load_data(
        self,
    ) -> None:
        """Load psu_sample.csv file to create the data member"""

        self._load_data("psu_sample.csv", colnames=["cluster", "region", "psu_prob"])


class SSUSample(_Dataset):
    """A class to represent the SSU sample dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "SSU Sample"
        self.description = "The SSU sample obtained from the simulated SSU frame."

    def load_data(
        self,
    ) -> None:
        """Load ssu_sample.csv file to create the data member"""

        self._load_data("ssu_sample.csv", colnames=["cluster", "household", "ssu_prob"])


class Nhanes2(_Dataset):
    """A class to represent a subset of the NHANES II sample dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "NHANES II Subsample"
        self.description = "A subset of NHANES II data. This file is not meant to be representative of NHANES II. It is just an subset to illustrate the syntax in this tutorial."

    def load_data(
        self,
    ) -> None:
        """Load nhanes2.csv file to create the data member"""

        self._load_data(
            "nhanes2.csv",
            colnames=[
                "stratid",
                "psuid",
                "race",
                "highbp",
                "highlead",
                "zinc",
                "diabetes",
                "finalwgt",
            ],
        )


class Nhanes2brr(_Dataset):
    """A class to represent a subset of the NHANES II sample dataset with bootstrap weights

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "NHANES II Subsample with bootstrap weights"
        self.description = "A subset of NHANES II data with bootstrap weights. This file is not meant to be representative of NHANES II. It is just an subset to illustrate the syntax in this tutorial."

    def load_data(
        self,
    ) -> None:
        """Load nhanes2brr_subset.csv file to create the data member"""

        self._load_data("nhanes2brr_subset.csv")


class Nhanes2jk(_Dataset):
    """A class to represent a subset of the NHANES II sample dataset with jackknife weights

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "NHANES II Subsample with jackknife weights"
        self.description = "A subset of NHANES II data with jackknife weights. This file is not meant to be representative of NHANES II. It is just an subset to illustrate the syntax in this tutorial."

    def load_data(
        self,
    ) -> None:
        """Load nhanes2jk_subset.csv file to create the data member"""

        self._load_data("nhanes2jk_subset.csv")


class Nmihs(_Dataset):
    """A class to represent the NMIHS sample dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "NMIHS Subsample"
        self.description = "A subset of NMHIS data. This file is not meant to be representative of NMHIS. It is just an subset to illustrate the syntax in this tutorial."

    def load_data(
        self,
    ) -> None:
        """Load nmihs_subset.csv file to create the data member"""

        self._load_data("nmihs_subset.csv")


class Auto(_Dataset):
    """A class to represent the Auto sample dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Auto Sample"
        self.description = "The Auto sample data."

    def load_data(
        self,
    ) -> None:
        """Load auto.csv file to create the data member"""

        self._load_data("auto.csv", colnames=["mpg", "foreign", "y1", "y2"])


class Birth(_Dataset):
    """A class to represent the Birth sample dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Birth Sample"
        self.description = "The Birth sample data."

    def load_data(
        self,
    ) -> None:
        """Load birth.csv file to create the data member"""

        self._load_data("birth.csv", colnames=["region", "agecat", "birthcat", "pop"])


class CountyCrop(_Dataset):
    """A class to represent the County Crop Areas sample dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "County Crop Areas Sample"
        self.description = "The County Crop Areas sample data."

    def load_data(
        self,
    ) -> None:
        """Load countycrop.csv file to create the data member"""

        self._load_data(
            "countycrop.csv",
            colnames=["county_id", "corn_area", "soybeans_area", "corn_pixel", "soybeans_pixel"],
        )


class CountyCropMeans(_Dataset):
    """A class to represent the County Crop Area Means dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "County Crop Area Means"
        self.description = "The County Crop Area Means data."

    def load_data(
        self,
    ) -> None:
        """Load countycrop_means.csv file to create the data member"""

        self._load_data(
            "countycrop_means.csv",
            colnames=[
                "county_id",
                "samp_segments",
                "pop_segments",
                "ave_corn_pixel",
                "ave_soybeans_pixel",
            ],
        )


class ExpenditureMilk(_Dataset):
    """A class to represent the expenditure on milk dataset

    Args:
        _Dataset ([type]): The base class for loading datasets
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Expenditure on Milk"
        self.description = "The expenditure on milk data."

    def load_data(
        self,
    ) -> None:
        """Load expenditure_on_milk.csv file to create the data member"""

        self._load_data(
            "expenditure_on_milk.csv",
            colnames=[
                "major_area",
                "small_area",
                "samp_size",
                "direct_est",
                "std_error",
                "coef_var",
            ],
        )
