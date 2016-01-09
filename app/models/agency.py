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

    # If this agency is set as public, then all new incident reports created
    # for this agency will show this agency's name to the general public by
    # default. That is, the marker on the map will name this particular agency
    # as the type of vehicle which was idling. If an agency is not set as
    # public, then all new incident reports created for that agency will not
    # show this agency by default.
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
