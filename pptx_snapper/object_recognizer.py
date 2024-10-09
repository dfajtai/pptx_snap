from collections.abc import Iterable
from typing import Callable, List
import inspect

from .snappable_object import SnappableObject


class ObjectRecognizer:
    """
    Class implementing methods to automatically recognize repeated objects
    """

    def __init__(self):
        self.match_validate_functions: List[Callable[[SnappableObject,SnappableObject], bool]] = []

    def add_validator(self, validator: Callable[[SnappableObject, SnappableObject], bool]):
        """
        Add a validation function to the list if it matches the required signature.
        Raises a TypeError if the validator does not match the expected signature.
        """
        if not callable(validator):
            raise TypeError("Validator must be callable")

        # Use inspect to check that the function has exactly one parameter of the correct type
        sig = inspect.signature(validator)
        parameters = list(sig.parameters.values())

        if len(parameters) != 2:
            raise TypeError("Validator must take exactly two parameter")

        # Check that both parameters have the expected annotation of 'SnappableObject'
        for param in parameters:
            if param.annotation is not SnappableObject:
                raise TypeError("Both validator parameters must be of type 'SnappableObject'")

        # Add the validator to the list if it passes all checks
        self.match_validate_functions.append(validator)

    def validate(self, ref_obj: SnappableObject, target_obj: SnappableObject) -> List[bool]:
        """
        Run all validators on a given pair of reference and target SnappableObject and return a list of boolean results.
        """
        return [validator(ref_obj,target_obj) for validator in self.match_validate_functions]


    def search_similar_objects(self, ref_object: SnappableObject, target_objects: Iterable[SnappableObject]) -> List[SnappableObject]:
        return [o for o in target_objects if all(self.validate(ref_object,o))]


    @staticmethod
    def get_size_recognizer(size_threshold: float = 1.0) -> 'ObjectRecognizer':
        recognizer = ObjectRecognizer()

        def exact_size_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.size_match_score(target) >= size_threshold

        def type_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.shape_type == target.shape_type

        recognizer.add_validator(type_match)
        recognizer.add_validator(exact_size_match)

        return recognizer

    @staticmethod
    def get_dice_recognizer(dice_threshold: float = 1.0) -> 'ObjectRecognizer':
        recognizer = ObjectRecognizer()

        def exact_size_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.dice_coefficient(target) >= dice_threshold

        def type_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.shape_type == target.shape_type

        recognizer.add_validator(type_match)
        recognizer.add_validator(exact_size_match)

        return recognizer

    @staticmethod
    def get_size_with_dice_recognizer(size_threshold: float = 1.0,dice_threshold: float = 1.0) -> 'ObjectRecognizer':
        recognizer = ObjectRecognizer()

        def exact_size_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.size_match_score(target) >= size_threshold

        def dice_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.dice_coefficient(target) >= dice_threshold

        def type_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.shape_type == target.shape_type

        recognizer.add_validator(type_match)
        recognizer.add_validator(exact_size_match)
        recognizer.add_validator(dice_match)

        return recognizer

    @staticmethod
    def get_exact_recognizer() -> 'ObjectRecognizer':
        recognizer = ObjectRecognizer()

        def exact_size_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.size_match_score(target) == 1.0

        def dice_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.dice_coefficient(target) == 1.0

        def type_match(ref: SnappableObject, target: SnappableObject) -> bool:
            return ref.shape_type == target.shape_type

        recognizer.add_validator(type_match)
        recognizer.add_validator(exact_size_match)
        recognizer.add_validator(dice_match)

        return recognizer