import yaml


class Config:
    def __init__(self):
        with open("./config/config.yaml", 'r') as f:
            self.config = yaml.load(f)
