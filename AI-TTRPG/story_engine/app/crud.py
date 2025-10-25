from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from . import models, schemas
from typing import List, Optional

# --- Campaign ---
def get_campaign(db: Session, campaign_id: int) -> Optional[models.Campaign]:
    return db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()

def create_campaign(db: Session, campaign: schemas.CampaignCreate) -> models.Campaign:
    db_campaign = models.Campaign(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

# --- ActiveQuest ---
def get_quest(db: Session, quest_id: int) -> Optional[models.ActiveQuest]:
    return db.query(models.ActiveQuest).filter(models.ActiveQuest.id == quest_id).first()

def get_quests_for_campaign(db: Session, campaign_id: int) -> List[models.ActiveQuest]:
    return db.query(models.ActiveQuest).filter(models.ActiveQuest.campaign_id == campaign_id).all()

def create_quest(db: Session, quest: schemas.ActiveQuestCreate) -> models.ActiveQuest:
    db_quest = models.ActiveQuest(**quest.dict())
    db.add(db_quest)
    db.commit()
    db.refresh(db_quest)
    return db_quest

def update_quest(
    db: Session, quest_id: int, updates: schemas.ActiveQuestUpdate
) -> Optional[models.ActiveQuest]:
    db_quest = get_quest(db, quest_id)
    if db_quest:
        update_data = updates.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_quest, key, value)

        if "steps" in update_data:
            flag_modified(db_quest, "steps")

        db.commit()
        db.refresh(db_quest)
    return db_quest

# --- StoryFlag ---
def get_flag(db: Session, flag_name: str) -> Optional[models.StoryFlag]:
    return db.query(models.StoryFlag).filter(models.StoryFlag.flag_name == flag_name).first()

def set_flag(db: Session, flag: schemas.StoryFlagBase) -> models.StoryFlag:
    """
    This is an "upsert" (update or insert).
    It updates the flag if it exists, or creates it if it doesn't.
    This is what the AI DM uses to remember things.
    """
    db_flag = get_flag(db, flag.flag_name)
    if db_flag:
        # Update existing flag
        db_flag.value = flag.value
    else:
        # Create new flag
        db_flag = models.StoryFlag(**flag.dict())
        db.add(db_flag)

    db.commit()
    db.refresh(db_flag)
    return db_flag