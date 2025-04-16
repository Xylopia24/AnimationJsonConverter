import json
import os
import shutil
import re
from datetime import datetime
import argparse

#############################################
########### CONFIGURATION OPTIONS ###########
#############################################

# Enable automatic tag inference when tags are missing
ENABLE_TAG_INFERENCE = True

# Settings for climax animations
CLIMAX_DEFAULT_SETTINGS = {
    "IsLooping": False,
    "IsErotic": True,
    "IsClimax": True
}

# Used to check if a character is a boss variant - will be treated as equivalent to base version
BOSS_PREFIX = "BOSS_"

# Enable tag enhancement mode by default when using that function
TAG_ENHANCEMENT_MODE = True

#############################################
############ EQUIPMENT MAPPINGS #############
#############################################

# Default equipment for character types - What equipment to assign if nothing is specified
DEFAULT_EQUIPMENT = {
    "Human": [],  # Humans don't get default equipment
    "DEFAULT_PAL": ["Vagina"],  # Default equipment for all non-specified pals
    
    # Add specific character defaults
    # "CharacterName": ["Equipment1", "Equipment2"],
}

# Sex requirement mappings for composite or special sex requirements
SEX_REQUIREMENT_MAP = {
    "female/male": ["Vagina", "Penis"],
    "male/female": ["Penis", "Vagina"],
    "futa": ["Penis", "Breasts"],
    "fullfuta": ["Penis", "Vagina", "Breasts" ],
    "any": []  # Empty list means no specific requirements
}

#############################################
####### LOCATION AND ACT TYPE MAPPINGS ######
#############################################

# Act Location Mappings - Add or change mappings for different body terms to standard locations
ACT_LOCATION_MAP = {
    # Standard body parts
    "penis": "Body",
    "slit": "Vaginal",
    "tits": "Breasts",
    "mouth": "Oral",
    "breasts": "Breasts",
    "breast": "Breasts",
    "boobs": "Breasts",
    "chest": "Breasts",
    "butt": "Anal",
    "ass": "Anal",
    "anus": "Anal",
    "face": "Oral",
    "butthole": "Anal",
    "feet": "Feet",
    "foot": "Feet",
    "thighs": "Body",
    "hands": "Body",
    "hand": "Body",
    "armpit": "Body",
    
    # Add your custom mappings here
    # "custom_term": "Standard_SCake_Location",
}

# Act Type Mappings - Define how different act types should be normalized
ACT_TYPE_MAP = {
    # Special cases based on action and location
    "servicing_penis": "Handling_Body",
    "serviced_penis": "External_Body", 
    "sucking_any": "Penetrating_Oral",
    "sucked_any": "Penetrated_Oral",
    "masturbation_penis": "Masturbation_Body",
    
    # Add your custom mappings here
    # "custom_act_location": "Standard_SCake_Type_Location",
}

#############################################
############## TAG MAPPINGS #################
#############################################

# Equipment assignments based on tags - What equipment is required when certain tags are found
TAG_EQUIPMENT = {
    "Blowjob": [{"actor": 0, "equipment": ["Mouth"]}, 
                {"actor": 1, "equipment": ["Penis"]}],
    "Anal": [{"actor": 0, "equipment": ["Anus"]}, 
             {"actor": 1, "equipment": ["Penis"]}],
    "Breast": [{"actor": 0, "equipment": ["Breasts"]}, 
               {"actor": 1, "equipment": ["Penis"]}],
    "Tits": [{"actor": 0, "equipment": ["Breasts"]}, 
             {"actor": 1, "equipment": ["Penis"]}],
    "Boob": [{"actor": 0, "equipment": ["Breasts"]}, 
             {"actor": 1, "equipment": ["Penis"]}],
    "Chest": [{"actor": 0, "equipment": ["Breasts"]}, 
              {"actor": 1, "equipment": ["Penis"]}],
    
    # Add your tag-based equipment here
    # "CustomTag": [{"actor": 0, "equipment": ["Equip1"]}, 
    #               {"actor": 1, "equipment": ["Equip2"]}],
}

# Default act types to assign when specific tags are found but no explicit act types exist
DEFAULT_TAG_ACT_TYPES = {
    "Blowjob": [{"actor": 0, "act_type": "Penetrated_Oral"},
                {"actor": 1, "act_type": "Penetrating_Oral"}],
    "Anal": [{"actor": 0, "act_type": "Penetrated_Anal"},
             {"actor": 1, "act_type": "Penetrating_Anal"}],
    "Breast": [{"actor": 0, "act_type": "Penetrated_Breasts"},
               {"actor": 1, "act_type": "Penetrating_Breasts"}],
    "Tits": [{"actor": 0, "act_type": "Penetrated_Breasts"},
             {"actor": 1, "act_type": "Penetrating_Breasts"}],
    "Cowgirl": [{"actor": 0, "act_type": "Penetrated_Vaginal"},
                {"actor": 1, "act_type": "Penetrating_Vaginal"}],
    
    # Add your tag-based act types here
    # "CustomTag": [{"actor": 0, "act_type": "Custom_ActType"}, 
    #               {"actor": 1, "act_type": "Custom_ActType"}],
}

# Act type to tag mappings - Automatically suggest tags based on act types
ACT_TYPE_TO_TAG_MAP = {
    "Penetrated_Vaginal": ["Vaginal", "Sex"],
    "Penetrating_Vaginal": ["Vaginal", "Sex"],
    "Penetrated_Anal": ["Anal", "Sex"],
    "Penetrating_Anal": ["Anal", "Sex"],
    "Penetrated_Oral": ["Blowjob", "Oral"],
    "Penetrating_Oral": ["Blowjob", "Oral"],
    "Penetrated_Breasts": ["Breast", "Titjob"],
    "Penetrating_Breasts": ["Breast", "Titjob"],
    "Masturbation_Body": ["Masturbation", "Solo"],
    "Masturbation_Vaginal": ["Masturbation", "Solo", "Vaginal"],
    "Handling_Body": ["Handjob"],
    "External_Body": ["Grinding", "Foreplay"],
}

# Name pattern to tag mappings - Suggest tags based on animation/event name patterns
NAME_PATTERN_TO_TAG_MAP = {
    "blowjob": ["Blowjob", "Oral"],
    "anal": ["Anal"],
    "vaginal": ["Vaginal"],
    "cowgirl": ["Cowgirl", "Riding"],
    "reverse": ["Reverse"],
    "doggystyle": ["Doggystyle"],
    "missionary": ["Missionary"],
    "handjob": ["Handjob"],
    "titjob": ["Titjob", "Breast"],
    "titfuck": ["Titjob", "Breast"],
    "masturbat": ["Masturbation", "Solo"],
    "ride": ["Riding"],
    "oral": ["Oral"],
    "rimjob": ["Rimjob", "Oral", "Anal"],
    "solo": ["Solo"],
    "duo": ["Duo"],
    "threesome": ["Threesome"],
    "femdom": ["Femdom"],
    "maledom": ["Maledom"],
}

# Default positioning/style tags to add based on actor count
DEFAULT_ACTOR_COUNT_TAGS = {
    1: ["Solo"],
    2: ["Duo"],
    3: ["Threesome"],
    4: ["Foursome", "Group"]
}

#############################################
########## END OF USER CONSTANTS ############
#############################################

def ensure_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Create a global issues log to track conversion problems
class IssuesLog:
    def __init__(self, output_dir):
        self.issues = []
        self.output_dir = output_dir
        
    def log_issue(self, source_file, section, message, data=None):
        """Log an issue encountered during conversion"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        issue = {
            "timestamp": timestamp,
            "file": source_file,
            "section": section,
            "message": message,
            "data": data
        }
        self.issues.append(issue)
    
    def save_to_file(self, source_file_name):
        """Save all logged issues to a text file"""
        if not self.issues:
            return
            
        base_name = os.path.splitext(source_file_name)[0]
        issues_filename = f"{base_name}_conversion_issues.txt"
        issues_path = os.path.join(self.output_dir, issues_filename)
        
        with open(issues_path, 'w', encoding='utf-8') as f:
            f.write(f"=== Conversion Issues for {source_file_name} ===\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for idx, issue in enumerate(self.issues, 1):
                f.write(f"Issue #{idx} [{issue['timestamp']}] - {issue['section']}:\n")
                f.write(f"  {issue['message']}\n")
                if issue['data'] is not None:
                    f.write(f"  Data: {json.dumps(issue['data'], indent=2)}\n")
                f.write("\n")
        
        print(f"Logged {len(self.issues)} conversion issues to: {issues_filename}")
        return issues_path

def normalize_act_location(location):
    """Normalize various act locations to SCake 0.5.2+ standard"""
    if not location:
        return location
        
    location_lower = location.lower()
    if location_lower in ACT_LOCATION_MAP:
        return ACT_LOCATION_MAP[location_lower]
    return location

def normalize_act_type(act_type, location):
    """Normalize various act types to SCake 0.5.2+ standard"""
    if not act_type or not location:
        return act_type
        
    # Check for specific type+location mappings
    key = f"{act_type.lower()}_{location.lower()}"
    if key in ACT_TYPE_MAP:
        type_loc = ACT_TYPE_MAP[key].split("_", 1)
        return type_loc[0] if len(type_loc) > 0 else act_type
    
    # Check for type with any location
    key = f"{act_type.lower()}_any"
    if key in ACT_TYPE_MAP:
        type_loc = ACT_TYPE_MAP[key].split("_", 1)
        return type_loc[0] if len(type_loc) > 0 else act_type
    
    return act_type

def get_character_base_id(character_id):
    """Get base character ID by removing known prefixes like 'BOSS_'"""
    if character_id.startswith(BOSS_PREFIX):
        return character_id[len(BOSS_PREFIX):]
    return character_id

def is_human_character(character_id):
    """Check if a character ID refers to a human character"""
    base_id = get_character_base_id(character_id)
    return base_id == "Human"

def add_equipment_for_tag(equip_req, tag, actor_idx):
    """Add equipment based on tags for the specified actor"""
    if tag not in TAG_EQUIPMENT:
        return
        
    for entry in TAG_EQUIPMENT[tag]:
        if entry["actor"] == actor_idx:
            for equip in entry["equipment"]:
                if equip not in equip_req:
                    equip_req.append(equip)

def get_act_type_for_tag(tag, actor_idx):
    """Get default act type for a tag and actor"""
    if tag not in DEFAULT_TAG_ACT_TYPES:
        return None
        
    for entry in DEFAULT_TAG_ACT_TYPES[tag]:
        if entry["actor"] == actor_idx:
            return entry["act_type"]
    
    return None

def parse_sex_requirement(req):
    """Parse sex requirement string and return appropriate equipment requirements"""
    if not req:
        return []
        
    # Check if it's a special case in our mapping
    req_lower = req.lower()
    if req_lower in SEX_REQUIREMENT_MAP:
        return SEX_REQUIREMENT_MAP[req_lower]
    
    # Handle standard cases
    if req_lower == "male":
        return ["Penis"]
    elif req_lower == "female":
        return ["Vagina", "Breasts"]
    elif req_lower == "none":
        return []
        
    # For unrecognized formats, return empty list and let calling code handle logging
    return []

def infer_tags_from_act_types(act_types):
    """Infer tags based on act types"""
    if not ENABLE_TAG_INFERENCE:
        return []
        
    inferred_tags = []
    for act_type in act_types:
        if act_type in ACT_TYPE_TO_TAG_MAP:
            for tag in ACT_TYPE_TO_TAG_MAP[act_type]:
                if tag not in inferred_tags:
                    inferred_tags.append(tag)
    return inferred_tags

def infer_tags_from_name(name):
    """Infer tags based on animation or event name"""
    if not ENABLE_TAG_INFERENCE or not name:
        return []
        
    inferred_tags = []
    name_lower = name.lower()
    
    for pattern, tags in NAME_PATTERN_TO_TAG_MAP.items():
        if pattern in name_lower:
            for tag in tags:
                if tag not in inferred_tags:
                    inferred_tags.append(tag)
    return inferred_tags

def infer_tags_from_equipment(equipment):
    """Infer tags based on required equipment"""
    if not ENABLE_TAG_INFERENCE:
        return []
        
    inferred_tags = []
    
    # These are simple mappings; expand as needed
    if "Penis" in equipment:
        if "Vagina" in equipment:
            inferred_tags.append("Futa")
    
    return inferred_tags

def enhance_tags_in_converted_file(file_path, output_dir, issues_log):
    """Add or enhance tags in already-converted JSON files"""
    print(f"Enhancing tags in: {os.path.basename(file_path)}")
    
    try:
        # Load the converted JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            converted_json = json.load(f)
        
        # Check if it's already in the new format (has SCakeAnimSlot and SCakeAnimEvent)
        if "SCakeAnimSlot" not in converted_json or "SCakeAnimEvent" not in converted_json:
            issues_log.log_issue(os.path.basename(file_path), "Format", 
                                "File doesn't appear to be in SCake 0.5.2+ format")
            return None
            
        # Track all inferred tags by animation ID
        animation_tags = {}
        
        # Enhanced animation slots with tags
        for slot_idx, anim_slot in enumerate(converted_json["SCakeAnimSlot"]):
            unique_id = anim_slot.get("UniqueID", f"Unknown_{slot_idx}")
            
            # Skip if the animation already has tags
            if "Tags" in anim_slot and anim_slot["Tags"]:
                # Just store for later use with events
                base_id = unique_id.rsplit('_', 1)[0] if '_' in unique_id else unique_id
                animation_tags[base_id] = anim_slot["Tags"]
                continue
                
            # Infer tags based on the animation name/ID
            name_tags = infer_tags_from_name(unique_id)
            
            # Extract act types from this slot if possible
            act_types_list = []
            for event in converted_json.get("SCakeAnimEvent", []):
                for stage in event.get("Stages", []):
                    if unique_id in stage.get("SlotAnims", []):
                        for slot_data in stage.get("SlotData", []):
                            if slot_data.get("ActorSlot") == 0 and "ActTypes" in slot_data:
                                act_types_list.extend(slot_data["ActTypes"])
            
            # Infer tags from act types
            act_tags = infer_tags_from_act_types(act_types_list)
            
            # Infer tags based on equipment requirements
            equip_tags = infer_tags_from_equipment(anim_slot.get("SEquipReq", []))
            
            # Get base ID (without the actor number suffix)
            base_id = unique_id.rsplit('_', 1)[0] if '_' in unique_id else unique_id
            
            # Combine all inferred tags
            all_tags = list(set(name_tags + act_tags + equip_tags))
            
            # Store by base ID for use with events
            if all_tags and base_id not in animation_tags:
                animation_tags[base_id] = all_tags
                
            # Add the tags to the animation slot
            if all_tags:
                anim_slot["Tags"] = all_tags
                issues_log.log_issue(os.path.basename(file_path), f"Animation {unique_id}", 
                                    f"Added inferred tags: {', '.join(all_tags)}")
        
        # Enhance event tags
        for event in converted_json["SCakeAnimEvent"]:
            event_id = event.get("UniqueID", "Unknown_Event")
            
            # Skip if the event already has tags
            if "AddTags" in event and event["AddTags"]:
                continue
                
            # Infer tags from the event ID/name
            event_tags = infer_tags_from_name(event_id)
            
            # Look for animation tags from this event's stages
            anim_tags = []
            first_anim_id = None
            
            # Get first animation for actor count tags
            for stage in event.get("Stages", []):
                if stage.get("SlotAnims"):
                    first_slot = stage["SlotAnims"][0]
                    first_anim_id = first_slot.rsplit('_', 1)[0] if '_' in first_slot else first_slot
                    break
            
            # Get animation tags
            for stage in event.get("Stages", []):
                for slot in stage.get("SlotAnims", []):
                    base_id = slot.rsplit('_', 1)[0] if '_' in slot else slot
                    if base_id in animation_tags:
                        anim_tags.extend(animation_tags[base_id])
            
            # Add default tags based on actor count
            actor_count = event.get("ActorCount", 1)
            if actor_count in DEFAULT_ACTOR_COUNT_TAGS:
                event_tags.extend(DEFAULT_ACTOR_COUNT_TAGS[actor_count])
            
            # Add unique act types to tag inference
            act_type_tags = []
            for stage in event.get("Stages", []):
                for slot_data in stage.get("SlotData", []):
                    if "ActTypes" in slot_data:
                        act_type_tags.extend(infer_tags_from_act_types(slot_data["ActTypes"]))
            
            # Combine all tags, remove duplicates
            all_tags = list(set(event_tags + anim_tags + act_type_tags))
            
            # Add tags to the event
            if all_tags:
                event["AddTags"] = all_tags
                issues_log.log_issue(os.path.basename(file_path), f"Event {event_id}", 
                                    f"Added inferred tags: {', '.join(all_tags)}")
        
        # Save the enhanced file
        output_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_Enhanced.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(converted_json, f, indent=4)
            
        print(f"Tags enhanced and saved to: {output_filename}")
        return output_path
        
    except Exception as e:
        issues_log.log_issue(os.path.basename(file_path), "General", f"Error enhancing tags: {str(e)}")
        print(f"Error enhancing tags in {os.path.basename(file_path)}: {str(e)}")
        return None

def process_tag_enhancement_mode():
    """Process files in tag enhancement mode"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "enhance")
    output_dir = os.path.join(script_dir, "enhanced")
    
    ensure_directory(input_dir)
    ensure_directory(output_dir)
    
    json_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.json')]
    
    if not json_files:
        print("No JSON files found in the 'enhance' folder. Please add already-converted JSON files and try again.")
        return
    
    for json_file in json_files:
        input_path = os.path.join(input_dir, json_file)
        issues_log = IssuesLog(output_dir)
        
        result = enhance_tags_in_converted_file(input_path, output_dir, issues_log)
        
        if result:
            issues_path = issues_log.save_to_file(json_file)
            if issues_path:
                print(f"Tag enhancement details logged to: {issues_path}")
    
    print("\nTag enhancement complete!")
    print(f"Enhanced files are in: {output_dir}")

def convert_animation(old_json, source_file, issues_log):
    """Convert old animation format to new format"""
    new_json = {
        "DevNote": f"This is a conversion JSON for {old_json.get('PackName', 'Unknown')} so it can be used with SCake 0.6+.",
        "ACakeVersion": "0005009",
        "PackName": old_json.get("PackName", "Unknown"),
        "PackAuthor": old_json.get("PackAuthor", "Unknown"),
        "SCakeAnimSlot": [],
        "SCakeAnimEvent": []
    }
    
    # Map to track unique IDs for animations
    anim_map = {}
    
    # Track climax animations for each animation
    climax_map = {}
    
    # Track inferred tags for each animation
    animation_tags = {}
    
    # Process RegisterAnim entries
    for idx, anim in enumerate(old_json.get("RegisterAnim", [])):
        try:
            unique_id = anim.get("UniqueAnimID", f"Unknown_{idx}")
            anim_name = anim.get("AnimName", unique_id)
            
            # Get animation paths (typically first is for pal, second for player)
            anim_paths = anim.get("AnimByPath", [])
            if not anim_paths:
                issues_log.log_issue(source_file, f"Animation {unique_id}", "No animation paths found", anim)
                continue
            
            # Extract tags or infer them if missing
            tags = anim.get("Tags", [])
            if not tags and ENABLE_TAG_INFERENCE:
                # Infer tags from animation name
                name_tags = infer_tags_from_name(anim_name)
                
                # Infer tags from actor count
                actor_count = len(anim_paths)
                if actor_count in DEFAULT_ACTOR_COUNT_TAGS:
                    name_tags.extend(DEFAULT_ACTOR_COUNT_TAGS[actor_count])
                
                # Infer tags from act types
                act_types_list = []
                for act_type in anim.get("ActTypes", []):
                    act = act_type.get("ActType", "")
                    location = act_type.get("ActLocation", "")
                    
                    if act and location:
                        # Normalize both
                        normalized_location = normalize_act_location(location)
                        normalized_act = normalize_act_type(act, location)
                        act_types_list.append(f"{normalized_act}_{normalized_location}")
                
                act_tags = infer_tags_from_act_types(act_types_list)
                
                # Combine all inferred tags, remove duplicates
                tags = list(set(name_tags + act_tags))
                
                if tags:
                    issues_log.log_issue(source_file, f"Animation {unique_id}", 
                                        f"Inferred tags for animation: {', '.join(tags)}", None)
            
            # Store tags for later use in events
            animation_tags[unique_id] = tags
            
            # Continue with the existing animation processing
            has_blowjob_tag = any(tag.lower() == "blowjob" for tag in tags)
            has_anal_tag = any(tag.lower() == "anal" or "anal" in tag.lower() for tag in tags)
            has_breast_tag = any(tag.lower() in ["breast", "tits", "boob", "chest"] for tag in tags)
            
            # Get act types for equipment determination
            act_types = anim.get("ActTypes", [])
            
            # Create separate entries for each actor
            for actor_idx, path in enumerate(anim_paths):
                new_anim = {
                    "UniqueID": f"{unique_id}_{actor_idx}",
                    "IsLooping": anim.get("IsLooping", True),
                    "IsErotic": not anim.get("NonErotic", False),  # Invert NonErotic
                }
                
                # Add tags to animation slot
                if tags:
                    new_anim["Tags"] = tags
                
                # Process face expressions if available
                if "FaceExpress" in anim and isinstance(anim["FaceExpress"], list) and len(anim["FaceExpress"]) > actor_idx:
                    new_anim["FaceExpress"] = anim["FaceExpress"][actor_idx]
                
                if "FaceExpressClimax" in anim and isinstance(anim["FaceExpressClimax"], list) and len(anim["FaceExpressClimax"]) > actor_idx:
                    new_anim["FaceExpressClimax"] = anim["FaceExpressClimax"][actor_idx]
                
                # Determine sex equipment requirement based on compatibility and animation types
                equip_req = []
                
                # Check each compatibility entry for more comprehensive requirements
                if "Compatibility" in anim and anim["Compatibility"]:
                    for compat in anim["Compatibility"]:
                        sex_req = compat.get("SexEquipReq", [])
                        if len(sex_req) > actor_idx:
                            req = sex_req[actor_idx]
                            
                            parsed_req = parse_sex_requirement(req)
                            if parsed_req:
                                for equip in parsed_req:
                                    if equip not in equip_req:
                                        equip_req.append(equip)
                            elif req != "None" and req:
                                issues_log.log_issue(source_file, f"Animation {unique_id}", 
                                                    f"Unknown sex requirement: {req} for actor {actor_idx}", 
                                                    {"compat": compat})
                
                # Check act types for this actor
                for act_type in act_types:
                    if act_type.get("ActorSlot") == actor_idx:
                        act = act_type.get("ActType", "")
                        location = act_type.get("ActLocation", "")
                        
                        if not act or not location:
                            issues_log.log_issue(source_file, f"Animation {unique_id}", 
                                                f"Incomplete act type for actor {actor_idx}", act_type)
                            continue
                        
                        normalized_location = normalize_act_location(location)
                        normalized_act = normalize_act_type(act, location)
                        
                        if normalized_location == "Oral":
                            if normalized_act in ["Penetrated", "Sucked"] and "Mouth" not in equip_req:
                                equip_req.append("Mouth")
                            elif normalized_act in ["Penetrating", "Sucking"] and "Penis" not in equip_req:
                                equip_req.append("Penis")
                        
                        elif normalized_location == "Vaginal":
                            if normalized_act == "Penetrated" and "Vagina" not in equip_req:
                                equip_req.append("Vagina")
                            elif normalized_act == "Penetrating" and "Penis" not in equip_req:
                                equip_req.append("Penis")
                        
                        elif normalized_location == "Anal":
                            if normalized_act == "Penetrated" and "Anus" not in equip_req:
                                equip_req.append("Anus")
                            elif normalized_act == "Penetrating" and "Penis" not in equip_req:
                                equip_req.append("Penis")
                        
                        elif normalized_location == "Breasts":
                            if normalized_act == "Penetrated" and "Breasts" not in equip_req:
                                equip_req.append("Breasts")
                            elif normalized_act == "Penetrating" and "Penis" not in equip_req:
                                equip_req.append("Penis")
                        
                        elif normalized_location == "Body":
                            if normalized_act == "Penetrating" and "Penis" not in equip_req:
                                equip_req.append("Penis")
                        
                        elif act == "Masturbation" and location.lower() == "penis":
                            if "Penis" not in equip_req:
                                equip_req.append("Penis")
                
                for tag in tags:
                    add_equipment_for_tag(equip_req, tag, actor_idx)
                
                if not equip_req and actor_idx == 0:
                    is_non_human = True
                    character_ids = set()
                    
                    if "Compatibility" in anim and anim["Compatibility"]:
                        for compat in anim["Compatibility"]:
                            by_id = compat.get("ByID", [])
                            if len(by_id) > actor_idx and by_id[actor_idx]:
                                character_id = by_id[actor_idx]
                                character_ids.add(character_id)
                                if is_human_character(character_id):
                                    is_non_human = False
                                    break
                    
                    if is_non_human:
                        character_base = get_character_base_id(next(iter(character_ids), ""))
                        if character_base in DEFAULT_EQUIPMENT:
                            equip_req.extend(DEFAULT_EQUIPMENT[character_base])
                        else:
                            equip_req.extend(DEFAULT_EQUIPMENT["DEFAULT_PAL"])
                
                if not equip_req:
                    equip_req = ["None"]
                
                new_anim["SEquipReq"] = equip_req
                    
                new_anim["AnimSet"] = []
                
                character_ids = set()
                if "Compatibility" in anim and anim["Compatibility"]:
                    for compat in anim["Compatibility"]:
                        by_id = compat.get("ByID", [])
                        if len(by_id) > actor_idx and by_id[actor_idx]:
                            character_ids.add(by_id[actor_idx])
                
                if not character_ids:
                    character_ids = {"Unknown"}
                    issues_log.log_issue(source_file, f"Animation {unique_id}", 
                                        f"No character ID found for actor {actor_idx}", 
                                        {"compatibility": anim.get("Compatibility", [])})
                
                new_anim["AnimSet"].append({
                    "CharacterID": list(character_ids),
                    "AssetPath": path
                })
                
                new_json["SCakeAnimSlot"].append(new_anim)
                
                if unique_id not in anim_map:
                    anim_map[unique_id] = []
                anim_map[unique_id].append(f"{unique_id}_{actor_idx}")
            
            # Process LinkClimaxAnims if present
            if "LinkClimaxAnims" in anim:
                climax_entries = []
                
                # Check if it's a list (original format) or a dictionary (alternate format)
                if isinstance(anim["LinkClimaxAnims"], list):
                    # Original list format
                    climax_entries = anim["LinkClimaxAnims"]
                elif isinstance(anim["LinkClimaxAnims"], dict):
                    # Dictionary format with named climax entries
                    climax_entries = list(anim["LinkClimaxAnims"].values())
                else:
                    issues_log.log_issue(source_file, f"Animation {unique_id}",
                                      f"Unsupported LinkClimaxAnims format: {type(anim['LinkClimaxAnims']).__name__}",
                                      anim["LinkClimaxAnims"])
                    continue
                
                for climax_idx, climax_anim in enumerate(climax_entries):
                    # Create a unique ID for the climax animation
                    climax_id = f"{unique_id}_CLIMAX_{climax_idx}"
                    
                    # Get climax animation paths
                    climax_paths = climax_anim.get("AnimByPath", [])
                    if not climax_paths:
                        issues_log.log_issue(source_file, f"Animation {unique_id}", 
                                            f"No paths found for climax animation {climax_idx}", climax_anim)
                        continue
                    
                    # Create animation slots for climax animations
                    climax_anim_slots = []
                    for actor_idx, path in enumerate(climax_paths):
                        if actor_idx >= len(anim_paths):  # Skip if we don't have enough base animations
                            continue
                            
                        climax_slot_id = f"{climax_id}_{actor_idx}"
                        
                        # Create new animation slot for climax
                        new_climax_anim = {
                            "UniqueID": climax_slot_id,
                            "IsLooping": climax_anim.get("IsLooping", CLIMAX_DEFAULT_SETTINGS["IsLooping"]),
                            "IsErotic": True,
                            "IsClimax": True,
                            "SEquipReq": new_json["SCakeAnimSlot"][-len(climax_paths) + actor_idx]["SEquipReq"],
                            "AnimSet": [{
                                "CharacterID": new_json["SCakeAnimSlot"][-len(climax_paths) + actor_idx]["AnimSet"][0]["CharacterID"],
                                "AssetPath": path
                            }]
                        }
                        
                        # Add tags to climax animation slots
                        if tags:
                            new_climax_anim["Tags"] = tags
                        
                        # Process face expressions for climax if available
                        if "FaceExpress" in anim and isinstance(anim["FaceExpress"], list) and len(anim["FaceExpress"]) > actor_idx:
                            new_climax_anim["FaceExpress"] = anim["FaceExpress"][actor_idx]
                        
                        if "FaceExpressClimax" in anim and isinstance(anim["FaceExpressClimax"], list) and len(anim["FaceExpressClimax"]) > actor_idx:
                            new_climax_anim["FaceExpressClimax"] = anim["FaceExpressClimax"][actor_idx]
                        
                        # Add to new JSON
                        new_json["SCakeAnimSlot"].append(new_climax_anim)
                        climax_anim_slots.append(climax_slot_id)
                    
                    # Store climax information for later event processing
                    slots_to_climax = []
                    climax_locations = {}
                    
                    # Process SlotsToClimax information
                    if "SlotsToClimax" in climax_anim:
                        for slot_info in climax_anim["SlotsToClimax"]:
                            try:
                                actor_slot = int(slot_info.get("ActorSlot", "0"))
                                slots_to_climax.append(actor_slot)
                                climax_locations[actor_slot] = slot_info.get("Location", "Outside")
                            except ValueError:
                                # Handle case where ActorSlot might be a string
                                issues_log.log_issue(source_file, f"Animation {unique_id}", 
                                                    f"Invalid ActorSlot value in climax info: {slot_info.get('ActorSlot')}", slot_info)
                    
                    # Store the mapping
                    if unique_id not in climax_map:
                        climax_map[unique_id] = []
                    
                    climax_map[unique_id].append({
                        "slots_to_climax": slots_to_climax,
                        "climax_anim_slots": climax_anim_slots,
                        "climax_locations": climax_locations
                    })
                
        except Exception as e:
            issues_log.log_issue(source_file, f"Animation {idx}", f"Error processing animation: {str(e)}", anim)
    
    for event_idx, event in enumerate(old_json.get("RegisterEvent", [])):
        try:
            event_id = event.get("UniqueEventID", f"Unknown_Event_{event_idx}")
            event_name = event.get("EventName", event_id)
            
            anim_id = None
            if event.get("Stages", []):
                anim_id = event["Stages"][0].get("AnimID", "")
            
            if not anim_id or anim_id not in anim_map:
                issues_log.log_issue(source_file, f"Event {event_id}", 
                                    f"Animation ID {anim_id} not found in mappings", event)
                continue
                
            new_event = {
                "UniqueID": event_id,
                "IsErotic": True,
                "ActorCount": len(anim_map[anim_id]),
                "Aggressors": [0],
                "Stages": []
            }
            
            # Get tags from event, animation, or infer if missing
            tags = []
            if "AddTags" in event:
                tags = event["AddTags"]
            elif "Addtags" in event:  # Some events use "Addtags" instead of "AddTags"
                tags = event["Addtags"]
            elif anim_id in animation_tags and animation_tags[anim_id]:
                tags = animation_tags[anim_id]
                issues_log.log_issue(source_file, f"Event {event_id}", 
                                    f"Using tags from animation: {', '.join(tags)}", None)
            elif ENABLE_TAG_INFERENCE:
                # Infer tags from event name
                name_tags = infer_tags_from_name(event_name)
                
                # Infer tags from actor count
                actor_count = len(anim_map[anim_id])
                if actor_count in DEFAULT_ACTOR_COUNT_TAGS:
                    name_tags.extend(DEFAULT_ACTOR_COUNT_TAGS[actor_count])
                
                # Combine all inferred tags, remove duplicates
                tags = list(set(name_tags))
                
                if tags:
                    issues_log.log_issue(source_file, f"Event {event_id}", 
                                        f"Inferred tags for event: {', '.join(tags)}", None)
            
            if tags:
                new_event["AddTags"] = tags
            
            for stage_idx, stage in enumerate(event.get("Stages", [])):
                stage_name = stage.get("StageName", f"{event_id}_STAGE{stage_idx+1}")
                stage_anim_id = stage.get("AnimID", "")
                
                if stage_anim_id not in anim_map:
                    issues_log.log_issue(source_file, f"Event {event_id}", 
                                        f"Stage {stage_idx} animation ID {stage_anim_id} not found in mappings", stage)
                    continue
                
                speed_mod = stage.get("SpeedMod", 1.0)
                
                new_stage = {
                    "Name": stage_name,
                    "SlotAnims": anim_map.get(stage_anim_id, []),
                    "SlotData": []
                }
                
                orig_act_types = []
                stage_original_anim = next((a for a in old_json.get("RegisterAnim", []) if a.get("UniqueAnimID") == stage_anim_id), None)
                if stage_original_anim and "ActTypes" in stage_original_anim:
                    orig_act_types = stage_original_anim["ActTypes"]
                
                for actor_idx in range(len(anim_map.get(stage_anim_id, []))):
                    slot_data = {
                        "ActorSlot": actor_idx,
                    }
                    
                    if "SpeedMod" in stage:
                        slot_data["SpeedMod"] = speed_mod
                    
                    act_types = []
                    
                    for act_type in orig_act_types:
                        if act_type.get("ActorSlot") == actor_idx:
                            act = act_type.get("ActType", "")
                            location = act_type.get("ActLocation", "")
                            
                            normalized_location = normalize_act_location(location)
                            normalized_act = normalize_act_type(act, location)
                            
                            if normalized_act and normalized_location:
                                act_types.append(f"{normalized_act}_{normalized_location}")
                    
                    if not act_types:
                        for tag in tags:
                            act_type = get_act_type_for_tag(tag, actor_idx)
                            if act_type and act_type not in act_types:
                                act_types.append(act_type)
                    
                    if not act_types:
                        if actor_idx == 0:
                            act_types.append("Penetrated_Vaginal")
                        else:
                            act_types.append("Penetrating_Vaginal")
                    
                    if act_types:
                        slot_data["ActTypes"] = act_types
                    
                    slot_data = {k: v for k, v in slot_data.items() if v is not None}
                    new_stage["SlotData"].append(slot_data)
                
                if stage_anim_id in climax_map:
                    new_stage["ClimaxVar"] = []
                    
                    for climax_info in climax_map[stage_anim_id]:
                        climax_var = {
                            "SlotsToClimax": climax_info["slots_to_climax"],
                            "SlotAnims": climax_info["climax_anim_slots"],
                            "SlotData": []
                        }
                        
                        for actor_idx, slot_id in enumerate(climax_info["climax_anim_slots"]):
                            if actor_idx >= len(new_stage["SlotData"]):
                                continue
                                
                            slot_data = {
                                "ActorSlot": actor_idx
                            }
                            
                            if actor_idx in climax_info["climax_locations"]:
                                slot_data["ClimaxLocation"] = climax_info["climax_locations"][actor_idx]
                            
                            if "ActTypes" in new_stage["SlotData"][actor_idx]:
                                slot_data["ActTypes"] = new_stage["SlotData"][actor_idx]["ActTypes"]
                            
                            climax_var["SlotData"].append(slot_data)
                        
                        new_stage["ClimaxVar"].append(climax_var)
                
                new_event["Stages"].append(new_stage)
            
            new_json["SCakeAnimEvent"].append(new_event)
        except Exception as e:
            issues_log.log_issue(source_file, f"Event {event_idx}", f"Error processing event: {str(e)}", event)
    
    return new_json

def process_files():
    """Process all JSON files in the anims folder"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    anims_dir = os.path.join(script_dir, "anims")
    output_dir = os.path.join(script_dir, "output")
    
    ensure_directory(anims_dir)
    ensure_directory(output_dir)
    
    json_files = [f for f in os.listdir(anims_dir) if f.lower().endswith('.json')]
    
    if not json_files:
        print("No JSON files found in the 'anims' folder. Please add some files and try again.")
        return
    
    for json_file in json_files:
        input_path = os.path.join(anims_dir, json_file)
        output_filename = os.path.splitext(json_file)[0] + "_Converted.json"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"Processing: {json_file}")
        
        issues_log = IssuesLog(output_dir)
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                try:
                    old_json = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON format in {json_file}")
                    issues_log.log_issue(json_file, "JSON Parsing", f"Invalid JSON format: {str(e)}")
                    issues_log.save_to_file(json_file)
                    continue
            
            new_json = convert_animation(old_json, json_file, issues_log)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(new_json, f, indent=4)
            
            print(f"Successfully converted: {output_filename}")
            
            issues_path = issues_log.save_to_file(json_file)
            if issues_path:
                print(f"Some conversion issues were encountered. See: {issues_path}")
            
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            issues_log.log_issue(json_file, "General", f"Unhandled error: {str(e)}")
            issues_log.save_to_file(json_file)
    
    print("\nConversion complete!")
    print(f"Converted files are in: {output_dir}")

def display_menu():
    """Display the main menu for the converter"""
    print("\nSCake Animation JSON Converter - Main Menu")
    print("==========================================")
    print("1. Convert old JSON files to new format")
    print("2. Enhance tags in already-converted files")
    print("3. Exit")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if 1 <= choice <= 3:
                return choice
            else:
                print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    print("SCake Animation JSON Converter")
    print("------------------------------")
    
    # Check for command line arguments
    parser = argparse.ArgumentParser(description='Convert or enhance SCake animation JSON files.')
    parser.add_argument('--mode', choices=['convert', 'enhance'], 
                        help='Mode to run: "convert" for old to new format, "enhance" for adding tags to converted files')
    args = parser.parse_args()
    
    # Determine mode from arguments or menu
    mode = None
    if args.mode:
        mode = args.mode
    else:
        choice = display_menu()
        if choice == 1:
            mode = 'convert'
        elif choice == 2:
            mode = 'enhance'
        else:
            print("Exiting program.")
            exit()
    
    # Run the appropriate mode
    if mode == 'convert':
        print("Running in conversion mode.")
        print("This tool converts old-format animation JSONs to the new SCake 0.6+ format.")
        print("Place your old JSON files in the 'anims' folder.")
        print("Converted files will be placed in the 'output' folder.\n")
        process_files()
    else:  # mode == 'enhance'
        print("Running in tag enhancement mode.")
        print("This tool adds tags to already-converted SCake 0.6+ format files.")
        print("Place your converted JSON files in the 'enhance' folder.")
        print("Enhanced files will be placed in the 'enhanced' folder.\n")
        process_tag_enhancement_mode()
    
    print("\nOperation completed successfully!")
