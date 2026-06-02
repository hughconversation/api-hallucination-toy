from pathlib import Path
import argparse


def scan_java_files(project_path: str):
    root = Path(project_path)

    if not root.exists():
        raise FileNotFoundError(f"Project path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {root}")

    return list(root.rglob("*.java"))


def main():
    parser = argparse.ArgumentParser(
        description="Scan a Java project and list all .java files."
    )

    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="Path to the Java project directory."
    )

    args = parser.parse_args()

    java_files = scan_java_files(args.project)

    print(f"Java files: {len(java_files)}")

    for file in java_files[:10]:
        print(file)


if __name__ == "__main__":
    main()