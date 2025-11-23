from enum import Enum


class BPCategory(str, Enum):
    NORMAL = "NORMAL"
    ELEVADO = "ELEVADO"
    PREHIPERTENSION = "PREHIPERTENSION"
    HIPERTENSION = "HIPERTENSION"


def classify_bp(systolic: int, diastolic: int) -> BPCategory:
    if systolic >= 140 or diastolic >= 90:
        return BPCategory.HIPERTENSION
    if 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return BPCategory.PREHIPERTENSION
    if 120 <= systolic <= 129 and diastolic < 80:
        return BPCategory.ELEVADO
    return BPCategory.NORMAL
