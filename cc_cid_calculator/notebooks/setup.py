"""
Script to setup notebook coding enviroment local or Sagemaker.
"""

import os
import sys


def main(env, project):
    """
    Main entry point for the script.
    """
    assert env in ['sagemaker',
                   'vscode'], "Enviroment must be Sagemaker or VSCode"
    if env == 'sagemaker':
        os.chdir("/root/machine_learning/users/luiz_superti/" + project)

    if env == 'vscode':
        os.chdir(
            "/users/luiz.superti/documents/github/alice-coding/"
            + project)

    print("Project directory: {}".format(os.getcwd()))


if __name__ == '__main__':
    sys.exit(main())