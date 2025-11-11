# data_validator.py
"""
Schema validation for rules_engine data files.
Ensures data integrity on load and provides detailed error reporting.
"""
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger("uvicorn.error")


class DataValidationError(Exception):
    """Raised when data validation fails."""
    pass


def validate_abilities_data(abilities_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate abilities.json structure.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(abilities_data, dict):
        errors.append(f"abilities_data must be dict, got {type(abilities_data)}")
        return False, errors
    
    for school_name, school_data in abilities_data.items():
        if not isinstance(school_data, dict):
            errors.append(f"School '{school_name}' is not a dict")
            continue
        
        # Check for required fields
        if "resource" not in school_data and "resource_pool" not in school_data:
            errors.append(f"School '{school_name}' missing 'resource' or 'resource_pool' field")
        
        # Check branches exist
        branches = school_data.get("branches", [])
        if not isinstance(branches, list):
            errors.append(f"School '{school_name}' branches is not a list, got {type(branches)}")
            continue
        
        if not branches:
            errors.append(f"School '{school_name}' has empty branches list")
            continue
        
        # Validate each branch
        for branch_idx, branch in enumerate(branches):
            if not isinstance(branch, dict):
                errors.append(f"Branch {branch_idx} in '{school_name}' is not a dict")
                continue
            
            tiers = branch.get("tiers", [])
            if not isinstance(tiers, list):
                errors.append(f"Branch {branch_idx} in '{school_name}' tiers is not a list")
                continue
            
            if not tiers:
                branch_name = branch.get("branch", f"Branch {branch_idx}")
                errors.append(f"Branch '{branch_name}' in '{school_name}' has empty tiers list")
                continue
            
            # Validate each tier
            for tier_idx, tier in enumerate(tiers):
                if not isinstance(tier, dict):
                    errors.append(f"Tier {tier_idx} in branch {branch_idx} of '{school_name}' is not a dict")
                    continue
                
                if "description" not in tier:
                    errors.append(f"Tier {tier_idx} in branch {branch_idx} of '{school_name}' missing 'description' field")
    
    return len(errors) == 0, errors


def validate_talents_data(talents_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate talents.json structure.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(talents_data, dict):
        errors.append(f"talents_data must be dict, got {type(talents_data)}")
        return False, errors
    
    required_sections = ["single_stat_mastery", "dual_stat_focus", "single_skill_mastery"]
    for section in required_sections:
        if section not in talents_data:
            errors.append(f"Missing required section: '{section}'")
    
    # Validate single_stat_mastery
    stat_mastery = talents_data.get("single_stat_mastery", [])
    if not isinstance(stat_mastery, list):
        errors.append(f"single_stat_mastery must be list, got {type(stat_mastery)}")
    else:
        for idx, talent in enumerate(stat_mastery):
            if not isinstance(talent, dict):
                errors.append(f"single_stat_mastery[{idx}] is not a dict")
                continue
            if "talent_name" not in talent:
                errors.append(f"single_stat_mastery[{idx}] missing 'talent_name' field")
    
    # Validate dual_stat_focus
    dual_focus = talents_data.get("dual_stat_focus", [])
    if not isinstance(dual_focus, list):
        errors.append(f"dual_stat_focus must be list, got {type(dual_focus)}")
    else:
        for idx, talent in enumerate(dual_focus):
            if not isinstance(talent, dict):
                errors.append(f"dual_stat_focus[{idx}] is not a dict")
                continue
            if "talent_name" not in talent:
                errors.append(f"dual_stat_focus[{idx}] missing 'talent_name' field")
    
    # Validate single_skill_mastery
    skill_mastery = talents_data.get("single_skill_mastery", {})
    if not isinstance(skill_mastery, dict):
        errors.append(f"single_skill_mastery must be dict, got {type(skill_mastery)}")
    else:
        for category_name, category_list in skill_mastery.items():
            if not isinstance(category_list, list):
                errors.append(f"single_skill_mastery['{category_name}'] is not a list, got {type(category_list)}")
                continue
            
            for group_idx, skill_group in enumerate(category_list):
                if not isinstance(skill_group, dict):
                    errors.append(f"single_skill_mastery['{category_name}'][{group_idx}] is not a dict")
                    continue
                
                talents_list = skill_group.get("talents", [])
                if not isinstance(talents_list, list):
                    errors.append(f"single_skill_mastery['{category_name}'][{group_idx}]['talents'] is not a list")
                    continue
                
                for talent_idx, talent in enumerate(talents_list):
                    if not isinstance(talent, dict):
                        errors.append(f"single_skill_mastery['{category_name}'][{group_idx}]['talents'][{talent_idx}] is not a dict")
                        continue
                    
                    # Check for either talent_name or name (for backwards compatibility)
                    if "talent_name" not in talent and "name" not in talent:
                        errors.append(f"single_skill_mastery['{category_name}'][{group_idx}]['talents'][{talent_idx}] missing 'talent_name' or 'name' field")
    
    return len(errors) == 0, errors


def validate_origin_choices(origin_data: List[Dict]) -> Tuple[bool, List[str]]:
    """Validate origin_choices.json structure."""
    errors = []
    
    if not isinstance(origin_data, list):
        errors.append(f"origin_choices must be list, got {type(origin_data)}")
        return False, errors
    
    for idx, choice in enumerate(origin_data):
        if not isinstance(choice, dict):
            errors.append(f"origin_choices[{idx}] is not a dict")
            continue
        if "name" not in choice:
            errors.append(f"origin_choices[{idx}] missing 'name' field")
        if "skills" not in choice:
            errors.append(f"origin_choices[{idx}] missing 'skills' field")
    
    return len(errors) == 0, errors


def validate_kingdom_features(features_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate kingdom_features.json structure."""
    errors = []
    
    if not isinstance(features_data, dict):
        errors.append(f"kingdom_features must be dict, got {type(features_data)}")
        return False, errors
    
    for feature_id, feature_data in features_data.items():
        if not isinstance(feature_data, dict):
            errors.append(f"Feature '{feature_id}' is not a dict")
            continue
        
        for kingdom_name, choices_list in feature_data.items():
            if not isinstance(choices_list, list):
                errors.append(f"Feature '{feature_id}' kingdom '{kingdom_name}' is not a list")
                continue
            
            for choice_idx, choice in enumerate(choices_list):
                if not isinstance(choice, dict):
                    errors.append(f"Feature '{feature_id}' kingdom '{kingdom_name}' choice {choice_idx} is not a dict")
                    continue
                if "name" not in choice:
                    errors.append(f"Feature '{feature_id}' kingdom '{kingdom_name}' choice {choice_idx} missing 'name' field")
                if "mods" not in choice:
                    errors.append(f"Feature '{feature_id}' kingdom '{kingdom_name}' choice {choice_idx} missing 'mods' field")
    
    return len(errors) == 0, errors


def validate_all_rules_data(rules_data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Validate all rules data at once.
    Returns (all_valid, dict_of_errors_by_dataset)
    """
    all_errors = {}
    
    # Validate abilities
    valid, errors = validate_abilities_data(rules_data.get("ability_data", {}))
    if not valid:
        all_errors["abilities"] = errors
    
    # Validate talents
    valid, errors = validate_talents_data(rules_data.get("talent_data", {}))
    if not valid:
        all_errors["talents"] = errors
    
    # Validate kingdom_features
    valid, errors = validate_kingdom_features(rules_data.get("kingdom_features_data", {}))
    if not valid:
        all_errors["kingdom_features"] = errors
    
    # Validate origin_choices
    valid, errors = validate_origin_choices(rules_data.get("origin_choices", []))
    if not valid:
        all_errors["origin_choices"] = errors
    
    return len(all_errors) == 0, all_errors
