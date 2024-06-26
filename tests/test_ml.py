from typing import Callable

import pytest
from heartpredict.backend.data import MLData
from heartpredict.backend.ml import MLBackend, load_model

from sklearn.metrics import root_mean_squared_error


def test_load_pretrained_classifiers_seed_42(
        ml_data_func: Callable[..., MLData]
) -> None:
    model_dir = "results/trained_models/classifier"
    data = ml_data_func()
    best_decision_tree_score = 0.859
    decision_tree = load_model(
        f"{model_dir}/DecisionTreeClassifier_model_{data.random_seed}.joblib"
    )
    assert decision_tree.score(data.valid.x, data.valid.y) == best_decision_tree_score

    best_random_forest_score = 0.992
    random_forest = load_model(
        f"{model_dir}/RandomForestClassifier_model_{data.random_seed}.joblib"
    )
    assert random_forest.score(data.valid.x, data.valid.y) == best_random_forest_score

    best_knn_score = 0.977
    knn = load_model(
        f"{model_dir}/KNeighborsClassifier_model_{data.random_seed}.joblib"
    )
    assert knn.score(data.valid.x, data.valid.y) == best_knn_score

    best_lda_score = 0.839
    lda = load_model(
        f"{model_dir}/LinearDiscriminantAnalysis_model_{data.random_seed}.joblib"
    )
    assert lda.score(data.valid.x, data.valid.y) == best_lda_score

    best_qda_score = 0.829
    qda = load_model(
        f"{model_dir}/QuadraticDiscriminantAnalysis_model_{data.random_seed}.joblib"
    )
    assert qda.score(data.valid.x, data.valid.y) == best_qda_score

    with pytest.raises(FileNotFoundError) as exc_info:
        load_model("CoolModel.joblib")
    assert (
            str(exc_info.value) == "[Errno 2] No such file or directory: "
                                   "'CoolModel.joblib'"
    )


def test_train_model_for_classification_seed_42(
        ml_data_func: Callable[..., MLData],
) -> None:
    data = ml_data_func(random_seed=42)
    backend = MLBackend(data)
    path_to_best_model = backend.classification_for_different_classifiers().model_file

    best_model_accuracy = 0.992
    best_model = load_model(path_to_best_model)
    assert (
            best_model.score(backend.data.valid.x, backend.data.valid.y)
            == best_model_accuracy
    )


def test_load_pretrained_regressors_seed_42(
        ml_data_func: Callable[..., MLData]
) -> None:
    model_dir = "results/trained_models/regressor"
    data = ml_data_func()

    best_logistic_regression_score = 0.386
    logistic_regressor = load_model(
        f"{model_dir}/LogisticRegression_model_{data.random_seed}.joblib"
    )
    error = round(root_mean_squared_error(
        data.valid.y,
        logistic_regressor.predict(data.valid.x)),
        3)
    assert error == best_logistic_regression_score

    best_logistic_regression_cv_score = 0.386
    logistic_regressor_cv = load_model(
        f"{model_dir}/LogisticRegressionCV_model_{data.random_seed}.joblib"
    )

    error = round(root_mean_squared_error(
        data.valid.y,
        logistic_regressor_cv.predict(data.valid.x)),
        3)
    assert error == best_logistic_regression_cv_score


def test_train_model_for_regressionn_seed_42(
        ml_data_func: Callable[..., MLData],
) -> None:
    data = ml_data_func(random_seed=42)
    backend = MLBackend(data)
    path_to_best_model = backend.regression_for_different_regressors().model_file

    best_model_rmse = 0.386
    best_model = load_model(path_to_best_model)
    error = round(root_mean_squared_error(
        data.valid.y,
        best_model.predict(data.valid.x)),
        3)
    assert error == best_model_rmse
