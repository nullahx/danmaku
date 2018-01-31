import json
from json.decoder import JSONDecodeError


def format_json_to_pytype(j_data):
    """
    格式化json数据为python可识别的数据类型
    :param j_data: bytes格式的json原始数据
    :return:  转换的python数据
    """
    data = json.loads(j_data)
    return data