import inspect


def call_method(obj, method_name, *args, **kwargs):
    """ 使用反射调用对象的方法 """
    if hasattr(obj, method_name):
        method = getattr(obj, method_name)
        return method(*args, **kwargs)
    else:
        raise AttributeError(f"{obj.__class__.__name__} 对象没有方法 {method_name}")


def get_attribute(obj, attribute_name):
    """ 使用反射获取对象的属性 """
    if hasattr(obj, attribute_name):
        return getattr(obj, attribute_name)
    else:
        raise AttributeError(f"{obj.__class__.__name__} 对象没有属性 {attribute_name}")


def create_instance(class_name, *args, **kwargs):
    """ 根据类名动态创建对象实例 """
    try:
        module = __import__(class_name)
        class_obj = getattr(module, class_name)
        return class_obj(*args, **kwargs)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"无法导入或找到类 {class_name}: {str(e)}")


def get_method_return_type(method_obj):
    # 获取方法的签名信息
    signature = inspect.signature(method_obj)
    # 获取返回值的类型注释
    return_annotation = signature.return_annotation
    return return_annotation


def has_async_method(cls, method_name) -> bool:
    # 获取类的方法
    method = getattr(cls, method_name, None)
    # 检查方法是否存在并且是异步的
    return inspect.iscoroutinefunction(method)
