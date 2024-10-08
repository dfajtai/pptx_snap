from copy import  deepcopy
from collections import OrderedDict

import numpy as np
import pandas as pd

from .snappable_object import SnappableObject
from .slide import Slide


class SnappableTemplate():
    def __init__(self, shape_type:str, sizes:np.ndarray, template_id:str):
        self.shape_type = shape_type
        self.sizes = sizes
        self.template_id = template_id

        self._template_object = None
        self.instances = []

        self.validate_functions = [self.validate_sizes, self.validate_shape_type]

    @property
    def template_object(self):
        return self._template_object

    @template_object.setter
    def template_object(self, value:SnappableObject):
        self._template_object = value

    def validate_shape_type(self,obj: SnappableObject) -> bool:
        return obj.shape_type == self.shape_type

    def validate_sizes(self,obj: SnappableObject, tolerance: float = 0.01) -> bool:
        if not np.allclose(self.sizes.shape,obj.sizes.shape): return False
        fraction = np.true_divide(obj.sizes,self.sizes)
        return np.allclose(fraction,np.ones_like(fraction),atol=tolerance)

    def add_instance(self, obj: SnappableObject, flush = False) -> None:
        if flush:
            self.instances.clear()

        if not isinstance(obj,SnappableObject):
            return

        if not all([lambda v:v(obj) for v in self.validate_functions if callable(v)]):
            return

        self.instances.append(obj)
        obj.template_snap_id = self.template_id

    def get_mean_object(self) -> None| SnappableObject:
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

class ObjectTemplates:
    templates = OrderedDict()

    @staticmethod
    def add_new_template(shape_type:str, sizes:np.ndarray):
        template = SnappableTemplate(shape_type=shape_type, sizes=sizes, template_id=f"template_{len(ObjectTemplates.templates)}")
        ObjectTemplates.templates[template.template_id] = template
        return template


class ObjectRecognizer:
    """
    Class implementing methods to automatically recognize repeated objects
    """

    @staticmethod
    def search_template_objects(slide_list: list[Slide]):
        objects = []
        for s in slide_list:
            objects.extend(s.snappable_objects)


        df = pd.DataFrame([OrderedDict(slide_index = o.slide_index,
                                       shape_index = o.shape_index,
                                       shape_type = o.shape_type,
                                       width = o.width,
                                       height = o.height,

                                       is_assigned_to_template = False,
                                       object = o) for o in objects])


        # shape type needs to be exact same
        types = df["shape_type"].unique().tolist()
        for shape_type in types:
            _df = df[df["shape_type"] == shape_type]

            print(_df)