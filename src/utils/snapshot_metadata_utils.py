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
    # include default values to check against
    spp_filename: str = ""
    spp_created_date: str = ""
    version: int = 1
    description: str = "SPP BERD snapshot files"
    iterationL1: str = "spp_snapshots"


@dataclass
class SnapshotCandidateFileInfo:
    mani_filename: str
    mani_last_modified_date: datetime
    spp_filename: str
    spp_created_date: str
    version: int


def filter_manifest_files(
    files_dict: dict[str, datetime], target_date: str = "", wanted_str: str = ""
) -> list[ManifestFileInfo]:
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
    manifest_list = [
        ManifestFileInfo(mani_filename=fn, mani_last_modified_date=lm)
        for fn, lm in filtered_files.items()
    ]
    return manifest_list


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
    """Check the created date in metadata matches the target date and other validation.

    As well as checking for the created date, also checks description and iterationL1
    fields to ensure data is as expected.

    Args:
        metadata (SPPMetadata): The SPPMetadata object to check.
        target_date (str): The target date in 'YYYY-MM-DD' format.

    Returns:
        dict: Dict of mismatched metadata entries, empty if all match.
    """
    # create a SPPMetadata object with expected entries. The entries not specified will
    # be checked against defaults set.
    if target_date == "":
        target_date = metadata.spp_created_date  # no check needed

    expected_metadata = SPPMetadata(
        spp_filename=metadata.spp_filename,  # no check needed
        spp_created_date=target_date,  # check created matches target date
        version=metadata.version,  # no check needed
    )

    error_dict = {
        k: v
        for k, v in expected_metadata.__dict__.items()
        if getattr(metadata, k, None) != v
    }
    if error_dict:
        msg = (
            f"Metadata check failed for date {target_date}. "
            f"Mismatched entries: {error_dict}"
        )
        MetadataLogger.error(msg)
        return error_dict
    return {}


def check_files(
    mani_files_list: list[ManifestFileInfo], target_date: str = ""
) -> list[SnapshotCandidateFileInfo]:
    """Test filtered files for metadata matching the target date and metadata validity.
    Args:
        files_dict (dict): {filename: last_modified_date}
        target_date (str): Target date in 'YYYY-MM-DD' format. If empty, no date check.

    Returns:
        dict: Dict with candidate file information if metadata matches target date.
    """
    candidate_file_list = []
    for mani_file_info in mani_files_list:
        spp_metadata = get_spp_file_info_from_manifest(mani_file_info.mani_filename)
        error_dict = check_metadata(spp_metadata, target_date)
        if not error_dict:
            # create a CandidateFileInfo object and add to dict
            new_candidate = SnapshotCandidateFileInfo(
                mani_filename=mani_file_info.mani_filename,
                mani_last_modified_date=mani_file_info.mani_last_modified_date,
                spp_filename=spp_metadata.spp_filename,
                spp_created_date=spp_metadata.spp_created_date,
                version=spp_metadata.version,
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
) -> tuple[str, int, str]:
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
        corresponding_created_date = sorted_files[0].spp_created_date
    else:
        highest_version_file = file_list[0].spp_filename
        corresponding_version = file_list[0].version
        corresponding_created_date = file_list[0].spp_created_date
    return highest_version_file, corresponding_version, corresponding_created_date


def get_snapshot_name_from_date(
    prefix: str, survey_year: str, spp_date: str
) -> tuple[str, int, str]:
    """Return the name of an spp snapshot delivered on the given date.

    Args:
        survey_year (str): The survey year the snapshot belongs to.
        spp_date (str): The date the snapshot was last modified (YYYY-MM-DD).

    Returns:
        tuple: The name of the spp snapshot, its version, and created date.
    """
    # get a dictionary of all manifest files with the given prefix
    files_dict = rd_list_manifest_files(prefix)
    # filter the manifest files for the given date and wanted string
    wanted_str = f"snapshot-{survey_year}12-002-"
    filtered_mani_file_list = filter_manifest_files(files_dict, spp_date, wanted_str)
    # check filtered files for metadata matching the target date and metadata validity
    candidate_file_list = check_files(filtered_mani_file_list, spp_date)
    # if no candidate files are found checking the last modified date, search all files
    if not candidate_file_list:
        files_dict = filter_manifest_files(files_dict, wanted_str=wanted_str)
        candidate_file_list = check_files(filtered_mani_file_list, spp_date)
        if not candidate_file_list:
            MetadataLogger.error(f"No valid SPP snapshot found for date {spp_date}")
            raise ValueError(f"No valid SPP snapshot found for date {spp_date}")
    # find the most recent file if multiple candidates are found
    snapshot_name = get_most_recent_file(candidate_file_list)
    # check whether snapshot filename is unique, if not get the highest version
    duplicate_files = [
        file for file in candidate_file_list if file.spp_filename == snapshot_name
    ]
    snapshot_name, version, created_date = get_lastest_version_file(duplicate_files)
    return snapshot_name, version, created_date


def get_latest_snapshot_name(prefix: str, survey_year: str) -> tuple[str, int, str]:
    """Return the name of the latest spp snapshot for a given survey year.

    Args:
        survey_year (str): The survey year the snapshot belongs to.

    Returns:
        tuple: The name of the latest spp snapshot, its version, and created date.
    """
    # get a dictionary of all manifest files with the given prefix
    files_dict = rd_list_manifest_files(prefix)
    # filter the manifest files for the wanted string
    wanted_str = f"snapshot-{survey_year}12-002-"
    filtered_mani_file_list = filter_manifest_files(files_dict, wanted_str=wanted_str)
    candidate_file_list = check_files(filtered_mani_file_list, target_date="")
    # check filtered files for metadata validity
    snapshot_name = get_most_recent_file(candidate_file_list)
    # check whether snapshot filename is unique, if not get the highest version
    duplicate_files = [
        file for file in candidate_file_list if file.spp_filename == snapshot_name
    ]
    snapshot_name, version, created_date = get_lastest_version_file(duplicate_files)
    return snapshot_name, version, created_date
