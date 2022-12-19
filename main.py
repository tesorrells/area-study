import argparse
import configparser
import os
import typing


def run(
    classification: str,
    data_directory: typing.Optional[str],
    save_directory: str,
    config_file: typing.Optional[str] = None,
    emergency_services: typing.Optional[bool] = None,
    law_enforcement: typing.Optional[bool] = None,
    military: typing.Optional[bool] = None,
    water: typing.Optional[bool] = None,
    power: typing.Optional[bool] = None,
    food: typing.Optional[bool] = None,
) -> None:
    x = 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--classification",
        default="UNCLASSIFIED",
        help="Classification level of output",
    )
    parser.add_argument(
        "--data-directory",
        required=False,
        type=str,
        help="directory of assets to detect on",
    )
    parser.add_argument(
        "--save-directory",
        default="save",
        help="directory to save results",
    )
    parser.add_argument(
        "--config-file",
        required=False,
        type=str,
        default=None,
        help="config for CLI arguments",
    )
    parser.add_argument(
        "--emergency-services",
        type=bool,
        default=True,
        help="Label emergency services",
    )
    parser.add_argument(
        "--law-enforcement",
        type=bool,
        default=True,
        help="Label law enforcement",
    )
    parser.add_argument(
        "--military",
        type=bool,
        default=True,
        help="Label military infrastructure",
    )
    parser.add_argument(
        "--water",
        type=bool,
        default=True,
        help="Label water infrastructure",
    )
    parser.add_argument(
        "--power",
        type=bool,
        default=True,
        help="Label power infrastructure",
    )
    parser.add_argument(
        "--food",
        type=bool,
        default=True,
        help="Label food locations",
    )

    opt = parser.parse_args()
    if opt.config_file:
        if os.path.isfile(opt.config_file):
            config = configparser.ConfigParser()
            config.read(opt.config_file)
            opt.classification = config["cutlass"].get("CLASSIFICATION")
            opt.dataset_directory = config["cutlass"].get("DATASET_DIRECTORY")
            opt.save_directory = config["cutlass"].get("SAVE_DIRECTORY")
        else:
            print("Config not found! Defaulting to cli arguments.")

    run(**vars(opt))


if __name__ == "__main__":
    main()
