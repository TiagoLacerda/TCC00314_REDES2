from database import *

db = Database()
db.insertUser('admin', '1234', True)
db.insertUser('tiago', '1234', False)
db.insertRoom('admin')

admin = db.selectUser('admin')
tiago = db.selectUser('tiago')

print(db.selectAdminByMemberOrAdmin(admin.username))
print(db)