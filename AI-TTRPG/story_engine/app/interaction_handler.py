# AI-TTRPG/story_engine/app/interaction_handler.py
import httpx
from fastapi import HTTPException
from typing import Dict, Any, Tuple, Optional, List
from . import schemas, services
import logging

logger = logging.getLogger("uvicorn.error")

async def handle_interaction(request: schemas.InteractionRequest) -> schemas.InteractionResponse:
    """
    Handles player interactions with objects based on world state annotations.
    """
    logger.info(f"Handling interaction: Actor '{request.actor_id}' -> Target '{request.target_object_id}' in Loc {request.location_id}")

    async with httpx.AsyncClient() as client:
        try:
            # 1. Get Location Context (including annotations)
            location_context = await services.get_world_location_context(client, request.location_id)
            annotations = location_context.get("ai_annotations")

            if annotations is None:
                logger.warning(f"Location {request.location_id} has no AI annotations.")
                # Decide default behavior: allow interaction? fail? For now, fail.
                return schemas.InteractionResponse(success=False, message="There are no interactable objects here.")

            target_object_state = annotations.get(request.target_object_id)

            if target_object_state is None:
                return schemas.InteractionResponse(success=False, message=f"You don't see a '{request.target_object_id}' here to interact with.")

            # 2. Process Interaction based on Type and Object State
            # --- Example: Simple Door Interaction ---
            if request.interaction_type == "use" and isinstance(target_object_state, dict) and target_object_state.get("type") == "door":
                if target_object_state.get("status") == "locked":
                    # --- Check if player has key ---
                    has_key = False
                    key_needed = target_object_state.get("key_id")

                    if key_needed:
                        logger.info(f"Door requires key: {key_needed}. Checking {request.actor_id}'s inventory.")
                        try:
                            # Call character_engine to get character context
                            char_context = await services.get_character_context(client, request.actor_id)
                            # --- MODIFIED: Use flat inventory ---
                            inventory = char_context.get("inventory", {})
                            # Check if the key_id is a key in the inventory dict with quantity > 0
                            has_key = inventory.get(key_needed, 0) > 0
                            # --- END MODIFIED ---

                            if has_key:
                                logger.info(f"Key '{key_needed}' found in {request.actor_id}'s inventory.")
                            else:
                                logger.info(f"Key '{key_needed}' NOT found in {request.actor_id}'s inventory.")
                        except HTTPException as e:
                            logger.error(f"Failed to get character context for inventory check: {e.detail}")
                            # Keep has_key = False if inventory check fails
                        except Exception as e:
                            logger.exception(f"Unexpected error during inventory check for key {key_needed}: {e}")
                            # Keep has_key = False

                    # --- End check section ---

                    if has_key:
                        # --- THIS BLOCK IS NOW FIXED ---
                        # Key is used, unlock the door and remove the key
                        target_object_state["status"] = "unlocked" # Or "closed", "unlocked" is clearer
                        logger.info(f"Door '{request.target_object_id}' unlocked by {request.actor_id}.")

                        items_removed_list = []

                        # Try to remove the key from inventory
                        try:
                            await services.remove_item_from_character(client, request.actor_id, key_needed, 1)
                            logger.info(f"Removed key '{key_needed}' from {request.actor_id}'s inventory.")
                            items_removed_list.append({"item_id": key_needed, "quantity": 1})
                        except Exception as e:
                            logger.error(f"Failed to remove key {key_needed} after use: {e}. Door is unlocked anyway.")

                        updated_context = await services.update_location_annotations(client, request.location_id, annotations)

                        return schemas.InteractionResponse(
                            success=True,
                            message=f"You use the {key_needed.replace('_', ' ')} and unlock the {request.target_object_id.replace('_', ' ')}.",
                            updated_annotations=updated_context.get("ai_annotations"),
                            items_removed=items_removed_list
                        )
                        # --- END FIX ---
                    else:
                        return schemas.InteractionResponse(success=False, message=f"The {request.target_object_id.replace('_', ' ')} is locked." + (f" It seems to require a '{key_needed}'." if key_needed else ""))

                elif target_object_state.get("status") == "unlocked" or target_object_state.get("status") == "closed":
                    target_object_state["status"] = "open"
                    logger.info(f"Door '{request.target_object_id}' opened by {request.actor_id}.")
                    updated_context = await services.update_location_annotations(client, request.location_id, annotations)
                    return schemas.InteractionResponse(
                        success=True,
                        message=f"You open the {request.target_object_id.replace('_', ' ')}.",
                        updated_annotations=updated_context.get("ai_annotations")
                    )

                elif target_object_state.get("status") == "open":
                    target_object_state["status"] = "closed"
                    logger.info(f"Door '{request.target_object_id}' closed by {request.actor_id}.")
                    updated_context = await services.update_location_annotations(client, request.location_id, annotations)
                    return schemas.InteractionResponse(
                        success=True,
                        message=f"You close the {request.target_object_id.replace('_', ' ')}.",
                        updated_annotations=updated_context.get("ai_annotations")
                    )

                else:
                    return schemas.InteractionResponse(success=False, message="You can't use the door that way right now.")

            # --- Example: Simple Item Pickup ---
            elif request.interaction_type == "use" and isinstance(target_object_state, dict) and target_object_state.get("type") == "item_pickup":
                item_id_to_give = target_object_state.get("item_id")
                quantity = target_object_state.get("quantity", 1)

                if not item_id_to_give:
                    return schemas.InteractionResponse(success=False, message="There's nothing here to pick up.")

                # Add item to character inventory
                try:
                    await services.add_item_to_character(client, request.actor_id, item_id_to_give, quantity)
                    logger.info(f"Item '{item_id_to_give}' (x{quantity}) added to {request.actor_id}'s inventory.")
                    # Remove the item annotation from the location
                    del annotations[request.target_object_id]
                    updated_context = await services.update_location_annotations(client, request.location_id, annotations)

                    return schemas.InteractionResponse(
                        success=True,
                        message=f"You pick up the {request.target_object_id.replace('_', ' ')} ({item_id_to_give} x{quantity}).",
                        updated_annotations=updated_context.get("ai_annotations"),
                        items_added=[{"item_id": item_id_to_give, "quantity": quantity}] # Inform client
                    )
                except HTTPException as e:
                    logger.error(f"Failed to add item {item_id_to_give} to {request.actor_id}: {e.detail}")
                    return schemas.InteractionResponse(success=False, message="You couldn't pick that up.")

            # --- Add more interaction types and object types here ---
            # elif request.interaction_type == "examine":
            #     description = target_object_state.get("description", "You see nothing special.")
            #     return schemas.InteractionResponse(success=True, message=description)

            else:
                return schemas.InteractionResponse(success=False, message=f"You're not sure how to '{request.interaction_type}' the {request.target_object_id.replace('_', ' ')}.")

        except HTTPException as he:
            logger.error(f"HTTPException during interaction: {he.detail}")
            return schemas.InteractionResponse(success=False, message=f"An error occurred: {he.detail}")
        except Exception as e:
            logger.exception(f"Unexpected error during interaction: {e}")
            return schemas.InteractionResponse(success=False, message="An unexpected error occurred during the interaction.")