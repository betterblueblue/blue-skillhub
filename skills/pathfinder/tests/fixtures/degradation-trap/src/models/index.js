class User {
  constructor(id, username, email, role) {
    this.id = id;
    this.username = username;
    this.email = email;
    this.role = role;
  }
}

class ApiKey {
  constructor(id, name, key, userId) {
    this.id = id;
    this.name = name;
    this.key = key;
    this.userId = userId;
  }
}

module.exports = { User, ApiKey };
