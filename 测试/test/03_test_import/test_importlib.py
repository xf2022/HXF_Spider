import importlib
import os

if __name__ == '__main__':
    os.chdir(r'D:\programme\python\HXF_Spider\测试\test')
    obj_class = importlib.import_module('测试.test.03_test_import.test_class')
    # obj = obj_class()
    list = obj_class.__dir__()
    # obj.run()
    getattr(obj_class, 'TestClass')
    pass