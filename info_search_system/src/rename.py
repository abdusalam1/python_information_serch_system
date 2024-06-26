import os

def rename_txt_files(directory):
    # 获取目录中的所有文件
    files = os.listdir(directory)
    # 过滤出所有的txt文件
    txt_files = [f for f in files if f.endswith('.txt')]

    # 对txt文件进行排序（可选，如果你想按某种顺序进行重命名）
   # txt_files.sort()

    # 初始化文件计数
    count = 1

    # 遍历每个txt文件并重命名
    for txt_file in txt_files:
        # 构建旧文件名和新文件名
        old_file_path = os.path.join(directory, txt_file)
        new_file_name = f"新闻{count}.txt"
        new_file_path = os.path.join(directory, new_file_name)
        while os.path.exists(new_file_path):
            count+=1
            new_file_name = f"新闻{count}.txt"
            new_file_path = os.path.join(directory, new_file_name)
        # 重命名文件
        os.rename(old_file_path, new_file_path)
        print(f"Renamed {old_file_path} to {new_file_path}")

        # 计数器加一
        count += 1

if __name__ == "__main__":
    # 定义数据路径
    data_path = 'src/files/News'
    
    # 调用函数重命名txt文件
    rename_txt_files(data_path)
