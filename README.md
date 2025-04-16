# AnimationJsonConverter Usage Guide

## Introduction

AnimationJsonConverter is a powerful tool designed to convert old-format animation JSON files for Palworld into the new SCake 0.6+ format. The converter automatically handles the transformation of animations, events, compatibility settings, and can intelligently infer missing information like tags and act types.

## Features

- Convert old animation JSONs to SCake 0.6+ format
- Enhance already converted JSONs with automatically inferred tags
- Support for both command line and interactive menu operation
- Detailed logging of conversion issues
- Customizable mapping system for tags, equipment, and act types

## Installation

1. Download the `AnimationJsonConverter.py` script
2. Place it in a directory of your choice
3. Ensure you have Python 3.6+ installed
4. Run the script using Python: `python AnimationJsonConverter.py`

No additional packages are required!

## Directory Structure

The converter uses the following directory structure:

- `anims/` - Place your old-format JSON files here for conversion
- `output/` - Converted files will be stored here
- `enhance/` - Place already-converted files here for tag enhancement
- `enhanced/` - Enhanced files with added tags will be stored here

These directories will be automatically created if they don't exist.

## Basic Usage

### Method 1: Interactive Menu

1. Run the script: `python AnimationJsonConverter.py`
2. Choose an option from the menu:
   - `1` - Convert old JSONs to new format
   - `2` - Enhance tags in already converted files
   - `3` - Exit

### Method 2: Command Line Arguments

- To convert old files: `python AnimationJsonConverter.py --mode convert`
- To enhance tags: `python AnimationJsonConverter.py --mode enhance`

## Converting Old JSON Files

1. Place your old animation JSON files in the `anims/` folder
2. Run the converter in conversion mode
3. Check the `output/` folder for the converted files
4. Review any conversion issues in the generated `*_conversion_issues.txt` files

## Enhancing Already Converted Files

If you have already converted JSONs but they lack proper tags (which help in searching and categorizing animations in-game):

1. Place your converted JSON files in the `enhance/` folder
2. Run the converter in tag enhancement mode
3. Check the `enhanced/` folder for the updated files with added tags

## Customizing the Converter

The top section of the script contains several user-configurable constants that you can modify to adjust the converter's behavior:

### Configuration Options

```python
# Enable automatic tag inference when tags are missing
ENABLE_TAG_INFERENCE = True

# Settings for climax animations
CLIMAX_DEFAULT_SETTINGS = {
    "IsLooping": False,
    "IsErotic": True,
    "IsClimax": True
}

# Used to check if a character is a boss variant
BOSS_PREFIX = "BOSS_"
```

### Equipment Mappings

Customize the default equipment assigned to different character types:

```python
DEFAULT_EQUIPMENT = {
    "Human": [],  # Humans don't get default equipment
    "DEFAULT_PAL": ["Vagina"],  # Default for all non-specified pals
    # Add your custom mappings here
}

# Sex requirement mappings for special requirements
SEX_REQUIREMENT_MAP = {
    "female/male": ["Vagina", "Penis"],
    # Add your custom mappings here
}
```

### Tag Mappings

Add or modify inferences for tags based on names, equipment, or act types:

```python
# Name pattern to tag mappings
NAME_PATTERN_TO_TAG_MAP = {
    "blowjob": ["Blowjob", "Oral"],
    "anal": ["Anal"],
    # Add your mappings here
}

# Default positioning/style tags based on actor count
DEFAULT_ACTOR_COUNT_TAGS = {
    1: ["Solo"],
    2: ["Duo"],
    # Add your mappings here
}
```

## Common Issues and Solutions

### Missing Tags

If your converted animations don't have tags, use the tag enhancement mode to automatically add them.

### Incorrect Equipment Requirements

Check the `ACT_LOCATION_MAP` and `TAG_EQUIPMENT` mappings in the constants section to adjust equipment assignments.

### Character Compatibility Issues

The converter preserves all character compatibility from the original file, including both normal and boss variants.

### Missing Act Types

If act types are missing, they'll be inferred from tags or animation names. Check `DEFAULT_TAG_ACT_TYPES` to customize.

## Example Before & After

### Old Format (Input)
```json
{
  "UniqueAnimID": "ExampleAnimation",
  "AnimByPath": [
    "/Game/Path/To/PalAnimation",
    "/Game/Path/To/PlayerAnimation"
  ],
  "Tags": ["Duo", "Cowgirl"],
  "ActTypes": [
    {
      "ActorSlot": 0,
      "ActType": "Penetrated",
      "ActLocation": "Vaginal"
    }
  ]
}
```

### New Format (Output)
```json
{
  "SCakeAnimSlot": [
    {
      "UniqueID": "ExampleAnimation_0",
      "SEquipReq": ["Vagina"],
      "AnimSet": [{"CharacterID": ["PalName"], "AssetPath": "/Game/Path/To/PalAnimation"}],
      "Tags": ["Duo", "Cowgirl"]
    },
    {
      "UniqueID": "ExampleAnimation_1",
      "SEquipReq": ["Penis"],
      "AnimSet": [{"CharacterID": ["Human"], "AssetPath": "/Game/Path/To/PlayerAnimation"}],
      "Tags": ["Duo", "Cowgirl"]
    }
  ],
  "SCakeAnimEvent": [
    {
      "UniqueID": "ExampleAnimation_EVENT",
      "Stages": [
        {
          "SlotAnims": ["ExampleAnimation_0", "ExampleAnimation_1"],
          "SlotData": [
            {
              "ActorSlot": 0,
              "ActTypes": ["Penetrated_Vaginal"]
            },
            {
              "ActorSlot": 1,
              "ActTypes": ["Penetrating_Vaginal"]
            }
          ]
        }
      ],
      "AddTags": ["Duo", "Cowgirl"]
    }
  ]
}
```

## Frequently Asked Questions

**Q: Will this converter work with all old-format files?**  
A: The converter is designed to handle most common formats, but extremely customized or non-standard JSONs might require manual adjustments.

**Q: Do I need to keep my original files?**  
A: Yes, it's always a good practice to keep your original files as backup.

**Q: Can I convert multiple files at once?**  
A: Yes, place all your files in the appropriate folder and the converter will process them in batch.

**Q: What if there are errors during conversion?**  
A: Check the corresponding `*_conversion_issues.txt` file for detailed logs of any issues encountered.