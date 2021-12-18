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
                self.rooms.append(Room(user, []))

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
