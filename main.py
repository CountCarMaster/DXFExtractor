import yaml
import argparse
import os
from src.utils import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="DWGExtractor")
    parser.add_argument('--file-path', type=str, default='./data/2.dxf')
    parser.add_argument('--yaml-path', type=str, default='./config.yaml')
    args = parser.parse_args()

    with open(args.yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)

    if os.path.exists(args.file_path) == False:
        raise FileError('The file does not exist')

    ground, floodY, pierList = dataLoad(args.file_path, config)
    pierList = sorted(pierList, key=lambda pier: pier.xMin)
    pierList = ground.is_abovePier(pierList)
    pierList, ground = changeCoordinate(pierList, ground)
    saveData(ground, pierList, config)