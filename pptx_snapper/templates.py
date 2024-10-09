from collections import OrderedDict
from copy import deepcopy
from typing import Iterable

import pandas as pd
import numpy as np

from .snappable_object import SnappableObject
from .object_recognizer import ObjectRecognizer

class ObjectTemplate():
    def __init__(self, shape_type:str,  template_id:str):
        self.shape_type = shape_type
        self.template_id = template_id

        self._template_object = None
        self.instances = []

        self.validate_functions = [self.validate_shape_type]

    @property
    def template_object(self):
        return self._template_object

    @template_object.setter
    def template_object(self, value:SnappableObject):
        self._template_object = value

    def validate_shape_type(self,obj: SnappableObject) -> bool:
        return obj.shape_type == self.shape_type

    def add_instance(self, obj: SnappableObject, flush = False) -> bool:
        if flush:
            self.instances.clear()

        if not isinstance(obj,SnappableObject):
            return False

        if not all([lambda v:v(obj) for v in self.validate_functions if callable(v)]):
            return False

        self.instances.append(obj)
        obj.template_snap_id = self.template_id
        return True

    def create_mean_object(self) -> None:
        """
        Returns a template a 'dummy' SnappableObject
        """
        if len(self.instances) == 0:
            return

        sample_shape = deepcopy(self.instances[0].shape)

        x = np.mean([i.top for i in self.instances]).astype(int)
        y = np.mean([i.left for i in self.instances]).astype(int)

        template_object = SnappableObject(shape = sample_shape, slide_index = -1,shape_index =-1, is_template=True)
        template_object.left = x
        template_object.top = y

        self.template_object = template_object

    def __str__(self):
        return f"ObjectTemplate with {len(self.instances)} objects of type '{self.shape_type}'"

    def __repr__(self):
        return self.__str__()

class ObjectTemplates:
    templates = OrderedDict()

    @staticmethod
    def add_new_template(shape_type:str):
        template = ObjectTemplate(shape_type=shape_type, template_id=f"template_{len(ObjectTemplates.templates)}")
        ObjectTemplates.templates[template.template_id] = template
        return template

    @staticmethod
    def recognize_templates(list_of_objects: Iterable[SnappableObject] | None,
                            object_recognizer: ObjectRecognizer,
                            min_num_of_re_occurrences:int = 2):
        """
        Method to automatically recognize repeated object (with the same type, and some criteria)
        :param list_of_objects: List of SnappableObjects or None. If None, all initialized SanppableObjects will be used.
        :param object_recognizer: ObjectRecognizer that validates object similarity
        :param min_num_of_re_occurrences: Minimal number of re-occurrence.
        :return:
        """

        if not list_of_objects:
            list_of_objects = SnappableObject.catalog

        list_of_objects = sorted(list_of_objects,key= lambda x: (x.slide_index,x.shape_index))

        df = pd.DataFrame([OrderedDict(
                                       id = o.full_id,
                                       slide_index=o.slide_index,
                                       shape_index=o.shape_index,
                                       shape_type=o.shape_type,
                                       width=o.width,
                                       height=o.height,
                                       is_assigned_to_template=False,
                                       is_touched = False,
                                       object_reference=o) for o in list_of_objects])

        assert df["id"].is_unique

        # shape type needs to be exact same
        types = sorted(df["shape_type"].unique().tolist())

        template_candidates = []

        for shape_type in types:
            _df = df[df["shape_type"] == shape_type]
            # create pairs

            pivot_index = _df.index[0]

            while True:
                pivot_object_row = _df.loc[pivot_index]
                pivot_object = pivot_object_row.get('object_reference')

                _target_objects = _df[~(_df["is_assigned_to_template"] | _df["is_touched"]) & (_df.index != pivot_index)]
                if len(_target_objects) == 0:
                    break
                target_objects = _target_objects["object_reference"].tolist()

                matching_objects = object_recognizer.search_similar_objects(pivot_object, target_objects)

                if len(matching_objects) > 0:
                    matching_object_ids = [mo.full_id for mo in matching_objects]

                    if len(matching_objects) > min_num_of_re_occurrences:
                        _df.loc[_df["id"].isin(matching_object_ids),"is_assigned_to_template"] = True
                        _df.loc[pivot_index,"is_assigned_to_template"] = True
                        template_candidates.append([pivot_object] + matching_objects)
                    else:
                        _df.loc[_df["id"].isin(matching_object_ids), "is_touched"] = True


                _df.loc[pivot_index,"is_touched"] = True

                if _df.apply(lambda x: x["is_assigned_to_template"] or x["is_touched"],axis = 1).all():
                    break

                untouched = _df.apply(lambda x: not(x["is_assigned_to_template"] or x["is_touched"]),axis = 1)
                untouched_indices = untouched.index.tolist()
                is_untouched = untouched.tolist()
                if all([not it for it in is_untouched]):
                    break
                pivot_index = untouched_indices[is_untouched.index(True)]

        for template_candidate_index, template_candidate in enumerate(template_candidates):
            shape_type = template_candidate[0].shape_type
            template = ObjectTemplates.add_new_template(shape_type)
            for instance_index, instance in enumerate(template_candidate):
                template.add_instance(instance)
                instance.template_snap_id = template.template_id
            template.create_mean_object()
        return True