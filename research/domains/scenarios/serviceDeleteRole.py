class serviceDeleteRole:
    def __init__(self, roles):
        self.roles = roles

    def delete(self, roleId):
        self.roles.delete(roleId)
