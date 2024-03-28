from datetime import datetime

import models
from sqlalchemy.orm import Session


def test_modified_at(session: Session, plan_instance: models.Plan):
    old_modified_at = plan_instance.modified_at
    plan_instance.approved_at = datetime.now()
    session.flush()
    session.refresh(plan_instance)
    assert plan_instance.modified_at != old_modified_at


# def test_update_lifecycle_status(session: Session, plan_instance: models.Plan):
#     old_valid_from = plan_instance.valid_from
#     plan_instance.lifecycle_status = "Valid"
#     session.flush()
#     session.refresh(plan_instance)
#     assert plan_instance.valid_from != old_valid_from
