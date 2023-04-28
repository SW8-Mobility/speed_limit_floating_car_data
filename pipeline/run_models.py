from datetime import datetime
from functools import reduce
import numpy as np
from typing import Any, Callable
import joblib
from pipeline.models.models import (
    create_mlp_grid_search,
    random_forest_regressor_gridsearch,
    xgboost_classifier_gridsearch,
    logistic_regression_gridsearch,
    statistical_model,
)
from pipeline.models.utils.model_enum import Model
import pipeline.models.utils.scoring as scoring
from pipeline.models.models import (
    create_mlp_grid_search,
    random_forest_regressor_gridsearch,
    xgboost_classifier_gridsearch,
    logistic_regression_gridsearch,
)
from pipeline.preprocessing.compute_features.feature import Feature
from sklearn.model_selection import train_test_split
import pandas as pd  # type: ignore
from keras_preprocessing.sequence import pad_sequences

from pipeline.preprocessing.sk_formatter import SKFormatter

# Model = dict[str, Model]
Params = dict[str, Any]
Models = dict[Model, Params]


def train_models_save_results(
    x_train, y_train
) -> dict[Model, Any]:  # TODO: update docstring
    """
    Creates every model from models.py, fits them, saves
    them to pickle, saves best params and returns dict
    mapping model names to the fitted model.

    use joblib for saving models to file:
    # https://scikit-learn.org/stable/model_persistence.html

    Args:
        x_train: Training dataset
        y_train: Target for training

    Returns: dictionary of model name to trained model model
    """

    # define a list of models and their corresponding grid search functions (from models.py)
    model_jobs = [
        (Model.MLP, create_mlp_grid_search),
        (Model.RF, random_forest_regressor_gridsearch),
        (Model.XGB, xgboost_classifier_gridsearch),
        (Model.LOGREG, logistic_regression_gridsearch),
        # (Model.STATMODEL, statistical_model), # TODO: Does not work currently...
    ]

    models: dict[str, Any] = {}  # model name to the trained model

    with open("models/training_results.txt", "a") as best_model_params_f:
        # loop through each model and perform grid search
        for model_name, model_func in model_jobs:
            best_model, best_params = model_func(x_train, y_train)
            best_model_params_f.write(  # save the best params to file
                f"\nmodel: {model_name.value}, params: {best_params}"
            )
            joblib.dump(  # save the model as joblib file
                best_model, f"{model_name.value}_best_model.joblib"
            )
            models[model_name] = best_model

    return models


def append_predictions_to_df(
    df: pd.DataFrame, predictions: np.ndarray, model: Model
) -> pd.DataFrame:
    """
    Save predictions made to dataframe.
    @param df: Dataframe to append predictions to.
    @param predictions: Predictions made by a model
    @param model: Which model made the predictions
    @return: Annoted dataframe
    """

    # The first test_size number of rows are used for testing
    # ex. 1000 row dataframe might have a test_size of 200 rows
    # to append the 200 rows of predictions, padding is needed
    # so that it is the same length.
    # so, pad to same length and append.
    predictions_padded = np.pad(
        predictions,
        (0, len(df) - len(predictions)),
        mode="constant",
        constant_values=None,
    )
    col_name = f"{model.value}_preds"
    df[col_name] = pd.Series(predictions_padded)
    return df


def test_models(
    models: dict[Model, Any], x_test: np.ndarray, y_test: np.ndarray, df: pd.DataFrame
) -> dict[str, dict]:
    """
    Tests all the models. Will return scoring metrics for each models predictions.

    Args:
        models (dict[Model, Any]): The dictionary of the best models after fitting on the train data.
        x_test (np.ndarray): The input test data from the train-test split
        y_test (np.ndarray): The target test data from the train-test split
    """
    per_model_metrics: dict[str, dict] = {}

    # initialize scored_predictions with y_test
    for model_name, model in models.items():
        # predict
        if model_name.value in Model.regression_models_names():
            y_pred = scoring.classify_with_regressor(model, x_test)
        else:
            y_pred = model.predict(x_test)

        append_predictions_to_df(df, y_pred)

        per_model_metrics[model_name.value] = scoring.score_model(y_test, y_pred)

    return per_model_metrics


def save_metrics(metrics_dict: dict[str, dict], save_to_folder: str) -> None:
    """
    Save the metrics from model predictions to a file.
    Will name file based on time created.

    @param metrics_dict: dict from model name to metrics
    @param save_to_folder: Folder to save file
    @return: None
    """
    date = datetime.today().strftime("%d%m%y_%H%M")
    filename = f"{save_to_folder}/{date}_metrics.txt"
    with open(filename, "w+") as f:
        f.write("model, mae, mape, mse, rmse, r2, ev\n")  # header
        for model, metrics in metrics_dict.items():
            f.write(f"{model}")
            for name, val in metrics.items():
                f.write(f", {val}")
            f.write("\n")


def main():
    formatter = SKFormatter(
        "/share-files/pickle_files_features_and_ground_truth/2012.pkl"
    )
    df = formatter.df
    x_train, x_test, y_train, y_test = formatter.generate_train_test_split()
    print("formatted. Training...")
    models = train_models_save_results(x_train, y_train)
    metrics = test_models(models, x_test, y_test, df)
    save_metrics(metrics, "/share-files/model_scores")

if __name__ == "__main__":
    main()