from pathlib import Path
import argparse
import json
import re


def scan_java_files(project_path: str) -> list[Path]:
    """
    扫描一个 Java 项目文件夹，找到里面所有 .java 文件。

    参数:
        project_path: Java 项目的路径，例如 data/sample_java_project

    返回:
        一个列表，里面存放所有 .java 文件的路径
    """

    # 把字符串路径变成 Path 对象，方便后面处理路径
    root = Path(project_path)

    # 检查路径是否存在
    if not root.exists():
        raise FileNotFoundError(f"Project path does not exist: {root}")

    # 检查路径是不是文件夹
    if not root.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {root}")

    # 递归查找所有 .java 文件
    java_files = list(root.rglob("*.java"))

    return java_files


def parse_java_file(path: Path) -> dict:
    """
    从一个 Java 文件中提取基础信息。

    目前只做粗提取，不追求完美。
    提取内容包括:
    1. import 语句
    2. class 名字
    3. method 名字

    参数:
        path: 一个 .java 文件路径

    返回:
        一个字典，里面保存这个 Java 文件的信息
    """

    # 读取 Java 文件内容
    # errors="ignore" 表示如果遇到无法识别的字符，就跳过，不让程序崩掉
    text = path.read_text(encoding="utf-8", errors="ignore")

    # 提取 import
    # 例如:
    # import java.util.List;
    # 会提取出:
    # java.util.List
    imports = re.findall(r"import\s+([\w\.]+);", text)

    # 提取 class 名字
    # 例如:
    # public class UserService {
    # 会提取出:
    # UserService
    classes = re.findall(r"\bclass\s+(\w+)", text) 
    #代码解读： \b 表示单词边界，确保我们匹配的是一个完整的单词 "class"。
    # \s+ 表示一个或多个空白字符，确保 "class" 和类名之间至少有一个空格。
    # (\w+) 表示一个或多个字母、数字或下划线，这部分会被捕获为类名。        

    # 提取方法名
    # 这个正则只处理比较普通的方法声明，例如:
    # public void save(User user)
    # private String getName()
    # public static int add(int a, int b)
    #
    # 它不完美，但 Day04 先够用。
    methods = re.findall(
        r"(?:public|private|protected)?\s*" # 可选的访问修饰符
        r"(?:static\s+)?" # 可选的 static 关键字
        r"(?!public\b|private\b|protected\b|static\b)" # 确保返回类型不是访问修饰符或 static
        r"[\w\<\>\[\]]+\s+" # 返回类型，可能是基本类型，也可能是泛型
        r"(\w+)\s*\(", # 方法名，后面跟着一个左括号
        text
    )

    # 把结果整理成字典
    result = {
        "file": str(path),
        "imports": imports,
        "classes": classes,
        "methods": methods
    }

    return result


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="Extract basic information from Java files."
    )

    # 让用户通过 --project 指定 Java 项目路径
    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="Path to the Java project directory."
    )

    # 解析命令行参数
    args = parser.parse_args()

    try:
        # 先扫描项目中的所有 .java 文件
        java_files = scan_java_files(args.project)

        # 保存每个 Java 文件的提取结果
        all_results = []

        # 逐个解析 Java 文件
        for java_file in java_files:
            info = parse_java_file(java_file)
            all_results.append(info)

        # 以 JSON 格式打印结果
        # ensure_ascii=False 可以让中文正常显示
        # indent=2 可以让输出更好看
        print(json.dumps(all_results, ensure_ascii=False, indent=2))

    except FileNotFoundError as e:
        print(f"[Error] {e}")

    except NotADirectoryError as e:
        print(f"[Error] {e}")

    except Exception as e:
        print(f"[Unexpected Error] {e}")


if __name__ == "__main__":
    main()