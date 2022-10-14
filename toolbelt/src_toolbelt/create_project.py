import logging
import os
import shutil


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def edit_metadata(file_name, translate_dict):
    try:
        if not file_name.startswith('.'):
            with open(file_name, "r") as f:
                content = f.read()
            for key, value in translate_dict.items():
                content = content.replace(key, value)

            with open(file_name, "w") as f:
                f.write(content)
    except:
        logging.warning(f"Could not edit {file_name}")


def default_input(prompt, default):
    res = input(prompt)
    if res == "":
        return default
    return res


def non_empty_check(text):
    if text == "":
        raise ValueError("This value cannot be empty")
    return text


def init_project():
    destination = os.getcwd()  # exec place
    data_path = os.path.join(os.path.dirname(__file__), "template")

    name = non_empty_check(input("Project name:"))
    description = input("Project decription:")
    version = default_input("Version [default = 0.0.1]:", "0.0.1")
    author = non_empty_check(input("Author:"))
    email = input("Email:")
    destination = destination + "/" + name
    os.makedirs(destination)
    copytree(data_path, destination)

    translate_dict = {
        "$PROJECT_NAME$": name,
        "$PROJECT_VERSION$": version,
        "$PROJECT_AUTHOR$": author,
        "$PROJECT_EMAIL$": email,
        "$PROJECT_DESCRIPTION$": description,
    }
    os.rename(f"{destination}/src/src_folder", f"{destination}/src/{name}")
    for root, _, files in os.walk(destination):
        for file in files:
            edit_metadata(os.path.join(root, file), translate_dict)

    print("Project installed ✅")
    print("To start making science:")
    print(f"    cd {name}")
    print(f"    pip3 install -e .")
    print("Fill the README.md to make everyone happy, good coding!")
