from abc import ABC, abstractmethod
import logging

class BaseModule(ABC):
  def __init__(self):
    # Dynamically set the name based on the child class (e.g., SecurityModule)
    name = self.__class__.__name__
    self.logger = logging.getLogger(name)
    self.logger.setLevel(logging.INFO)
    
    # Add a simple console handler so you see the logs in your terminal
    if not self.logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] [%(name)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

  @abstractmethod
  def run_logic(self, *args, **kwargs):
    """Forces every module to implement its own core logic."""
    pass