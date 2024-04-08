from datetime import datetime

import models

# import codes
from sqlalchemy.orm import Session


def test_modified_at(session: Session, plan_instance: models.Plan):
    old_modified_at = plan_instance.modified_at
    plan_instance.approved_at = datetime.now()
    session.flush()
    session.refresh(plan_instance)
    assert plan_instance.modified_at != old_modified_at


# def test_update_lifecycle_status(session: Session, plan_instance: models.Plan, lifecycle_date_instance: models.LifeCycleDate, code_instance: codes.LifeCycleStatus, another_code_instance: codes.LifeCycleStatus):
#     session.flush()
#     lifecycle_date_instance.lifecycle_status_id = code_instance.id
#     plan_instance.lifecycle_status_id = code_instance.id
#     old_starting_at = datetime.now()
#     lifecycle_date_instance.starting_at = old_starting_at

#     # Update lifecycle status
#     plan_instance.lifecycle_status_id = another_code_instance.id
#     assert lifecycle_date_instance.starting_at != old_starting_at
