"""
配置路径工具文件，为工程提供绝对路径
"""
import os

#配置项目文件根目录 后续可以用 ./文件名.txt等方便配置相对路径
def get_project_root() -> str :     #一级一级获取根目录
    #获取当前文件绝对路径
    current_file = os.path.abspath(__file__)    #传入打算配置的文件路径（文件夹名/文件名..）自动创建
    #获取文件的文件夹目录
    current_dir = os.path.dirname(current_file)
    #获取根目录
    root_project = os.path.dirname(current_dir)
    return root_project

#传入相对路径 获取绝对路径
def get_abs_path(relative_path:str) -> str :
    project = get_project_root()
    #相对目录+根目录 = 绝对路径
    return os.path.join(project, relative_path)

# if __name__ == '__main__':
#     print(get_abs_path(relative_path="config/config.txt"))
