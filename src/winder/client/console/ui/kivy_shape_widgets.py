from kivy.uix.widget import Widget
from .kivy_mixins import BackgroundShapeMixin, BackgroundEllipseMixin, BackgroundCircleMixin, BackgroundRectangleMixin

class ShapeWidget( BackgroundShapeMixin, Widget ):
   pass

class EllipseWidget( BackgroundEllipseMixin, Widget ):
   pass

class CircleWidget( BackgroundCircleMixin, Widget ):
   pass

class RectangleWidget( BackgroundRectangleMixin, Widget ):
   pass
