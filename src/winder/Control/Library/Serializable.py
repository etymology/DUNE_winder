###############################################################################
# Name: Serializable.py
# Uses: Interface class to define an object that can be de/serialized into XML.
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from abc import ABCMeta, abstractmethod

class Serializable :
  # Make class abstract.
  __metaclass__ = ABCMeta

  #---------------------------------------------------------------------
  @abstractmethod
  def serialize( self, xml ) :
    """
    Turn this object into an XML node.

    Args:
      xml: Instance of xml.dom.minidom.Document.

    Returns:
      Must return an XML node with the data from this object.
    """
    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def unserialize( self, node ) :
    """
    Take an XML node and load values into this object.

    Args:
      node: Instance of xml.dom.minidom.Node.

    Returns:
      True if there was an error, False if not.
    """
    pass
