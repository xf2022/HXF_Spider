import yaml


def get_config():
    path = r'D:\programme\python\HXF_Spider\setting.yml'
    with open(path, 'r', encoding='utf-8') as file_config:
        return [config for config in yaml.load_all(file_config, Loader=yaml.FullLoader)]


comm_config, test_config, dev_config, master_config = get_config()

# 数据库配置
MYSQL_CONFIG = {
    'host': dev_config['MYSQL_CONFIG']['HOST'],
    'port': dev_config['MYSQL_CONFIG']['PORT'],
    'user': dev_config['MYSQL_CONFIG']['USER'],
    'password': dev_config['MYSQL_CONFIG']['PASSWORD'],
    'database': dev_config['MYSQL_CONFIG']['DBNAME'],
    'charset': dev_config['MYSQL_CONFIG']['CHARSET'],
}

PROCESS_COUNT = comm_config['PROCESS_COUNT']
LOGGING_FILENAME = comm_config['LOGGING_FILENAME']
DOMNLOAD_PATH = comm_config['DOMNLOAD_PATH']

if __name__ == '__main__':
    test_config, dev_config, master_config = get_config()
    print(dev_config['MYSQL_CONFIG']['TYPE'])
