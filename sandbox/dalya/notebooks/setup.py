"""
Script to setup notebook coding enviroment local or Sagemaker.
"""
import os
import sys
from tokenize import Ignore


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
            "/Users/luiz.superti/Documents/GitHub/alice-coding/ML-models/"
            + project)

    print("Project directory: {}".format(os.getcwd()))


if __name__ == '__main__':
    sys.exit()