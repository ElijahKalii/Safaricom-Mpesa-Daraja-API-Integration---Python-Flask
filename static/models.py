from application import db


"""
    Set up the MYSQL table model (using the sqlalchemy ORM) for setting up the table where we shall record our customer payments 
"""

#Define a master table for stock keeping
class client_payments_table(db.Model):
    transLoID = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    TransactionType = db.Column(db.String(10), nullable=False)
    TransID = db.Column(db.String(10), nullable=False)
    TransTime = db.Column(db.String(14), nullable=False)
    TransAmount = db.Column(db.String(10), nullable=False)
    BusinessShortCode = db.Column(db.String(7), nullable=False)
    BillRefNumber = db.Column(db.String(10), nullable=False)
    InvoiceNumber = db.Column(db.String(10), nullable=False)
    OrgAccountBalance = db.Column(db.String(10), nullable=False)
    ThirdPartyTransID = db.Column(db.String(10), nullable=True)
    MSISDN = db.Column(db.String(12), nullable=False)
    FirstName = db.Column(db.String(20), nullable=False)
    MiddleName = db.Column(db.String(20), nullable=True)
    LastName = db.Column(db.String(20), nullable=False, nullable=False)