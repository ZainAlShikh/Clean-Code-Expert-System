// A perfectly clean JS file following best practices

const MAXIMUM_LOGIN_ATTEMPTS = 3;
const LOCKOUT_DURATION_MS = 15 * 60 * 1000;

class AuthenticationService {
    constructor(database, emailService) {
        this.database = database;
        this.emailService = emailService;
    }

    async authenticateUser(credentials) {
        const user = await this.database.findUser(credentials.username);
        
        if (!user) {
            return this.handleFailedAttempt(null);
        }

        if (this.isAccountLocked(user)) {
            throw new Error("Account is temporarily locked.");
        }

        const isPasswordValid = await this.verifyPassword(credentials.password, user.passwordHash);
        
        if (!isPasswordValid) {
            return this.handleFailedAttempt(user);
        }

        return this.handleSuccessfulLogin(user);
    }

    isAccountLocked(user) {
        if (!user.lastFailedAttempt) {
            return false;
        }
        
        const timeSinceLastFailure = Date.now() - user.lastFailedAttempt;
        const isLocked = user.failedAttempts >= MAXIMUM_LOGIN_ATTEMPTS && timeSinceLastFailure < LOCKOUT_DURATION_MS;
        
        return isLocked;
    }

    async verifyPassword(plainPassword, hashedPassword) {
        // Simulated hash check
        return plainPassword + "_hashed" === hashedPassword;
    }

    async handleFailedAttempt(user) {
        if (user) {
            user.failedAttempts += 1;
            user.lastFailedAttempt = Date.now();
            await this.database.saveUser(user);
            
            if (user.failedAttempts >= MAXIMUM_LOGIN_ATTEMPTS) {
                await this.emailService.sendLockoutAlert(user.email);
            }
        }
        return false;
    }

    async handleSuccessfulLogin(user) {
        user.failedAttempts = 0;
        user.lastFailedAttempt = null;
        await this.database.saveUser(user);
        return true;
    }
}

module.exports = AuthenticationService;
