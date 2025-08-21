"""Read in complex json schema for a survey and return a much simpler one.

The intended use is to read in the json file representing a survey in the ONS
'electronic questionaire' (eQ) system, and return a schema containing meta data
useful for processing the responses.
"""
import json
import csv

def load_json(filepath: str) -> dict:
    """Function to load JSON data from a file on a local network drive
    Args:
        filepath (string): The filepath

    Returns:
    -------
        dict: JSON data
    """
    # Open the file in read mode
    with open(filepath, "r") as file:
        # Load JSON data from the file
        data = json.load(file)

    return data


def flatten_nested(obj: dict | list, rows: list, prefix=""):
    """Recursively print nested JSON objects so each appears on a single line.

    The function handles both dictionaries and lists, printing each key-value pair
    or list item on a new line. The `prefix` variable is recursively updated to
    reflect the current nesting level.

    Args:
        obj (dict or list): The JSON object to print.
        prefix (str): The prefix to use for nested keys.

    Returns:
    --------
    list: A list of flattened key-value pairs.
    """

    if isinstance(obj, dict):
        for k, v in obj.items():
            # check whether the value is still a dictionary or list
            if isinstance(v, (dict, list)):
                # if so, call the recurseive function again
                flatten_nested(v, rows, prefix=f"{prefix}{k}.")
            else:
                # if not, we can add the value to a new row
                # with all higher level items held in the prefix and current `k`
                rows.append({"key": f"{prefix}{k}", "value": v})
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            # each item in a list needs to go through the recursion function again
            flatten_nested(item, rows, prefix=f"{prefix}[{idx}].")
    return rows


def get_nested_rows(json_data: dict) -> list:
    """
    Get a list of flattened rows from nested JSON data.
    """
    rows = []
    return flatten_nested(json_data, rows)


def write_nested_rows_to_csv(rows: list, csv_filepath: str):
    """
    Write list of flattened JSON objects to a CSV file, each item in a new line.

    Args:
        rows (list): The list of flattened JSON objects.
        csv_filepath (str): Path to the output CSV file.
    """
    with open(csv_filepath, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["key", "value"])
        writer.writeheader()
        for row in rows:
            print(row)
            writer.writerow(row)


def get_wanted_sections(json_data: dict):
    """Get the wanted sections from the JSON data."""
    section_dict_list = json_data["sections"]
    wanted_sections = [
        d for d in section_dict_list if d["title"] not in ["Introduction", "Comments"]
    ]
    for d in wanted_sections:
        print(f"TITLE: {d['title']}")
        for dgroup in d["groups"]:
            for block in dgroup["blocks"]:
                print(f"id: {block['id']}")
                print(f"  Type: {block['type']}")
                if "page_title" in block:
                    print(f"  Page Title: {block['page_title']}")
                if "question" in block:
                    if "text" in block['question']['title']:
                        print(f"  Question: {block['question']['title']['text']}")
                    else:
                        print(f"  Question: `{block['question']['title']}`")
                    if "answers" in block['question']:
                        for answer in block['question']['answers']:
                            print(f"Q code: {answer.get('q_code', '')}")
                            print(f"label: {answer.get('label', '')}")
                            print(f"mandatory: {answer.get('mandatory', False)}")
                            print(f"type: {answer.get('type', '')}")
                            print(f"decimal places: {answer.get('decimal_places', '')}")
                            if "type" in answer and answer["type"] == "Radio":
                                if "options" in answer:
                                    for option in answer["options"]:
                                        print(f"    Value: {option.get('value', '')}")
                            # elif "type" in answer and answer["type"]  in ["Date", "DateRange"]:
                            #     for placeholder in block['question']['title']["placeholders"]:
                            #         if "transforms" in placeholder:
                            #             for t in placeholder["transforms"]:
                            #                 print(f"date_format: {t['arguments'].get('date_format', '')}")


def write_wanted_sections(json_data: dict, csv_filepath: str):
    """Repeat the code in get_wanted_sections but instead of printing to screen write to csv
    """


    section_dict_list = json_data["sections"]
    wanted_sections = [
        d for d in section_dict_list if d["title"] not in ["Introduction", "Comments"]
    ]

    with open(csv_filepath, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["TITLE", "ID", "TYPE", "PAGE TITLE", "QUESTION", "Q CODE", "LABEL", "MANDATORY", "TYPE", "DECIMAL PLACES", "OPTIONS"])
        for d in wanted_sections:
            for dgroup in d["groups"]:
                for block in dgroup["blocks"]:
                    row = [
                        d['title'],
                        block['id'],
                        block['type'],
                        block.get('page_title', ''),
                    ]
                    if 'question' in block:
                        if 'title' in block['question']:
                            if 'text' in block['question']['title']:
                                row.append(block['question']['title']['text'])
                            else:
                                row.append(
                                    block['question'].get('title', '')
                                )

                        if "answers" in block['question']:
                            for answer in block['question']['answers']:
                                row.extend([
                                    answer.get('q_code', ''),
                                    answer.get('label', ''),
                                    answer.get('mandatory', False),
                                    answer.get('type', ''),
                                    answer.get('decimal_places', ''),
                                ])
                                if "type" in answer and answer["type"] == "Radio":
                                    if "options" in answer:
                                        for option in answer["options"]:
                                            row.append(option.get('value', ''))
                    writer.writerow(row)


if __name__ == "__main__":
    # Example usage
    github_ref = "https://github.com/ONSdigital/eq-questionnaire-schemas/blob/main/schemas/business/en/berd_0001.json"
    filepath = "config/json_schemas/berd_0001.json"
    json_data = load_json(filepath)

    # csv_filepath = "longform_json_schema.csv"
    csv_filepath = "longform_reduced_schema2.csv"
    flattened_rows = get_nested_rows(json_data)
    write_nested_rows_to_csv(flattened_rows, csv_filepath)
    # write_wanted_sections(json_data, csv_filepath)
    # print_nested(json_data)
    # get_wanted_sections(json_data)
