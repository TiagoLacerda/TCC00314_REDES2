from numpy import add


class User():
    def __init__(self, username: str, password: str, premium: bool):
        self.username = username
        self.password = password
        self.premium = premium

    def __str__(self):
        return '{{username={}, password={}, premium={}}}'.format(self.username, self.password, self.premium)

    def __eq__(self, other):
        return other is not None and other.username == self.username


class Room():
    def __init__(self, admin: User, members: list):
        self.admin = admin
        self.members = members

    def __str__(self):
        return '{admin=' + str(self.admin) + ', members={' + ', '.join(map(str, self.members)) + '}}'

    def __eq__(self, other):
        return other is not None and other.admin == self.admin


# INSERT, SELECT, UPDATE, DELETE

# Room has Users, not UserIDs, so Database must keep consistency
class Database():
    def __init__(self):
        self.users = []
        self.rooms = []

    def __str__(self):
        string = ''
        for user in self.users:
            string += (user.__str__() + '\n')
        for room in self.rooms:
            string += (room.__str__() + '\n')
        return string

    # --------------------------------------------------

    def insertUser(self, username: str, password: str, premium: bool):
        isUnique = True
        for user in self.users:
            if user.username == username:
                isUnique = False

        if isUnique:
            self.users.append(User(username, password, premium))

    def selectUser(self, username: str):
        for user in self.users:
            if user.username == username:
                return user
        return None

    def updateUser(self, username: str, password: str, premium: bool):
        user = self.selectUser(username)
        if user is not None:
            user.password = password
            user.premium = premium

    def deleteUser(self, username: str):
        user = self.selectUser(username)
        if user is not None:
            self.users.remove(user)

            for room in self.rooms:
                # Delete room if user was admin
                if room.admin == user:
                    self.rooms.remove(room)

                # Remove user from room if was member
                if user in room.members:
                    room.members.remove(user)

    # --------------------------------------------------

    def insertRoom(self, username: str):
        user = self.selectUser(username)
        if user is not None and user.premium:
            isAdmin = False
            for room in self.rooms:
                if room.admin == user:
                    isAdmin = True

            if not isAdmin:
                room = Room(user, [])
                self.rooms.append(room)
                return room
        return None

    def selectRoom(self, username: str):
        user = self.selectUser(username)
        if user is not None:
            for room in self.rooms:
                if room.admin == user:
                    return room
        return None

    def updateRoom(self, username: str, members: list):
        user = self.selectUser(username)
        if user is not None:
            room = self.selectRoom(user.username)
            if room is not None:
                for member in members:
                    if member in self.users:
                        if member in room.members:
                            room.members.remove(member)
                        else:
                            room.members.append(member)

    def deleteRoom(self, username: str):
        user = self.selectUser(username)
        if user is not None:
            room = self.selectRoom(user.username)
            if room is not None:
                self.rooms.remove(room)

    def insertMember(self, admin_username, member_username):
        admin = self.selectUser(admin_username)
        if admin:
            member = self.selectUser(member_username)
            if member:
                room = self.selectRoom(admin.username)
                if room:
                    if member not in room.members:
                        room.members.append(member)
                        return member
        return None

    def deleteMember(self, admin_username, member_username):
        admin = self.selectUser(admin_username)
        if admin:
            member = self.selectUser(member_username)
            if member:
                room = self.selectRoom(admin.username)
                if room:
                    if member in room.members:
                        room.members.remove(member)
                        return member
        return None

    # --------------------------------------------------

    def isMember(self, username: str):
        for room in self.rooms:
            usernames = [member.username for member in room.members]
            if username in usernames:
                return True
        return False

    def isAdmin(self, username: str):
        for room in self.rooms:
            if username == room.admin.username:
                return True
        return False

    def isMemberOrAdmin(self, username: str):
        return self.isMember(username) or self.isAdmin(username)

    def selectRoomByMember(self, username: str):
        for room in self.rooms:
            usernames = [member.username for member in room.members]
            if username in usernames:
                return room
        return None

    def selectRoomByMemberOrAdmin(self, username: str):
        for room in self.rooms:
            usernames = [member.username for member in room.members]
            if username == room.admin.username or username in usernames:
                return room
        return None

    def selectAdminByMemberOrAdmin(self, username: str):
        room = self.selectRoomByMemberOrAdmin(username)
        if room:
            return room.admin
        return None
