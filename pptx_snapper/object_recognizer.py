from copy import  deepcopy
from collections import OrderedDict

import numpy as np

from .snappable_object import SnappableObject
from .slide import Slide


class SnappableTemplate():
    def __init__(self, shape_type:str, sizes:np.ndarray, template_id:str):
        self.shape_type = shape_type
        self.sizes = sizes
        self.template_id = template_id

        self._template_object = None
        self.instances = []

    @property
    def template_object(self):
        return self._template_object

    @template_object.setter
    def template_object(self, value:SnappableObject):
        self._template_object = value

    def _validate_shape_type(self,shape_type:str) -> bool:
        return shape_type == self.shape_type

    def _validate_sizes(self,sizes:np.ndarray) -> bool:
        return np.array_equiv(sizes,self.sizes)

    def add_instance(self, obj: SnappableObject, flush = False) -> None:
        if flush:
            self.instances.clear()

        if not isinstance(obj,SnappableObject):
            return

        if not (self._validate_sizes(obj.sizes) and self._validate_shape_type(obj.shape_type)):
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
    pass

