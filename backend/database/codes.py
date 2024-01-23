from base import CodeBase


class LifeCycleStatus(CodeBase):
    """
    Elinkaaren vaihe
    """

    __tablename__ = "lifecycle_status"
    code_list_uri = "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari"
