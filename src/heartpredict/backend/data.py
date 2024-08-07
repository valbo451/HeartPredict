from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing_extensions import Self


@dataclass
class NumpyMatrix:
    x: np.ndarray
    y: np.ndarray


class Column(str, Enum):
    AGE = "age"
    ANAEMIA = "anaemia"
    CREATININE_PHOSPHOKINASE = "creatinine_phosphokinase"
    DIABETES = "diabetes"
    EJECTION_FRACTION = "ejection_fraction"
    HIGH_BLOOD_PRESSURE = "high_blood_pressure"
    PLATELETS = "platelets"
    SERUM_CREATININE = "serum_creatinine"
    SERUM_SODIUM = "serum_sodium"
    SEX = "sex"
    SMOKING = "smoking"
    TIME = "time"
    DEATH_EVENT = "DEATH_EVENT"


class ProjectData:
    def __init__(self, csv: Path) -> None:
        self.df = pd.read_csv(csv)

    @classmethod
    @lru_cache
    def build(cls, csv: Path) -> Self:
        return cls(csv)


class MLData:
    def __init__(
            self, project_data: ProjectData, test_size: float, random_seed: int
    ) -> None:
        self.project_data = project_data
        self.test_size = test_size
        self.random_seed = random_seed
        self.dataset = self._get_whole_dataset()
        self.scaled_feature_matrix = MLData._scale_input_features(self.dataset.x)[0]
        self.train, self.valid = self._get_prepared_matrices()

    @classmethod
    @lru_cache
    def build(
            cls, project_data: ProjectData, test_size: float, random_seed: int
    ) -> Self:
        return cls(project_data, test_size, random_seed)

    def _get_whole_dataset(self) -> NumpyMatrix:
        """
        Prepare the whole dataset.
        Returns:
            Whole dataset as NumpyMatrix.
        """
        x = self.project_data.df.drop(columns=["DEATH_EVENT"]).values
        y = self.project_data.df["DEATH_EVENT"].values

        return NumpyMatrix(x, y)  # type: ignore

    def _get_prepared_matrices(self) -> tuple[NumpyMatrix, NumpyMatrix]:
        """
        Prepare training and validation matrices.
        Returns:
            Training and validation matrices as NumpyMatrix.
        """
        unscaled_x_train, unscaled_x_valid, y_train, y_valid = train_test_split(
            self.dataset.x,
            self.dataset.y,
            test_size=self.test_size,
            random_state=self.random_seed,
        )
        x_train, x_valid = MLData._scale_train_valid_input_features(unscaled_x_train,
                                                                    unscaled_x_valid)
        return NumpyMatrix(x_train, y_train), NumpyMatrix(x_valid, y_valid)

    @staticmethod
    def _scale_input_features(x: np.ndarray) -> tuple[np.ndarray, StandardScaler]:
        """
        Scale input features.
        Args:
            x: Input features.

        Returns:
            Scaled input features and the scaler used for scaling.
        """
        scaler = StandardScaler()
        x = scaler.fit_transform(x)

        # Save the fitted scaler needed for prediction of new data.
        output_dir = Path("results/scalers")
        output_dir.mkdir(parents=True, exist_ok=True)
        scaler_file = output_dir / "used_scaler.joblib"
        joblib.dump(scaler, scaler_file, compress=False)

        return x, scaler

    @staticmethod
    def _scale_train_valid_input_features(
            x_train: np.ndarray, x_valid: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Scale input features.
        Args:
            x_train:
            x_valid:

        Returns:
            Scaled training and validation input features.
        """
        x_train, scaler = MLData._scale_input_features(x_train)
        x_valid = scaler.transform(x_valid)  # type: ignore
        return x_train, x_valid
