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


def extract_method_calls_from_file(path: Path) -> list[dict]:
    """
    从一个 Java 文件中提取简单的方法调用。

    目前只处理最简单的形式：

    变量名.方法名(

    例如：
    userService.save(user);
    user.getName();
    System.out.println("hello");

    暂时不处理复杂情况，比如：
    getUser().getName();
    users.get(0).getName();
    new UserService().save(user);
    """

    text = path.read_text(encoding="utf-8", errors="ignore")

    results = []

    # 正则含义：
    # (\w+)     提取点号前面的名字，例如 userService、user、System、out
    # \.        匹配中间的点号 .
    # (\w+)     提取点号后面的方法名，例如 save、getName、println
    # \s*       方法名和左括号之间可以有空格
    # \(        匹配左括号 (
    pattern = r"(\w+)\.(\w+)\s*\("

    # 按行处理，方便记录原始代码行
    for line_number, line in enumerate(text.splitlines(), start=1):
        matches = re.findall(pattern, line)

        for receiver, method in matches:
            results.append({
                "file": str(path),
                "line_number": line_number,
                "receiver": receiver,
                "method": method,
                "line": line.strip()
            })

    return results


def extract_method_calls(project_path: str) -> list[dict]:
    """
    扫描整个 Java 项目，并提取所有简单 method call。
    """

    java_files = scan_java_files(project_path)

    all_calls = []

    for java_file in java_files:
        calls = extract_method_calls_from_file(java_file)
        all_calls.extend(calls)

    return all_calls


def save_method_calls(method_calls: list[dict], output_path: str):
    """
    把提取出的 method call 保存成 JSON 文件。
    """

    output_file = Path(output_path)

    # 如果输出文件所在的文件夹不存在，就自动创建
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_file.write_text(
        json.dumps(method_calls, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Extract simple method calls from Java files."
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
        default="data/method_calls.json",
        help="Path to save extracted method calls."
    )

    args = parser.parse_args()

    try:
        method_calls = extract_method_calls(args.project)
        save_method_calls(method_calls, args.output)

        print(f"Method calls saved to: {args.output}")
        print(f"Method calls: {len(method_calls)}")
        print(json.dumps(method_calls[:10], ensure_ascii=False, indent=2))

        if len(method_calls) > 10:
            print(f"... and {len(method_calls) - 10} more method calls.")

    except FileNotFoundError as e:
        print(f"[Error] {e}")

    except NotADirectoryError as e:
        print(f"[Error] {e}")

    except Exception as e:
        print(f"[Unexpected Error] {e}")


if __name__ == "__main__":
    main()