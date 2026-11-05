// Authentication, Role-Based Access Control & User Management System
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.SCAuth = factory();
        root.Auth = root.SCAuth;
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
                    totalQuestions: 220,
                    attempted: 30,
                    correct: 25,
                    score: 75,
                    maxMarks: 660,
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
                    totalQuestions: 65,
                    attempted: 20,
                    correct: 16,
                    score: 48,
                    maxMarks: 195,
                    accuracy: 80.0,
                    timeSpent: '30 mins'
                }
            ];
            localStorage.setItem(ATTEMPTS_KEY, JSON.stringify(sampleAttempts));
        }
    }

    // Initialize on load
    seedDefaultUsers();

    return {
        getUsers: function () {
            try {
                return JSON.parse(localStorage.getItem(USERS_KEY)) || [];
            } catch (e) {
                return [];
            }
        },

        getCurrentUser: function () {
            try {
                const s = localStorage.getItem(SESSION_KEY);
                return s ? JSON.parse(s) : null;
            } catch (e) {
                return null;
            }
        },

        login: function (email, password) {
            const users = this.getUsers();
            const cleanEmail = (email || '').trim().toLowerCase();
            const user = users.find(u => u.email.toLowerCase() === cleanEmail && u.password === password);
            if (user) {
                if (user.status === 'suspended') {
                    return { success: false, message: 'Account is suspended. Please contact administrator.' };
                }
                const sessionUser = {
                    id: user.id,
                    name: user.name,
                    email: user.email,
                    rollNo: user.rollNo,
                    role: user.role
                };
                localStorage.setItem(SESSION_KEY, JSON.stringify(sessionUser));
                return { success: true, user: sessionUser };
            }
            return { success: false, message: 'Invalid email address or password.' };
        },

        signup: function (userData) {
            const users = this.getUsers();
            const cleanEmail = (userData.email || '').trim().toLowerCase();
            if (users.some(u => u.email.toLowerCase() === cleanEmail)) {
                return { success: false, message: 'An account with this email already exists.' };
            }

            const newUser = {
                id: 'usr_' + Date.now().toString(36),
                name: userData.name.trim(),
                email: cleanEmail,
                rollNo: (userData.rollNo || '24DS' + Math.floor(100000 + Math.random() * 900000)).trim().toUpperCase(),
                password: userData.password,
                role: userData.role || 'student',
                status: 'active',
                createdAt: new Date().toISOString(),
                testsTaken: 0,
                bestScore: 0
            };

            users.push(newUser);
            localStorage.setItem(USERS_KEY, JSON.stringify(users));

            const sessionUser = {
                id: newUser.id,
                name: newUser.name,
                email: newUser.email,
                rollNo: newUser.rollNo,
                role: newUser.role
            };
            localStorage.setItem(SESSION_KEY, JSON.stringify(sessionUser));
            return { success: true, user: sessionUser };
        },

        logout: function () {
            localStorage.removeItem(SESSION_KEY);
        },

        addUser: function (userData) {
            const users = this.getUsers();
            const cleanEmail = (userData.email || '').trim().toLowerCase();
            if (users.some(u => u.email.toLowerCase() === cleanEmail)) {
                return { success: false, message: 'Email already exists.' };
            }
            const newUser = {
                id: 'usr_' + Date.now().toString(36),
                name: userData.name.trim(),
                email: cleanEmail,
                rollNo: (userData.rollNo || '24DS' + Math.floor(100000 + Math.random() * 900000)).trim().toUpperCase(),
                password: userData.password || 'Student@123',
                role: userData.role || 'student',
                status: userData.status || 'active',
                createdAt: new Date().toISOString(),
                testsTaken: 0,
                bestScore: 0
            };
            users.push(newUser);
            localStorage.setItem(USERS_KEY, JSON.stringify(users));
            return { success: true, user: newUser };
        },

        deleteUser: function (userId) {
            let users = this.getUsers();
            const currentUser = this.getCurrentUser();
            if (currentUser && currentUser.id === userId) {
                return { success: false, message: 'You cannot delete the active session user.' };
            }
            users = users.filter(u => u.id !== userId);
            localStorage.setItem(USERS_KEY, JSON.stringify(users));
            return { success: true };
        },

        resetPassword: function (userId, newPassword) {
            const users = this.getUsers();
            const u = users.find(x => x.id === userId);
            if (u) {
                u.password = newPassword;
                localStorage.setItem(USERS_KEY, JSON.stringify(users));
                return { success: true };
            }
            return { success: false, message: 'User not found.' };
        },

        getAttempts: function () {
            try {
                return JSON.parse(localStorage.getItem(ATTEMPTS_KEY)) || [];
            } catch (e) {
                return [];
            }
        },

        saveAttempt: function (attempt) {
            const attempts = this.getAttempts();
            const newAttempt = Object.assign({
                id: 'att_' + Date.now().toString(36),
                timestamp: new Date().toISOString()
            }, attempt);
            attempts.unshift(newAttempt);
            localStorage.setItem(ATTEMPTS_KEY, JSON.stringify(attempts));

            // Update user stats
            const users = this.getUsers();
            const u = users.find(x => x.id === attempt.userId);
            if (u) {
                u.testsTaken = (u.testsTaken || 0) + 1;
                if ((attempt.score || 0) > (u.bestScore || 0)) {
                    u.bestScore = attempt.score;
                }
                localStorage.setItem(USERS_KEY, JSON.stringify(users));
            }
            return newAttempt;
        },

        clearAttempts: function () {
            localStorage.setItem(ATTEMPTS_KEY, JSON.stringify([]));
        }
    };
}));
