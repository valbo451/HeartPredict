import importlib.metadata
from dataclasses import dataclass, field
from enum import Enum

import logging
from logging import Logger, getLogger
from pathlib import Path
from typing import Optional

import typer
from heartpredict.backend.correlation import CorrelationBackend, CorrelationMethod
from heartpredict.backend.data import Column, MLData, ProjectData
from heartpredict.backend.ml import MLBackend
from heartpredict.backend.survival import SurvivalBackend
from heartpredict.backend.descriptive import DescriptiveBackend
from heartpredict.backend.descriptive import BoolColumn, DiscreteColumn 
from rich import print
from typing_extensions import Annotated


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class State:
    csv: str = "data/heart_failure_clinical_records.csv"
    # use root logger so we can simply use the modified one in other modules
    logger: Logger = field(default_factory=lambda: getLogger())


app = typer.Typer(no_args_is_help=True)
state = State()


@app.callback()
def set_path(
        csv: str = "data/heart_failure_clinical_records.csv",
        loglevel: LogLevel = LogLevel.INFO
) -> None:
    state.csv = csv

    if loglevel == LogLevel.DEBUG:
        state.logger.setLevel(logging.DEBUG)
    elif loglevel == LogLevel.INFO:
        state.logger.setLevel(logging.INFO)
    elif loglevel == LogLevel.WARNING:
        state.logger.setLevel(logging.WARNING)
    elif loglevel == LogLevel.ERROR:
        state.logger.setLevel(logging.ERROR)
    elif loglevel == LogLevel.CRITICAL:
        state.logger.setLevel(logging.CRITICAL)


@app.command()
def version() -> None:
    print(importlib.metadata.version("heartpredict"))


@app.command()
def test() -> None:
    print("test successful")


@app.command()
def train_model_for_classification(
        seed: Annotated[int, typer.Option(help="Random seed for reproducibility.")] = 42
) -> None:
    project_data = ProjectData.build(Path(state.csv))
    data = MLData.build(project_data, 0.2, seed)
    backend = MLBackend(data)
    backend.classification_for_different_classifiers()


@app.command()
def train_model_for_regression(
        seed: Annotated[int, typer.Option(help="Random seed for reproducibility.")] = 42
) -> None:
    project_data = ProjectData.build(Path(state.csv))
    data = MLData.build(project_data, 0.2, seed)
    backend = MLBackend(data)
    backend.regression_for_different_regressors()


@app.command()
def create_kaplan_meier_plot(
        seed: Annotated[
            int, typer.Option(help="Random seed for reproducibility.")
        ] = 42,
        regressor: Annotated[
            Optional[str], typer.Option(help="Path to regressor model.")
        ] = None,
) -> None:
    project_data = ProjectData.build(Path(state.csv))
    ml_data = MLData.build(project_data, 0.2, seed)
    survival_backend = SurvivalBackend(ml_data)
    if regressor is None:
        ml_backend = MLBackend(ml_data)
        regressor = str(ml_backend.regression_for_different_regressors().model_file)
    survival_backend.create_kaplan_meier_plot_for(Path(regressor))


@app.command(name="cc")
def single_correlation(
        column: Annotated[Column, typer.Option()],
        method: Annotated[CorrelationMethod, typer.Option()] = CorrelationMethod.PEARSON
) -> None:
    data = ProjectData.build(Path(state.csv))
    backend = CorrelationBackend.build(data)
    print(backend.get_column_correlation_to_death_event(column, method))


@app.command(name="cm")
def multiple_correlation(
        method: Annotated[CorrelationMethod, typer.Option()] = CorrelationMethod.PEARSON
) -> None:
    data = ProjectData.build(Path(state.csv))
    backend = CorrelationBackend.build(data)
    print(backend.get_correlation_matrix(method))


@app.command(name="bstat")
def boolean_statistic(
    bool_col: Annotated[BoolColumn, ...]
    ) -> None:
    if not isinstance(bool_col, BoolColumn):
        raise ValueError("Input should be boolean column")
    descriptive = DescriptiveBackend(state.csv)
    stats = descriptive.calculate_boolean_statistics(bool_col)
    print(stats)


@app.command(name="dstat")
def discrete_statistic(
    disc_col: Annotated[DiscreteColumn, ...]
    ) -> None:
    if not isinstance(disc_col, DiscreteColumn):
        raise ValueError("Input should be discrete column")
    descriptive = DescriptiveBackend(state.csv)
    stats = descriptive.calculate_discrete_statistics(disc_col)
    print(stats)
