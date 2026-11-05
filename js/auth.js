// Authentication, Role-Based Access Control & User Management System
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        const authInstance = factory();
        root.SCAuth = authInstance;
        root.Auth = authInstance;
        root.MLTAuth = authInstance;
        root.MLFAuth = authInstance;
    }
}(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    const USERS_KEY = 'sc_users_v1';
    const SESSION_KEY = 'sc_current_user_v1';
    const ATTEMPTS_KEY = 'sc_test_attempts_v1';

    // Seed default administrative and demo student accounts
    function seedDefaultUsers() {
        const existing = localStorage.getItem(USERS_KEY);
        if (!existing) {
            const defaults = [
                {
                    id: 'usr_admin_01',
                    name: 'Faculty Administrator',
                    email: 'admin@iitm.ac.in',
                    rollNo: 'ADMIN-001',
                    password: 'Admin@123',
                    role: 'admin',
                    status: 'active',
                    createdAt: '2026-11-01T10:00:00Z',
                    testsTaken: 0,
                    bestScore: 0
                },
                {
                    id: 'usr_student_01',
                    name: 'Avesh Dubey',
                    email: 'student@iitm.ac.in',
                    rollNo: '24DS109284',
                    password: 'Student@123',
                    role: 'student',
                    status: 'active',
                    createdAt: '2026-11-02T12:30:00Z',
                    testsTaken: 3,
                    bestScore: 54
                },
                {
                    id: 'usr_student_02',
                    name: 'Priya Sharma',
                    email: 'priya.s@iitm.ac.in',
                    rollNo: '24DS105412',
                    password: 'Student@123',
                    role: 'student',
                    status: 'active',
                    createdAt: '2026-11-03T14:15:00Z',
                    testsTaken: 2,
                    bestScore: 48
                },
                {
                    id: 'usr_student_03',
                    name: 'Rahul Verma',
                    email: 'rahul.v@iitm.ac.in',
                    rollNo: '24DS107823',
                    password: 'Student@123',
                    role: 'student',
                    status: 'active',
                    createdAt: '2026-11-04T09:45:00Z',
                    testsTaken: 1,
                    bestScore: 36
                }
            ];
            localStorage.setItem(USERS_KEY, JSON.stringify(defaults));
        }

        const existingAttempts = localStorage.getItem(ATTEMPTS_KEY);
        if (!existingAttempts) {
            const sampleAttempts = [
                {
                    id: 'att_001',
                    userId: 'usr_student_01',
                    userName: 'Avesh Dubey',
                    userRoll: '24DS109284',
                    timestamp: '2026-11-04T16:20:00Z',
                    section: 'All Weeks',
                    totalQuestions: 189,
                    attempted: 30,
                    correct: 25,
                    score: 75,
                    maxMarks: 567,
                    accuracy: 83.3,
                    timeSpent: '45 mins'
                },
                {
                    id: 'att_002',
                    userId: 'usr_student_02',
                    userName: 'Priya Sharma',
                    userRoll: '24DS105412',
                    timestamp: '2026-11-05T09:10:00Z',
                    section: 'Week 2: File System Hierarchy, Permissions, Redirection & Links',
                    totalQuestions: 21,
                    attempted: 20,
                    correct: 16,
                    score: 48,
                    maxMarks: 63,
                    accuracy: 80.0,
                    timeSpent: '30 mins'
                }
            ];
            localStorage.setItem(ATTEMPTS_KEY, JSON.stringify(sampleAttempts));
        }
    }

    function getUsersList() {
        try {
            seedDefaultUsers();
            return JSON.parse(localStorage.getItem(USERS_KEY)) || [];
        } catch (e) {
            return [];
        }
    }

    function setUsersList(users) {
        localStorage.setItem(USERS_KEY, JSON.stringify(users));
    }

    function getAttemptsList() {
        try {
            return JSON.parse(localStorage.getItem(ATTEMPTS_KEY)) || [];
        } catch (e) {
            return [];
        }
    }

    function setAttemptsList(attempts) {
        localStorage.setItem(ATTEMPTS_KEY, JSON.stringify(attempts));
    }

    // Initialize on load
    seedDefaultUsers();

    const Auth = {
        init: function () {
            seedDefaultUsers();
        },

        getUsers: function () {
            return getUsersList();
        },

        getAllUsers: function () {
            return getUsersList().map(u => {
                const safe = Object.assign({}, u);
                delete safe.password;
                return safe;
            });
        },

        getCurrentUser: function () {
            try {
                const sessionStr = sessionStorage.getItem(SESSION_KEY) || localStorage.getItem(SESSION_KEY);
                return sessionStr ? JSON.parse(sessionStr) : null;
            } catch (e) {
                return null;
            }
        },

        // Supports Email OR Roll Number, case-insensitive
        login: function (identifier, password, rememberMe) {
            seedDefaultUsers();
            const users = getUsersList();
            const cleanId = (identifier || '').trim().toLowerCase();
            const cleanPass = (password || '').trim();

            const user = users.find(u => 
                (u.email.toLowerCase() === cleanId || (u.rollNo && u.rollNo.toLowerCase() === cleanId)) &&
                u.password === cleanPass
            );

            if (!user) {
                return { success: false, error: 'Invalid Email/Roll Number or Password.', message: 'Invalid Email/Roll Number or Password.' };
            }

            if (user.status === 'suspended') {
                return { success: false, error: 'This user account has been suspended by the administrator.', message: 'This user account has been suspended.' };
            }

            const safeUser = Object.assign({}, user);
            delete safeUser.password;

            const sessionData = JSON.stringify(safeUser);
            sessionStorage.setItem(SESSION_KEY, sessionData);
            if (rememberMe) {
                localStorage.setItem(SESSION_KEY, sessionData);
            }

            return { success: true, user: safeUser };
        },

        // Universal sign-up supporting both object and positional arguments
        signUp: function (nameOrData, email, rollNo, password, role) {
            seedDefaultUsers();
            const users = getUsersList();

            let name, mail, roll, pass, rle;
            if (typeof nameOrData === 'object' && nameOrData !== null) {
                name = nameOrData.name;
                mail = nameOrData.email;
                roll = nameOrData.rollNo;
                pass = nameOrData.password;
                rle = nameOrData.role;
            } else {
                name = nameOrData;
                mail = email;
                roll = rollNo;
                pass = password;
                rle = role;
            }

            const cleanName = (name || '').trim();
            const cleanEmail = (mail || '').trim().toLowerCase();
            const cleanRoll = (roll || '').trim().toUpperCase() || ('24DS' + Math.floor(100000 + Math.random() * 900000));
            const cleanPass = (pass || '').trim();

            if (!cleanName || cleanName.length < 2) {
                return { success: false, error: 'Please enter a valid full name.', message: 'Please enter a valid full name.' };
            }
            if (!cleanEmail || !cleanEmail.includes('@')) {
                return { success: false, error: 'Please enter a valid email address.', message: 'Please enter a valid email address.' };
            }
            if (!cleanPass || cleanPass.length < 6) {
                return { success: false, error: 'Password must be at least 6 characters long.', message: 'Password must be at least 6 characters long.' };
            }

            // Check duplicates
            const exists = users.some(u => 
                u.email.toLowerCase() === cleanEmail || (u.rollNo && u.rollNo.toUpperCase() === cleanRoll)
            );
            if (exists) {
                return { success: false, error: 'An account with this Email or Roll Number already exists.', message: 'An account with this Email or Roll Number already exists.' };
            }

            const newUser = {
                id: 'usr_' + Date.now().toString(36),
                name: cleanName,
                email: cleanEmail,
                rollNo: cleanRoll,
                password: cleanPass,
                role: rle === 'admin' ? 'admin' : 'student',
                status: 'active',
                createdAt: new Date().toISOString(),
                testsTaken: 0,
                bestScore: 0
            };

            users.push(newUser);
            setUsersList(users);

            const safeUser = Object.assign({}, newUser);
            delete safeUser.password;
            sessionStorage.setItem(SESSION_KEY, JSON.stringify(safeUser));
            localStorage.setItem(SESSION_KEY, JSON.stringify(safeUser));

            return { success: true, user: safeUser };
        },

        // Alias for signup
        signup: function (a, b, c, d, e) {
            return this.signUp(a, b, c, d, e);
        },

        logout: function () {
            sessionStorage.removeItem(SESSION_KEY);
            localStorage.removeItem(SESSION_KEY);
            return true;
        },

        addUser: function (userData) {
            return this.signUp(userData);
        },

        addUserByAdmin: function (userData) {
            return this.signUp(
                userData.name,
                userData.email,
                userData.rollNo,
                userData.password || 'Student@123',
                userData.role || 'student'
            );
        },

        deleteUser: function (userId) {
            let users = getUsersList();
            const currentUser = this.getCurrentUser();
            if (currentUser && currentUser.id === userId) {
                return { success: false, error: 'Cannot delete active session user.', message: 'Cannot delete active session user.' };
            }
            users = users.filter(u => u.id !== userId);
            setUsersList(users);
            return { success: true };
        },

        resetPassword: function (userId, newPassword) {
            const users = getUsersList();
            const u = users.find(x => x.id === userId);
            if (u) {
                u.password = newPassword.trim();
                setUsersList(users);
                return { success: true };
            }
            return { success: false, error: 'User not found.', message: 'User not found.' };
        },

        toggleUserStatus: function (userId) {
            const users = getUsersList();
            const u = users.find(x => x.id === userId);
            if (u) {
                u.status = u.status === 'suspended' ? 'active' : 'suspended';
                setUsersList(users);
                return { success: true, status: u.status };
            }
            return { success: false, error: 'User not found.' };
        },

        getAttempts: function () {
            return getAttemptsList();
        },

        saveAttempt: function (attempt) {
            const attempts = getAttemptsList();
            const newAttempt = Object.assign({
                id: 'att_' + Date.now().toString(36),
                timestamp: new Date().toISOString()
            }, attempt);
            attempts.unshift(newAttempt);
            setAttemptsList(attempts);

            // Update user stats
            const users = getUsersList();
            const u = users.find(x => x.id === attempt.userId);
            if (u) {
                u.testsTaken = (u.testsTaken || 0) + 1;
                if ((attempt.score || 0) > (u.bestScore || 0)) {
                    u.bestScore = attempt.score;
                }
                setUsersList(users);
            }
            return newAttempt;
        },

        recordTestAttempt: function (attempt) {
            return this.saveAttempt(attempt);
        },

        clearAttempts: function () {
            setAttemptsList([]);
            return true;
        },

        resetAllData: function () {
            localStorage.removeItem(USERS_KEY);
            localStorage.removeItem(SESSION_KEY);
            sessionStorage.removeItem(SESSION_KEY);
            localStorage.removeItem(ATTEMPTS_KEY);
            seedDefaultUsers();
            return true;
        }
    };

    return Auth;
}));
