"""Published API contracts; source revisions are recorded in tests/parity-audit.json."""

TASK_PATH = "/seedance/tasks"

ENDPOINTS = {
    "seedance_generate_video": {
        "method": "POST",
        "path": "/seedance/videos",
        "operation": "generate",
        "schema": {
            "type": "object",
            "required": ["model", "content"],
            "properties": {
                "model": {
                    "type": "string",
                    "enum": [
                        "doubao-seedance-1-0-pro-250528",
                        "doubao-seedance-1-0-pro-fast-251015",
                        "doubao-seedance-1-5-pro-251215",
                        "doubao-seedance-1-0-lite-t2v-250428",
                        "doubao-seedance-1-0-lite-i2v-250428",
                        "doubao-seedance-2-0-260128",
                        "doubao-seedance-2-0-fast-260128",
                        "doubao-seedance-2-0-mini-260615",
                        "doubao-seedance-2-5-260628",
                    ],
                },
                "content": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {
                                "type": "object",
                                "required": ["type", "text"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["text"]},
                                    "text": {"type": "string", "maxLength": 1000},
                                },
                                "additionalProperties": False,
                            },
                            {
                                "type": "object",
                                "required": ["type", "image_url"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["image_url"]},
                                    "image_url": {
                                        "type": "object",
                                        "required": ["url"],
                                        "properties": {"url": {"type": "string"}},
                                        "additionalProperties": False,
                                    },
                                    "role": {
                                        "type": "string",
                                        "enum": ["first_frame", "last_frame", "reference_image"],
                                    },
                                },
                                "additionalProperties": False,
                            },
                            {
                                "type": "object",
                                "required": ["type", "audio_url", "role"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["audio_url"]},
                                    "audio_url": {
                                        "type": "object",
                                        "required": ["url"],
                                        "properties": {"url": {"type": "string"}},
                                        "additionalProperties": False,
                                    },
                                    "role": {"type": "string", "enum": ["reference_audio"]},
                                },
                                "additionalProperties": False,
                            },
                            {
                                "type": "object",
                                "required": ["type", "video_url", "role"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["video_url"]},
                                    "video_url": {
                                        "type": "object",
                                        "required": ["url"],
                                        "properties": {"url": {"type": "string"}},
                                        "additionalProperties": False,
                                    },
                                    "role": {"type": "string", "enum": ["reference_video"]},
                                },
                                "additionalProperties": False,
                            },
                        ],
                        "discriminator": {"propertyName": "type"},
                    },
                },
                "resolution": {"type": "string", "enum": ["480p", "720p", "1080p", "4k"]},
                "ratio": {
                    "type": "string",
                    "enum": ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"],
                },
                "duration": {"type": "integer", "minimum": -1, "maximum": 30},
                "frames": {"type": "integer", "minimum": 29, "maximum": 289},
                "seed": {"type": "integer", "minimum": -1, "maximum": 4294967295},
                "camerafixed": {"type": "boolean"},
                "watermark": {"type": "boolean"},
                "generate_audio": {"type": "boolean"},
                "callback_url": {"type": "string", "format": "uri"},
                "async": {"type": "boolean"},
                "return_last_frame": {"type": "boolean"},
                "execution_expires_after": {"type": "integer", "minimum": 3600, "maximum": 259200},
                "omni_reference_task_type": {
                    "type": "string",
                    "enum": ["auto", "reference", "edit", "extend"],
                },
                "output_format": {"type": "string", "enum": ["mp4", "mov"]},
                "tools": {
                    "type": "array",
                    "maxItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["type"],
                        "additionalProperties": False,
                        "properties": {
                            "type": {"type": "string", "enum": ["web_search"]},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                            "max_keyword": {"type": "integer", "minimum": 1, "maximum": 50},
                            "sources": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["toutiao", "douyin", "moji", "search_engine"],
                                },
                            },
                        },
                    },
                },
                "priority": {"type": "integer", "minimum": 0, "maximum": 9},
                "safety_identifier": {"type": "string", "maxLength": 64},
            },
        },
        "properties": {
            "model": {
                "type": "string",
                "enum": [
                    "doubao-seedance-1-0-pro-250528",
                    "doubao-seedance-1-0-pro-fast-251015",
                    "doubao-seedance-1-5-pro-251215",
                    "doubao-seedance-1-0-lite-t2v-250428",
                    "doubao-seedance-1-0-lite-i2v-250428",
                    "doubao-seedance-2-0-260128",
                    "doubao-seedance-2-0-fast-260128",
                    "doubao-seedance-2-0-mini-260615",
                    "doubao-seedance-2-5-260628",
                ],
            },
            "content": {
                "type": "array",
                "items": {
                    "oneOf": [
                        {
                            "type": "object",
                            "required": ["type", "text"],
                            "properties": {
                                "type": {"type": "string", "enum": ["text"]},
                                "text": {"type": "string", "maxLength": 1000},
                            },
                            "additionalProperties": False,
                        },
                        {
                            "type": "object",
                            "required": ["type", "image_url"],
                            "properties": {
                                "type": {"type": "string", "enum": ["image_url"]},
                                "image_url": {
                                    "type": "object",
                                    "required": ["url"],
                                    "properties": {"url": {"type": "string"}},
                                    "additionalProperties": False,
                                },
                                "role": {
                                    "type": "string",
                                    "enum": ["first_frame", "last_frame", "reference_image"],
                                },
                            },
                            "additionalProperties": False,
                        },
                        {
                            "type": "object",
                            "required": ["type", "audio_url", "role"],
                            "properties": {
                                "type": {"type": "string", "enum": ["audio_url"]},
                                "audio_url": {
                                    "type": "object",
                                    "required": ["url"],
                                    "properties": {"url": {"type": "string"}},
                                    "additionalProperties": False,
                                },
                                "role": {"type": "string", "enum": ["reference_audio"]},
                            },
                            "additionalProperties": False,
                        },
                        {
                            "type": "object",
                            "required": ["type", "video_url", "role"],
                            "properties": {
                                "type": {"type": "string", "enum": ["video_url"]},
                                "video_url": {
                                    "type": "object",
                                    "required": ["url"],
                                    "properties": {"url": {"type": "string"}},
                                    "additionalProperties": False,
                                },
                                "role": {"type": "string", "enum": ["reference_video"]},
                            },
                            "additionalProperties": False,
                        },
                    ],
                    "discriminator": {"propertyName": "type"},
                },
            },
            "resolution": {"type": "string", "enum": ["480p", "720p", "1080p", "4k"]},
            "ratio": {
                "type": "string",
                "enum": ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"],
            },
            "duration": {"type": "integer", "minimum": -1, "maximum": 30},
            "frames": {"type": "integer", "minimum": 29, "maximum": 289},
            "seed": {"type": "integer", "minimum": -1, "maximum": 4294967295},
            "camerafixed": {"type": "boolean"},
            "watermark": {"type": "boolean"},
            "generate_audio": {"type": "boolean"},
            "callback_url": {"type": "string", "format": "uri"},
            "async": {"type": "boolean"},
            "return_last_frame": {"type": "boolean"},
            "execution_expires_after": {"type": "integer", "minimum": 3600, "maximum": 259200},
            "omni_reference_task_type": {
                "type": "string",
                "enum": ["auto", "reference", "edit", "extend"],
            },
            "output_format": {"type": "string", "enum": ["mp4", "mov"]},
            "tools": {
                "type": "array",
                "maxItems": 1,
                "items": {
                    "type": "object",
                    "required": ["type"],
                    "additionalProperties": False,
                    "properties": {
                        "type": {"type": "string", "enum": ["web_search"]},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                        "max_keyword": {"type": "integer", "minimum": 1, "maximum": 50},
                        "sources": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["toutiao", "douyin", "moji", "search_engine"],
                            },
                        },
                    },
                },
            },
            "priority": {"type": "integer", "minimum": 0, "maximum": 9},
            "safety_identifier": {"type": "string", "maxLength": 64},
        },
        "parameters": [],
        "defaults": {
            "model": "doubao-seedance-2-0-mini-260615",
            "resolution": "480p",
            "ratio": "16:9",
            "generate_audio": False,
        },
        "fixed": {},
        "allow_empty": [],
        "query_actions": [],
        "media_response": False,
    },
    "seedance_task_retrieve": {
        "method": "POST",
        "path": "/seedance/tasks",
        "operation": "task",
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "ids": {"type": "array", "items": {"type": "string"}},
                "action": {"enum": ["retrieve", "retrieve_batch"], "type": "string"},
            },
        },
        "properties": {
            "id": {"type": "string"},
            "ids": {"type": "array", "items": {"type": "string"}},
            "action": {"enum": ["retrieve", "retrieve_batch"], "type": "string"},
        },
        "parameters": [],
        "defaults": {"wait_seconds": 0},
        "fixed": {},
        "allow_empty": [],
        "query_actions": ["retrieve", "retrieve_batch", "list", "presets"],
        "media_response": False,
    },
    "seedance_tasks_retrieve_batch": {
        "method": "POST",
        "path": "/seedance/tasks",
        "operation": "batch",
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "action": {"enum": ["retrieve", "retrieve_batch"], "type": "string"},
            },
            "required": ["action", "ids"],
        },
        "properties": {
            "id": {"type": "string"},
            "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "action": {"enum": ["retrieve", "retrieve_batch"], "type": "string"},
        },
        "parameters": [],
        "defaults": {},
        "fixed": {"action": "retrieve_batch"},
        "allow_empty": [],
        "query_actions": ["retrieve", "retrieve_batch", "list", "presets"],
        "media_response": False,
    },
}
