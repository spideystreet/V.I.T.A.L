"""Generate the VITAL Sync Apple Shortcut programmatically.

Creates a .shortcut file with all health metrics, ready to sign and import.
Usage: uv run python scripts/generate_shortcut.py [--ip 192.168.1.24]
"""

import argparse
import plistlib
import uuid


def _uuid() -> str:
    return str(uuid.uuid4()).upper()


def _text_action(text: str) -> tuple[str, dict]:
    """Create a plain text action. Returns (uuid, action_dict)."""
    uid = _uuid()
    return uid, {
        "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
        "WFWorkflowActionParameters": {
            "UUID": uid,
            "WFTextActionText": text,
        },
    }


def _set_variable(name: str, output_name: str, output_uuid: str) -> dict:
    """Create a Set Variable action referencing a previous action's output."""
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
        "WFWorkflowActionParameters": {
            "WFInput": {
                "Value": {
                    "OutputName": output_name,
                    "OutputUUID": output_uuid,
                    "Type": "ActionOutput",
                },
                "WFSerializationType": "WFTextTokenAttachment",
            },
            "WFVariableName": name,
        },
    }


def _find_health_samples(
    health_type: str,
    time_unit: int = 16,  # 16 = hours for "is in the last"
    time_value: str = "1",
    operator: int = 1001,  # 1001 = "is in the last", 1002 = "is today"
    group_by: str | None = None,
    sort_property: str = "Start Date",
    sort_order: str = "Latest First",
) -> tuple[str, dict]:
    """Create a Find Health Samples action. Returns (uuid, action_dict)."""
    uid = _uuid()

    filters = [
        {
            "Bounded": True,
            "Operator": 4,
            "Property": "Type",
            "Removable": False,
            "Values": {
                "Enumeration": {
                    "Value": health_type,
                    "WFSerializationType": "WFStringSubstitutableState",
                },
            },
        },
        {
            "Bounded": True,
            "Operator": operator,
            "Property": "Start Date",
            "Removable": False,
            "Values": {
                "Number": time_value,
                "Unit": time_unit,
            },
        },
    ]

    params = {
        "UUID": uid,
        "WFContentItemFilter": {
            "Value": {
                "WFActionParameterFilterPrefix": 1,
                "WFActionParameterFilterTemplates": filters,
                "WFContentPredicateBoundedDate": False,
            },
            "WFSerializationType": "WFContentPredicateTableTemplate",
        },
        "WFContentItemLimitEnabled": True,
        "WFContentItemLimitNumber": 1.0,
    }

    if group_by:
        params["WFHKSampleFilteringGroupBy"] = group_by
    else:
        params["WFContentItemSortOrder"] = sort_order
        params["WFContentItemSortProperty"] = sort_property

    return uid, {
        "WFWorkflowActionIdentifier": "is.workflow.actions.filter.health.quantity",
        "WFWorkflowActionParameters": params,
    }


def _variable_attachment(var_name: str) -> dict:
    """Create a variable reference attachment."""
    return {
        "Type": "Variable",
        "VariableName": var_name,
    }


def _current_date_attachment() -> dict:
    """Create a Current Date attachment with ISO 8601 format (with time)."""
    return {
        "Aggrandizements": [
            {
                "Type": "WFDateFormatVariableAggrandizement",
                "WFDateFormatStyle": "ISO 8601",
                "WFISO8601IncludeTime": True,
            },
        ],
        "Type": "CurrentDate",
    }


def _text_token_string(template: str, attachments: dict) -> dict:
    """Create a WFTextTokenString with variable attachments."""
    return {
        "Value": {
            "attachmentsByRange": attachments,
            "string": template,
        },
        "WFSerializationType": "WFTextTokenString",
    }


def _dict_field(key: str, value, item_type: int = 0) -> dict:
    """Create a dictionary field. item_type: 0=text, 3=number."""
    field = {
        "WFItemType": item_type,
        "WFKey": {
            "Value": {"string": key},
            "WFSerializationType": "WFTextTokenString",
        },
    }

    if isinstance(value, dict):
        field["WFValue"] = value
    else:
        field["WFValue"] = {
            "Value": {"string": str(value)},
            "WFSerializationType": "WFTextTokenString",
        }

    return field


def _metric_dict(metric_name: str, var_name: str, unit: str) -> dict:
    """Create a metric dictionary entry for the JSON array."""
    return {
        "WFItemType": 1,  # Dictionary type
        "WFValue": {
            "Value": {
                "Value": {
                    "WFDictionaryFieldValueItems": [
                        _dict_field("metric", metric_name),
                        _dict_field(
                            "value",
                            _text_token_string(
                                "\ufffc",
                                {"{0, 1}": _variable_attachment(var_name)},
                            ),
                            item_type=3,  # Number
                        ),
                        _dict_field("unit", unit),
                        _dict_field(
                            "recorded_at",
                            _text_token_string(
                                "\ufffc",
                                {"{0, 1}": _current_date_attachment()},
                            ),
                        ),
                    ],
                },
                "WFSerializationType": "WFDictionaryFieldValue",
            },
            "WFSerializationType": "WFDictionaryFieldValue",
        },
    }


def _post_action(server_url_uuid: str, metrics: list[dict]) -> tuple[str, dict]:
    """Create the POST URL action with JSON body."""
    uid = _uuid()

    return uid, {
        "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
        "WFWorkflowActionParameters": {
            "ShowHeaders": True,
            "UUID": uid,
            "WFHTTPBodyType": "JSON",
            "WFHTTPMethod": "POST",
            "WFJSONValues": {
                "Value": {
                    "WFDictionaryFieldValueItems": [
                        {
                            "WFItemType": 2,  # Array type
                            "WFKey": {
                                "Value": {"string": "metrics"},
                                "WFSerializationType": "WFTextTokenString",
                            },
                            "WFValue": {
                                "Value": metrics,
                                "WFSerializationType": "WFArrayParameterState",
                            },
                        },
                    ],
                },
                "WFSerializationType": "WFDictionaryFieldValue",
            },
            "WFURL": _text_token_string(
                "\ufffc",
                {"{0, 1}": _variable_attachment("server_url")},
            ),
        },
    }


def _show_result(output_uuid: str) -> dict:
    """Create a Show Result action."""
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
        "WFWorkflowActionParameters": {
            "Text": _text_token_string(
                "\ufffc",
                {
                    "{0, 1}": {
                        "OutputName": "Contents of URL",
                        "OutputUUID": output_uuid,
                        "Type": "ActionOutput",
                    },
                },
            ),
        },
    }


HEALTH_METRICS = [
    # (var_name, health_type, unit, operator, time_value, group_by)
    ("heart_rate", "Heart Rate", "bpm", 1001, "1", None),
    ("resting_hr", "Resting Heart Rate", "bpm", 1001, "1", None),
    ("spo2", "Oxygen Saturation", "%", 1001, "1", None),
    ("steps", "Steps", "count", 1001, "24", "Day"),
    ("hrv", "Heart Rate Variability", "ms", 1001, "1", None),
    ("sleep", "Sleep", "hours", 1001, "1", None),
]


def generate_shortcut(server_ip: str, port: int = 8420) -> dict:
    """Generate the full shortcut plist structure."""
    actions = []

    # Step 1: Server URL
    url = f"http://{server_ip}:{port}/health"
    url_uuid, url_action = _text_action(url)
    actions.append(url_action)
    actions.append(_set_variable("server_url", "Text", url_uuid))

    # Steps 2-7: Health metrics
    for var_name, health_type, unit, operator, time_val, group_by in HEALTH_METRICS:
        sample_uuid, sample_action = _find_health_samples(
            health_type=health_type,
            operator=operator,
            time_value=time_val,
            time_unit=16,  # hours
            group_by=group_by,
        )
        actions.append(sample_action)
        actions.append(_set_variable(var_name, "Health Samples", sample_uuid))

    # Step 8: POST with JSON body
    metric_dicts = [
        _metric_dict(name, var, unit)
        for var, _, unit, _, _, _ in HEALTH_METRICS
        for name, var_check in [(var, var)]
        if var_check == var  # just iterate
    ]
    # Simplify: build metric dicts properly
    metric_dicts = []
    for var_name, _, unit, _, _, _ in HEALTH_METRICS:
        metric_dicts.append(_metric_dict(var_name, var_name, unit))

    post_uuid, post_action = _post_action(url_uuid, metric_dicts)
    actions.append(post_action)

    # Step 9: Show result
    actions.append(_show_result(post_uuid))

    return {
        "WFWorkflowClientVersion": "2702.0.5",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowName": "VITAL Sync",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 4274264319,  # Orange
            "WFWorkflowIconGlyphNumber": 59584,  # Heart icon
        },
        "WFWorkflowInputContentItemClasses": [
            "WFAppStoreAppContentItem",
            "WFArticleContentItem",
            "WFContactContentItem",
            "WFDateContentItem",
            "WFEmailAddressContentItem",
            "WFGenericFileContentItem",
            "WFImageContentItem",
            "WFiTunesProductContentItem",
            "WFLocationContentItem",
            "WFDCMapsLinkContentItem",
            "WFAVAssetContentItem",
            "WFPDFContentItem",
            "WFPhoneNumberContentItem",
            "WFRichTextContentItem",
            "WFSafariWebPageContentItem",
            "WFStringContentItem",
            "WFURLContentItem",
        ],
        "WFWorkflowActions": actions,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate VITAL Sync shortcut")
    parser.add_argument("--ip", default="192.168.1.24", help="Mac IP address")
    parser.add_argument("--port", type=int, default=8420, help="Server port")
    parser.add_argument("--output", default="/tmp/vital_sync.shortcut", help="Output path")
    args = parser.parse_args()

    shortcut = generate_shortcut(args.ip, args.port)

    with open(args.output, "wb") as f:
        plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)

    print(f"Shortcut generated: {args.output}")
    print(f"Server URL: http://{args.ip}:{args.port}/health")
    print(f"\nTo sign: shortcuts sign --mode anyone --input {args.output} --output /tmp/vital_sync_signed.shortcut")


if __name__ == "__main__":
    main()
