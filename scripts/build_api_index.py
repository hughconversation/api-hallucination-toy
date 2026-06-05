from pathlib import Path
import argparse
import json
import re


def scan_java_files(project_path: str) -> list[Path]:
    """
    扫描 Java 项目文件夹，找到所有 .java 文件。
    """

    root = Path(project_path)

    if not root.exists():
        raise FileNotFoundError(f"Project path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {root}")

    return list(root.rglob("*.java"))


def parse_java_file(path: Path) -> dict:
    """
    从一个 Java 文件中粗略提取 class 和 method。

    注意：
    这里仍然是正则粗提取，不追求完美。
    Day05 的重点是把提取结果整理成 API 索引。
    """

    text = path.read_text(encoding="utf-8", errors="ignore")

    # 提取 class 名字，例如 public class UserService
    classes = re.findall(r"\bclass\s+(\w+)", text)

    # 粗略提取 method 名字
    # 这个正则可能会误提取 constructor，所以后面会再过滤一次
    methods = re.findall(
        r"(?:public|private|protected)?\s*"
        r"(?:static\s+)?"
        r"[\w\<\>\[\]]+\s+"
        r"(\w+)\s*\(",
        text
    )

    return {
        "file": str(path),
        "classes": classes,
        "methods": methods
    }


def build_api_index(project_path: str) -> dict:
    """
    构建 API 索引。

    API 索引的形式是：
    {
      "类名": ["方法1", "方法2", "方法3"]
    }
    """

    java_files = scan_java_files(project_path)

    # api_index 是最终要保存的字典
    api_index = {}

    for java_file in java_files:
        info = parse_java_file(java_file)

        classes = info["classes"]
        methods = info["methods"]

        # 一个简单 Java 文件通常只有一个 class。
        # 这里为了简单处理，把这个文件里提取到的方法都挂到每个 class 下面。
        for class_name in classes:
            # 如果这个 class 还没有出现在索引里，就先创建一个空列表
            if class_name not in api_index:
                api_index[class_name] = []

            for method in methods:
                # 过滤 constructor
                # 因为 constructor 的名字通常和 class 名字一样
                if method == class_name:
                    continue

                # 避免重复加入同一个方法名
                if method not in api_index[class_name]:
                    api_index[class_name].append(method)

    return api_index


def save_api_index(api_index: dict, output_path: str):
    """
    把 API 索引保存成 JSON 文件。
    """

    output_file = Path(output_path)

    # 如果 data/ 目录不存在，就自动创建
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_file.write_text(
        json.dumps(api_index, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Build a simple class-method API index from a Java project."
    )

    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="Path to the Java project directory."
    )

    parser.add_argument(
        "--output",
        type=str,
        default="data/api_index.json",
        help="Path to save the API index JSON file."
    )

    args = parser.parse_args()

    try:
        api_index = build_api_index(args.project)
        save_api_index(api_index, args.output)

        print(f"API index saved to: {args.output}")
        print(json.dumps(api_index, ensure_ascii=False, indent=2))

    except FileNotFoundError as e:
        print(f"[Error] {e}")

    except NotADirectoryError as e:
        print(f"[Error] {e}")

    except Exception as e:
        print(f"[Unexpected Error] {e}")


if __name__ == "__main__":
    main()