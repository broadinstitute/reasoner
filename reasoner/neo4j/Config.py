import yaml
import os

class Config:
    def __init__(self):
        configfile = os.path.join(os.path.dirname(__file__), 'config/config.yaml')
        with open(configfile, 'r') as f:
            self.config = yaml.load(f)
