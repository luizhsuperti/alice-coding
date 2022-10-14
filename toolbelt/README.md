# Toolbelt DS
Toolbelt is a project for creating data science projects in Alice's standards.

## How to install
`pip3 install -e git+ssh://git@github.com/alice-health/toolbelt-ds-cli.git#egg=toolbelt_ds`

## Commands
`init_project`: Initilizes default repo

## Structure
The created project is divided into `notebooks` and `src`, the first for designing experiments and explorations and the latter for implementing data extraction, deploy and model training.

### `src`
The source folder is divided into `interfaces`, `models` and `steps`. Interfaces are classes for interacting with data (`DataInteractor`), for creating a model (`model`), for defining a general pipeline step (`PipelineStep`) and for abstracting transformations (`transform`).
The models folder is where each of your model should go. Each model shoul inherit the abstract `model` from interfaces. Take a look at `model_example` for an example.
Finally the `steps` folder defines three steps: `extract` for extracting and preprocessing your data, `modelServe` for implementing deploy time execution of your model and `trainModel` for implementing the training step. Each of these steps inherit `pipelineStep`, so they all have a `self.di` property for interacting with data, saving and loading objects, etc.
