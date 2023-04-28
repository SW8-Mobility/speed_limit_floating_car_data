from __future__ import annotations
from enum import Enum


# enum to represent our features
class Feature(Enum):
    OSM_ID = "osm_id"
    COORDINATES = "coordinates"
    SPEEDS = "speeds"
    DISTANCES = "distances"
    MEANS = "means"
    AGGREGATE_MEAN = "aggregate_mean"
    MINS = "mins"
    AGGREGATE_MIN = "aggregate_min"
    MAXS = "maxs"
    AGGREGATE_MAX = "aggregate_max"
    ROAD_TYPE = "road_type"
    ROLLING_AVERAGES = "rolling_averages"
    LEVEL = "level"
    MEDIANS = "medians"
    AGGREGATE_MEDIAN = "aggregate_median"
    VCR = "vcr"
    DAY_OF_WEEK = "day_of_week"
    TIME_GROUP = "time_group"
    SPEED_LIMIT_TARGET = "speed_limit_target"
    SPEED_LIMIT_PREDICTED = "speed_limit_predicted"

    # vejman features
    CPR_VEJNAVN = "cpr_vejnavn"
    HAST_GENEREL_HAST = "hast_generel_hast"
    HAST_GAELDENDE_HAST = "hast_gaeldende_hast"
    VEJSTIKLASSE = "vejstiklasse"
    VEJTYPESKILTET = "vejtypeskiltet"
    HAST_SENEST_RETTET = "hast_senest_rettet"
    TARGET = "target"

    @staticmethod
    def array_features() -> FeatureList:
        """
        returns a list of the of the array features.
        """
        return Feature.array_1d_features() + Feature.array_2d_features()

    @staticmethod
    def array_1d_features() -> FeatureList:
        """
        returns a list of the features where the type is 1d-arrays.
        """
        return FeatureList(
            [
                Feature.MEANS,
                Feature.MINS,
                Feature.MAXS,
                Feature.MEDIANS,
            ]
        )

    @staticmethod
    def array_2d_features() -> FeatureList:
        """
        returns a list of features where the type is 2d arrays.
        """
        return FeatureList(
            [
                Feature.COORDINATES,
                Feature.DISTANCES,
                Feature.SPEEDS,
                Feature.ROLLING_AVERAGES,
                Feature.VCR,
            ]
        )

    @staticmethod
    def categorical_features() -> FeatureList:
        """
        returns a list of features where the feature is categorical.
        """
        return FeatureList(
            [
                Feature.HAST_SENEST_RETTET,
                Feature.VEJSTIKLASSE,
                Feature.VEJTYPESKILTET,
            ]
        )

    def __str__(self) -> str:
        return self.value


class FeatureList(list):
    def __init__(self, features: list[Feature]):
        self.features = features
        self.features_names = [f.value for f in features]

    def __sub__(self, other):
        if isinstance(other, FeatureList):
            return FeatureList([x for x in self.features if x not in other.features])
        else:
            raise NotImplemented()

    def __add__(self, other):
        if isinstance(other, FeatureList):
            return FeatureList(self.features + other.features)
        else:
            raise NotImplemented()

    def __iter__(self):
        return self.features_names.__iter__()

    def __repr__(self):
        return self.features_names.__repr__()

    def not_in(self, feature_list: list[str]) -> list[str]:
        return [f for f in feature_list if f not in self.features_names]
