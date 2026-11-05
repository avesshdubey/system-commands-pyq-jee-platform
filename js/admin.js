// Admin Control Panel & Dashboard Controller
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['SCAuth'], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory(require('./auth'));
    } else {
        root.SCAdmin = factory(root.SCAuth || root.Auth);
        root.Admin = root.SCAdmin;
    }
}(typeof self !== 'undefined' ? self : this, function (Auth) {
    'use strict';

    let questionsData = [];

    const Admin = {
        init: function (questions) {
            questionsData = questions || window.SC_QUESTIONS || [];
            this.bindEvents();
            this.renderOverview();
            this.renderUsersTable();
            this.renderAttemptsTable();
            this.renderQuestionsTable();
            this.renderSyllabusAnalytics();
        },

        bindEvents: function () {
            // Admin Navigation Tabs
            document.querySelectorAll('.admin-nav-tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    document.querySelectorAll('.admin-nav-tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.admin-tab-content').forEach(c => c.style.display = 'none');
                    tab.classList.add('active');
                    const targetId = tab.dataset.tab;
                    const contentElem = document.getElementById(targetId);
                    if (contentElem) contentElem.style.display = 'block';

                    if (targetId === 'adminTabUsers') Admin.renderUsersTable();
                    if (targetId === 'adminTabAttempts') Admin.renderAttemptsTable();
                    if (targetId === 'adminTabQuestions') Admin.renderQuestionsTable();
                    if (targetId === 'adminTabAnalytics') Admin.renderSyllabusAnalytics();
                });
            });

            // User Search & Filter
            const userSearch = document.getElementById('adminUserSearch');
            if (userSearch) {
                userSearch.addEventListener('input', () => Admin.renderUsersTable());
            }
            const roleFilter = document.getElementById('adminUserRoleFilter');
            if (roleFilter) {
                roleFilter.addEventListener('change', () => Admin.renderUsersTable());
            }

            // Question Search & Filter
            const qSearch = document.getElementById('adminQSearch');
            if (qSearch) {
                qSearch.addEventListener('input', () => Admin.renderQuestionsTable());
            }
            const qWeekFilter = document.getElementById('adminQWeekFilter');
            if (qWeekFilter) {
                qWeekFilter.addEventListener('change', () => Admin.renderQuestionsTable());
            }

            // Add User Button & Modal
            const btnOpenAddUser = document.getElementById('btnOpenAddUser');
            const addUserModal = document.getElementById('addUserModal');
            const closeAddUser = document.getElementById('closeAddUserModal');
            const cancelAddUser = document.getElementById('cancelAddUserBtn');
            const formAddUser = document.getElementById('formAddUser');

            if (btnOpenAddUser && addUserModal) {
                btnOpenAddUser.addEventListener('click', () => addUserModal.style.display = 'flex');
            }
            if (closeAddUser && addUserModal) {
                closeAddUser.addEventListener('click', () => addUserModal.style.display = 'none');
            }
            if (cancelAddUser && addUserModal) {
                cancelAddUser.addEventListener('click', () => addUserModal.style.display = 'none');
            }
            if (formAddUser) {
                formAddUser.addEventListener('submit', (e) => {
                    e.preventDefault();
                    const name = document.getElementById('newUserName').value.trim();
                    const email = document.getElementById('newUserEmail').value.trim();
                    const rollNo = document.getElementById('newUserRoll').value.trim();
                    const password = document.getElementById('newUserPassword').value.trim();
                    const role = document.getElementById('newUserRole').value;

                    const res = Auth.addUser({ name, email, rollNo, password, role });
                    if (res.success) {
                        alert(`User ${name} successfully registered.`);
                        formAddUser.reset();
                        addUserModal.style.display = 'none';
                        Admin.renderOverview();
                        Admin.renderUsersTable();
                    } else {
                        alert(res.message || 'Failed to add user.');
                    }
                });
            }

            // Export Data Buttons
            const btnExportJson = document.getElementById('btnExportJson');
            if (btnExportJson) {
                btnExportJson.addEventListener('click', () => Admin.exportDataJson());
            }

            const btnExportCsv = document.getElementById('btnExportCsv');
            if (btnExportCsv) {
                btnExportCsv.addEventListener('click', () => Admin.exportAttemptsCsv());
            }

            // Reset Data Button
            const btnResetData = document.getElementById('btnResetSystemData');
            if (btnResetData) {
                btnResetData.addEventListener('click', () => {
                    if (confirm('WARNING: Reset system database to defaults? All test history will be reset.')) {
                        Auth.clearAttempts();
                        localStorage.removeItem('sc_users_v1');
                        location.reload();
                    }
                });
            }
        },

        renderOverview: function () {
            const users = Auth.getUsers();
            const attempts = Auth.getAttempts();
            const totalQ = questionsData.length;
            const uniquePapers = new Set();
            questionsData.forEach(q => (q.source_papers || []).forEach(p => uniquePapers.add(p)));

            const elTotalQ = document.getElementById('statTotalQuestions') || document.getElementById('kpiTotalQuestions');
            if (elTotalQ) elTotalQ.textContent = totalQ.toLocaleString();

            const elTotalPapers = document.getElementById('statTotalPapers');
            if (elTotalPapers) elTotalPapers.textContent = uniquePapers.size || 34;

            const elTotalUsers = document.getElementById('statTotalUsers') || document.getElementById('kpiTotalUsers');
            if (elTotalUsers) elTotalUsers.textContent = users.length;

            const elTotalAttempts = document.getElementById('statTotalAttempts') || document.getElementById('kpiTotalAttempts');
            if (elTotalAttempts) elTotalAttempts.textContent = attempts.length;

            const elAvgScore = document.getElementById('kpiAvgScore');
            if (elAvgScore) {
                const totalScore = attempts.reduce((acc, a) => acc + (a.score || 0), 0);
                elAvgScore.textContent = attempts.length ? (totalScore / attempts.length).toFixed(1) : '0';
            }

            const elAvgAcc = document.getElementById('kpiAvgAccuracy');
            if (elAvgAcc) {
                const totalAcc = attempts.reduce((acc, a) => acc + (a.accuracy || 0), 0);
                elAvgAcc.textContent = attempts.length ? (totalAcc / attempts.length).toFixed(1) + '%' : '0%';
            }
        },

        renderUsersTable: function () {
            const tbody = document.getElementById('adminUsersTableBody') || document.getElementById('adminUsersTbody');
            if (!tbody) return;

            const searchVal = (document.getElementById('adminUserSearch')?.value || '').toLowerCase();
            const roleVal = document.getElementById('adminUserRoleFilter')?.value || 'ALL';

            let users = Auth.getUsers();
            if (roleVal !== 'ALL' && roleVal !== 'all') {
                users = users.filter(u => u.role.toLowerCase() === roleVal.toLowerCase());
            }
            if (searchVal) {
                users = users.filter(u =>
                    u.name.toLowerCase().includes(searchVal) ||
                    u.email.toLowerCase().includes(searchVal) ||
                    u.rollNo.toLowerCase().includes(searchVal)
                );
            }

            if (users.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No users found matching query.</td></tr>';
                return;
            }

            tbody.innerHTML = users.map(u => {
                const badgeClass = u.role === 'admin' ? 'badge-admin' : 'badge-student';
                return `
                    <tr>
                        <td><strong>${u.rollNo}</strong></td>
                        <td>${u.name}</td>
                        <td>${u.email}</td>
                        <td><span class="user-role-badge ${badgeClass}">${u.role.toUpperCase()}</span></td>
                        <td>${u.testsTaken || 0}</td>
                        <td>${u.bestScore || 0}</td>
                        <td class="action-cell">
                            <button class="btn-action-sm btn-edit" onclick="Admin.promptResetPassword('${u.id}')" title="Reset Password">&#128273;</button>
                            ${u.role !== 'admin' ? `<button class="btn-action-sm btn-delete" onclick="Admin.confirmDeleteUser('${u.id}', '${u.name}')" title="Delete User">&times;</button>` : ''}
                        </td>
                    </tr>
                `;
            }).join('');
        },

        renderAttemptsTable: function () {
            const tbody = document.getElementById('adminAttemptsTableBody') || document.getElementById('adminAttemptsTbody');
            if (!tbody) return;

            const attempts = Auth.getAttempts();
            if (attempts.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">No test submissions recorded yet.</td></tr>';
                return;
            }

            tbody.innerHTML = attempts.map(a => {
                const dateStr = a.timestamp ? new Date(a.timestamp).toLocaleString() : 'N/A';
                const accColor = a.accuracy >= 75 ? '#15803d' : (a.accuracy >= 50 ? '#b45309' : '#dc2626');
                return `
                    <tr>
                        <td><strong>${a.userRoll || 'N/A'}</strong></td>
                        <td>${a.userName || 'Student'}</td>
                        <td>${a.section || 'All Weeks'}</td>
                        <td><strong>${a.score}</strong> / ${a.maxMarks || 0}</td>
                        <td><span style="color: ${accColor}; font-weight: 600;">${a.accuracy}%</span></td>
                        <td>${a.attempted || 0} / ${a.totalQuestions || 0}</td>
                        <td>${a.timeSpent || 'N/A'}</td>
                        <td class="text-muted" style="font-size: 11px;">${dateStr}</td>
                    </tr>
                `;
            }).join('');
        },

        renderQuestionsTable: function () {
            const tbody = document.getElementById('adminQuestionsTableBody') || document.getElementById('adminQuestionsTbody');
            if (!tbody) return;

            const searchVal = (document.getElementById('adminQSearch')?.value || '').toLowerCase();
            const weekVal = document.getElementById('adminQWeekFilter')?.value || 'ALL';

            let filtered = questionsData;
            if (weekVal !== 'ALL' && weekVal !== 'all') {
                filtered = filtered.filter(q => q.week && q.week.startsWith(weekVal));
            }
            if (searchVal) {
                filtered = filtered.filter(q =>
                    q.id.toLowerCase().includes(searchVal) ||
                    (q.question_text || '').toLowerCase().includes(searchVal) ||
                    (q.subtopic || '').toLowerCase().includes(searchVal)
                );
            }

            const countIndicator = document.getElementById('adminQCountIndicator');
            if (countIndicator) {
                countIndicator.textContent = `Showing ${Math.min(filtered.length, 100)} of ${filtered.length} questions`;
            }

            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">No questions found matching criteria.</td></tr>';
                return;
            }

            tbody.innerHTML = filtered.slice(0, 100).map(q => {
                const previewText = (q.question_text || '[Visual Command/Card]').substring(0, 75) + '...';
                const ans = (q.correct_answer || []).join(', ') || 'N/A';
                return `
                    <tr>
                        <td><strong>${q.id}</strong></td>
                        <td><span class="badge-type">${q.question_type || 'MCQ'}</span></td>
                        <td><small style="color: #64748b;">${q.subtopic || q.week}</small><br>${previewText}</td>
                        <td><strong style="color: #15803d;">${ans}</strong></td>
                        <td>+${q.marks || 3}</td>
                        <td>
                            ${q.card_image ? `<button class="btn-action-sm btn-preview" onclick="Admin.previewCard('${q.card_image}', '${q.id}')" title="View Question Card">&#128065;</button>` : '<span class="text-muted">-</span>'}
                        </td>
                    </tr>
                `;
            }).join('');
        },

        renderSyllabusAnalytics: function () {
            const container = document.getElementById('adminSyllabusBreakdown');
            if (!container) return;

            const weekCounts = {};
            const subCounts = {};
            questionsData.forEach(q => {
                const wk = q.week || 'Unknown Week';
                const sub = q.subtopic || 'General';
                weekCounts[wk] = (weekCounts[wk] || 0) + 1;
                subCounts[sub] = (subCounts[sub] || 0) + 1;
            });

            const total = questionsData.length || 1;
            const weekOrder = [
                "Week 1: Introduction to Operating Systems, Shell & Basic Commands",
                "Week 2: File System Hierarchy, Permissions, Redirection & Links",
                "Week 3: Text Processing Filters, Grep/Regex, Sed & Awk",
                "Week 4: Shell Scripting, Environment Variables & Process Management"
            ];

            let html = '<div class="syllabus-grid">';
            weekOrder.forEach((wk, i) => {
                const count = weekCounts[wk] || 0;
                const pct = ((count / total) * 100).toFixed(1);
                
                // Get subtopics for this week
                const subsForWeek = Object.keys(subCounts).filter(s => s.startsWith(`${i+1}.`)).sort();

                html += `
                    <div class="syllabus-week-card">
                        <div class="week-card-header">
                            <div>
                                <h4>${wk}</h4>
                                <span class="text-muted" style="font-size: 11px;">${count} Questions (${pct}%)</span>
                            </div>
                            <span class="week-badge week-${i+1}">Week ${i+1}</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill week-${i+1}-fill" style="width: ${pct}%;"></div>
                        </div>
                        <div class="subtopics-list">
                            ${subsForWeek.map(s => `
                                <div class="subtopic-row">
                                    <span class="subtopic-name">${s}</span>
                                    <span class="subtopic-count">${subCounts[s]} Qs</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        },

        previewCard: function (imgSrc, qId) {
            const modal = document.getElementById('cardPreviewModal');
            const img = document.getElementById('cardPreviewImg');
            const title = document.getElementById('cardPreviewTitle');
            if (modal && img) {
                img.src = imgSrc;
                if (title) title.textContent = `Question Card: ${qId}`;
                modal.style.display = 'flex';
            }
        },

        promptResetPassword: function (userId) {
            const newPass = prompt('Enter new password for user:');
            if (newPass && newPass.trim()) {
                const res = Auth.resetPassword(userId, newPass.trim());
                if (res.success) {
                    alert('Password successfully reset.');
                } else {
                    alert(res.message || 'Error updating password.');
                }
            }
        },

        confirmDeleteUser: function (userId, name) {
            if (confirm(`Are you sure you want to delete user "${name}"?`)) {
                const res = Auth.deleteUser(userId);
                if (res.success) {
                    alert('User deleted.');
                    this.renderOverview();
                    this.renderUsersTable();
                } else {
                    alert(res.message || 'Cannot delete user.');
                }
            }
        },

        exportDataJson: function () {
            const data = {
                questions: questionsData,
                users: Auth.getUsers(),
                attempts: Auth.getAttempts(),
                exportedAt: new Date().toISOString()
            };
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `system_commands_pyq_export_${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
        },

        exportAttemptsCsv: function () {
            const attempts = Auth.getAttempts();
            if (attempts.length === 0) {
                alert('No test attempts to export.');
                return;
            }
            const headers = ['Attempt ID', 'Roll No', 'Name', 'Section', 'Score', 'Max Marks', 'Accuracy (%)', 'Questions Attempted', 'Total Questions', 'Time Spent', 'Timestamp'];
            const rows = attempts.map(a => [
                a.id,
                `"${a.userRoll || ''}"`,
                `"${a.userName || ''}"`,
                `"${a.section || ''}"`,
                a.score,
                a.maxMarks,
                a.accuracy,
                a.attempted,
                a.totalQuestions,
                `"${a.timeSpent || ''}"`,
                `"${a.timestamp || ''}"`
            ]);
            const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `system_commands_test_submissions_${Date.now()}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        }
    };

    return Admin;
}));
