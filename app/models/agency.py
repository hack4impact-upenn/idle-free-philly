from .. import db


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
    users = db.relationship('User', backref='agency', lazy='select')
    reports = db.relationship('IncidentReport', backref='agency',
                              lazy='joined')

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
            agency = Agency.query.filter_by(name=a).first()
            if agency is None:
                agency = Agency(name=a)
            agency.is_public = agencies[a][0]
            agency.is_official = agencies[a][1]
            db.session.add(agency)
        db.session.commit()

    def __repr__(self):
        return '<Agency \'%s\'>' % self.name
