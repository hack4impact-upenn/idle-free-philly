from .. import db


# Configure many-to-many relationship
agency_user_table = db.Table(
    'association',
    db.Column('agencies_id', db.Integer, db.ForeignKey('agencies.id')),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
)


class Agency(db.Model):
    __tablename__ = 'agencies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)

    # True if this agency was officially created by an Administrator. Official
    # agencies can have relationships to AgencyWorkers and will show up in the
    # reporting form. Non-official agencies will not show up in the form.
    is_official = db.Column(db.Boolean, default=False)

    # True if this agency will be publicly shown with reports. That is, when a
    # public user sees a report on the map, the report's agency will only be
    # shown if is_public is True.
    is_public = db.Column(db.Boolean, default=False)

    # Many users to many agencies. We use the above agency_user_table to
    # configure this relationship.
    users = db.relationship('User', secondary=agency_user_table,
                            backref='agencies', lazy='select')
    incident_reports = db.relationship('IncidentReport', backref='agency',
                                       lazy='joined')

    def __init__(self, **kwargs):
        super(Agency, self).__init__(**kwargs)
        if self.name is not None:
            self.name = self.name.upper()

    @staticmethod
    def get_agency_by_name(name):
        return Agency.query.filter_by(name=name.upper()).first()

    @staticmethod
    def insert_agencies():
        agencies = {
            'SEPTA': (
                False, True
            ),
            'SEPTA BUS': (
                False, True
            ),
            'SEPTA CCT': (
                False, True
            ),
            'PWD': (
                False, True
            ),
            'PECO': (
                False, True
            ),
            'STREETS': (
                False, True
            ),
        }
        for a in agencies:
            agency = Agency.get_agency_by_name(a)
            if agency is None:
                agency = Agency(name=a)
            agency.is_public = agencies[a][0]
            agency.is_official = agencies[a][1]
            db.session.add(agency)
        db.session.commit()

    def __repr__(self):
        return '<Agency \'%s\'>' % self.name
