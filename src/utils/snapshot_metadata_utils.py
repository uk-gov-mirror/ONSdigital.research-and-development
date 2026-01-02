"""
Functions to obtain information about spp snapshots from metadata files.

These scripts are designed to run in DAP S3 environment only.
"""

import logging
from dataclasses import dataclass
from datetime import datetime

from src.utils.s3_mods import rd_load_json, rd_list_manifest_files

MetadataLogger = logging.getLogger(__name__)


# Data classes for manifest file info and SPP metadata
@dataclass
class ManifestFileInfo:
    mani_filename: str
    mani_last_modified_date: datetime


@dataclass
class SPPMetadata:
    spp_filename: str
    spp_created_date: str
    version: int
    description: str = ""
    iterationL1: str = ""


@dataclass
class SnapshotCandidateFileInfo:
    mani_filename: str
    mani_last_modified_date: datetime
    spp_filename: str
    spp_created_date: str
    version: int


def filter_manifest_files(
    files_dict: dict[str, datetime], target_date: str = "", wanted_str: str = ""
) -> dict:
    """
    Filter manifest files by target date and/ or filename substring.

    Args:
        files_dict (dict): Dictionary of {filename: last_modified_date}.
        target_date (str): The target date in 'YYYY-MM-DD' format.
        wanted_str (str): Substring that should be present in the filename.

    Returns:
        dict: Filtered dictionary with files matching the target date or substring.
    """
    if wanted_str:
        filtered_files = {
            filename: last_mod_date
            for filename, last_mod_date in files_dict.items()
            if wanted_str in filename
        }
    if target_date:
        filtered_files = {
            filename: last_mod_date
            for filename, last_mod_date in files_dict.items()
            if last_mod_date.strftime("%Y-%m-%d") == target_date
        }
    return filtered_files


def get_spp_file_info_from_manifest(filename: str) -> SPPMetadata:
    """Get SPP file information from a manifest file as SPPMetadata."""
    manif_file_dict = rd_load_json(filename)
    metadata = SPPMetadata(
        spp_filename=manif_file_dict["files"][0]["name"],
        spp_created_date=str(manif_file_dict["tdzComplete"])[:10],
        version=manif_file_dict.get("version", 1),
        description=manif_file_dict.get("description", ""),
        iterationL1=manif_file_dict.get("iterationL1", ""),
    )
    return metadata


def check_metadata(metadata: SPPMetadata, target_date: str) -> dict:
    """Check if the created date in metadata matches the target date."""
    expected_entries = {
        "created_date": target_date,
        "description": "SPP BERD snapshot files",
        "iterationL1": "spp_snapshots",
    }
    error_dict = {
        k: v for k, v in expected_entries.items() if getattr(metadata, k, None) != v
    }
    if error_dict:
        msg = (
            f"Metadata check failed for date {target_date}. "
            f"Mismatched entries: {error_dict}"
        )
        MetadataLogger.error(msg)
        return error_dict
    return {}


def check_manifest_files_for_date(
    files_dict: dict, target_date: str, wanted_str: str
) -> dict:
    """Check manifest files for a specific target date.

    Args:
        files_dict (dict): {filename: last_modified_date}
        target_date (str): The target date in 'YYYY-MM-DD' format.

    Returns:
        dict: Filtered dictionary with files matching the target date.
    """
    correct_date_files = {}
    for filename, last_mod_date in files_dict.items():
        if last_mod_date.strftime("%Y-%m-%d") == target_date:
            # get all the mainfest files with the correct substring
            new_files_dict = filter_manifest_files(files_dict, wanted_str=wanted_str)
            # read each manifest file and check the tdzComplete date
            for filename in new_files_dict.keys():
                manif_file_dict = rd_load_json(filename)
                created_date = manif_file_dict["tdzComplete"]
                if created_date.startswith(target_date):
                    correct_date_files[filename] = target_date
                    file_version = manif_file_dict.get("version", "")
                    if file_version > 1:
                        correct_date_files[filename] = f"{target_date}_v{file_version}"


def test_filtered_files(
    files_dict: dict, target_date: str
) -> list[SnapshotCandidateFileInfo]:
    """Test filtered files for metadata matching the target date and metadata validity.
    Args:
        files_dict (dict): {filename: last_modified_date}
        target_date (str): The target date in 'YYYY-MM-DD' format.

    Returns:
        dict: Dict with candidate file information if metadata matches target date.
    """
    candidate_file_list = []
    for filename, last_mod_date in files_dict.items():
        metadata_dict = get_spp_file_info_from_manifest(filename)
        error_dict = check_metadata(metadata_dict, target_date)
        if not error_dict:
            # create a CandidateFileInfo object and add to dict
            new_candidate = SnapshotCandidateFileInfo(
                mani_filename=filename,
                mani_last_modified_date=last_mod_date,
                spp_filename=metadata_dict.spp_filename,
                spp_created_date=metadata_dict.spp_created_date,
                version=metadata_dict.version,
            )
            candidate_file_list.append(new_candidate)
    return candidate_file_list


def get_most_recent_file(file_list: list[SnapshotCandidateFileInfo]) -> str:
    """Get the filename of the most recently modified file from a dictionary.

    Args:
        file_dict (dict): {filename: last_modified_date}

    Returns:
        str: The filename (key) of the most recently modified file.
    """
    if len(file_list) > 1:
        # sort the list by last modified date and get the most recent
        sorted_files = sorted(
            file_list, key=lambda x: x.mani_last_modified_date, reverse=True
        )
        most_recent_file = sorted_files[0].spp_filename
    else:
        most_recent_file = file_list[0].spp_filename
    return most_recent_file


def get_lastest_version_file(
    file_list: list[SnapshotCandidateFileInfo],
) -> tuple[str, int]:
    """Get filename of the highest version file from a list where filenames the same.

    Args:
        file_list (list): List of SnapshotCandidateFileInfo objects.

    Returns:
        tuple: The filename of the highest version file and its version number.
    """
    if len(file_list) > 1:
        # sort the list by version and get the highest version
        sorted_files = sorted(file_list, key=lambda x: x.version, reverse=True)
        highest_version_file = sorted_files[0].spp_filename
        corresponding_version = sorted_files[0].version
    else:
        highest_version_file = file_list[0].spp_filename
        corresponding_version = file_list[0].version
    return highest_version_file, corresponding_version


def get_snapshot_name_from_date(
    prefix: str, survey_year: str, spp_date: str
) -> tuple[str, int]:
    """Return the name of an spp snapshot delivered on the given date.

    Args:
        survey_year (str): The survey year the snapshot belongs to.
        spp_date (str): The date the snapshot was last modified (YYYY-MM-DD).

    Returns:
        str: The name of the required spp snapshot.
    """
    # get a dictionary of all manifest files with the given prefix
    files_dict = rd_list_manifest_files(prefix)
    # filter the manifest files for the given date and wanted string
    wanted_str = f"snapshot-{survey_year}12-002-"
    files_dict = filter_manifest_files(files_dict, spp_date, wanted_str)
    # check filtered files for metadata matching the target date and metadata validity
    candidate_file_dict = test_filtered_files(files_dict, spp_date)
    # if no candidate files are found checking the last modified date, search all files
    if not candidate_file_dict:
        files_dict = filter_manifest_files(files_dict, wanted_str=wanted_str)
        candidate_file_dict = test_filtered_files(files_dict, spp_date)
        if not candidate_file_dict:
            MetadataLogger.error(f"No valid SPP snapshot found for date {spp_date}")
            raise ValueError(f"No valid SPP snapshot found for date {spp_date}")
    # find the most recent file if multiple candidates are found
    snapshot_name = get_most_recent_file(candidate_file_dict)
    # check whether snapshot filename is unique, if not get the highest version
    duplicate_files = [
        file for file in candidate_file_dict if file.spp_filename == snapshot_name
    ]
    if len(duplicate_files) > 1:
        snapshot_name, version = get_lastest_version_file(duplicate_files)
    return snapshot_name, version
