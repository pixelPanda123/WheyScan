from enum import Enum


class ProductKind(str, Enum):
    PROTEIN = "protein"

    CREATINE = "creatine"

    ACCESSORY = "accessory"

    VITAMIN = "vitamin"

    PRE_WORKOUT = "pre_workout"

    BUNDLE = "bundle"

    UNKNOWN = "unknown"