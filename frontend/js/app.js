// frontend/js/app.js
class PortfolioApp {
    constructor() {
        this.apiBase = '/api';
        this.userId = 'default_user';
        this.pollInterval = null;
        this.syncInProgress = false;
        this.init();
    }

    init() {
        console.log('🚀 Portfolio App initializing...');
        this.setupEventListeners();
        this.loadPortfolio();
        this.startPolling(60000); // Poll every 60 seconds
        this.updateStatus('online', 'System ready');
    }

    setupEventListeners() {
        // Sync button
        const syncBtn = document.getElementById('syncBtn');
        if (syncBtn) {
            syncBtn.addEventListener('click', () => this.triggerSync());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.triggerSync();
            }
        });
    }

    async loadPortfolio() {
        try {
            this.updateStatus('syncing', 'Loading portfolio...');
            const response = await fetch(`${this.apiBase}/portfolio/${this.userId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderPortfolio(data.data);
                this.updateLastSynced(data.data.last_synced);
                this.updateStatus('online', 'Portfolio loaded');
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Error loading portfolio:', error);
            this.updateStatus('offline', 'Failed to load portfolio');
            this.renderEmptyState();
        }
    }

    renderPortfolio(data) {
        // Profile
        this.renderProfile(data.profile);
        
        // Experience
        this.renderExperience(data.experience || []);
        
        // Projects
        this.renderProjects(data.projects || []);
        
        // Skills
        this.renderSkills(data.skills || []);
        
        // Education
        this.renderEducation(data.education || []);
        
        // Certifications
        this.renderCertifications(data.certifications || []);
    }

    renderProfile(profile) {
        const nameEl = document.getElementById('name');
        const headlineEl = document.getElementById('headline');
        const avatarEl = document.getElementById('avatar');
        
        if (nameEl) nameEl.textContent = profile?.name || 'Your Name';
        if (headlineEl) headlineEl.textContent = profile?.headline || 'Software Engineer';
        
        if (avatarEl && profile?.avatar_url) {
            avatarEl.src = profile.avatar_url;
            avatarEl.alt = profile.name || 'Avatar';
        }
    }

    renderExperience(experience) {
        const container = document.getElementById('experienceList');
        if (!container) return;
        
        if (!experience || experience.length === 0) {
            container.innerHTML = `
                <div class="loading-placeholder">No experience data available</div>
            `;
            return;
        }
        
        container.innerHTML = experience.map(exp => `
            <div class="experience-card">
                <h3>${this.escapeHtml(exp.role || 'Role')}</h3>
                <div class="experience-company">${this.escapeHtml(exp.company || 'Company')}</div>
                <div class="experience-duration">${this.escapeHtml(exp.duration || 'Duration')}</div>
                ${exp.bullets && exp.bullets.length > 0 ? `
                    <ul class="experience-bullets">
                        ${exp.bullets.map(b => `<li>${this.escapeHtml(b)}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `).join('');
    }

    renderProjects(projects) {
        const container = document.getElementById('projectList');
        if (!container) return;
        
        if (!projects || projects.length === 0) {
            container.innerHTML = `
                <div class="loading-placeholder">No projects available</div>
            `;
            return;
        }
        
        container.innerHTML = projects.map(project => `
            <div class="project-card">
                <h3>${this.escapeHtml(project.name || 'Project')}</h3>
                <p class="project-description">${this.escapeHtml(project.description || 'No description')}</p>
                <div class="project-meta">
                    <span class="project-stars">⭐ ${project.stars || 0}</span>
                    ${project.url ? `<a href="${project.url}" target="_blank" rel="noopener noreferrer" class="project-link">🔗 View</a>` : ''}
                </div>
                ${project.tech_stack && project.tech_stack.length > 0 ? `
                    <div class="project-tech">
                        ${project.tech_stack.map(tech => `<span class="tech-tag">${this.escapeHtml(tech)}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    renderSkills(skills) {
        const container = document.getElementById('skillsList');
        if (!container) return;
        
        if (!skills || skills.length === 0) {
            container.innerHTML = `
                <div class="loading-placeholder">No skills available</div>
            `;
            return;
        }
        
        container.innerHTML = skills.map(skill => `
            <span class="skill-tag">${this.escapeHtml(skill)}</span>
        `).join('');
    }

    renderEducation(education) {
        const container = document.getElementById('educationList');
        if (!container) return;
        
        if (!education || education.length === 0) {
            container.innerHTML = `
                <div class="loading-placeholder">No education data available</div>
            `;
            return;
        }
        
        container.innerHTML = education.map(edu => `
            <div class="education-card">
                <h4>${this.escapeHtml(edu.institution || 'Institution')}</h4>
                <div class="education-details">${this.escapeHtml(edu.degree || '')}</div>
                ${edu.field_of_study ? `<div class="education-details">${this.escapeHtml(edu.field_of_study)}</div>` : ''}
            </div>
        `).join('');
    }

    renderCertifications(certifications) {
        const container = document.getElementById('certificationList');
        if (!container) return;
        
        if (!certifications || certifications.length === 0) {
            container.innerHTML = `
                <div class="loading-placeholder">No certifications available</div>
            `;
            return;
        }
        
        container.innerHTML = certifications.map(cert => `
            <div class="certification-card">
                <h4>${this.escapeHtml(cert.name || 'Certification')}</h4>
                <div class="certification-details">${this.escapeHtml(cert.issuer || '')}</div>
                ${cert.issue_date ? `<div class="certification-details">Issued: ${this.escapeHtml(cert.issue_date)}</div>` : ''}
            </div>
        `).join('');
    }

    renderEmptyState() {
        const sections = ['experienceList', 'projectList', 'skillsList', 'educationList', 'certificationList'];
        sections.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.innerHTML = `
                    <div class="loading-placeholder">No data available. Click "Sync Now" to load your portfolio.</div>
                `;
            }
        });
    }

    async triggerSync() {
        if (this.syncInProgress) {
            console.log('Sync already in progress...');
            return;
        }
        
        this.syncInProgress = true;
        const syncBtn = document.getElementById('syncBtn');
        if (syncBtn) {
            syncBtn.disabled = true;
            syncBtn.innerHTML = '<span class="sync-icon">⏳</span> Syncing...';
        }
        
        this.updateStatus('syncing', 'Syncing portfolio...');
        
        try {
            const response = await fetch(`${this.apiBase}/sync`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: this.userId })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'pending') {
                this.updateStatus('syncing', data.message);
                console.log('✅ Sync triggered successfully. Waiting for completion.');
            } else {
                throw new Error(data.error || 'Failed to start sync process.');
            }
        } catch (error) {
            console.error('❌ Sync error:', error);
            this.updateStatus('offline', 'Sync failed: ' + error.message);
        } finally {
            this.syncInProgress = false;
            if (syncBtn) {
                syncBtn.disabled = false;
                syncBtn.innerHTML = '<span class="sync-icon">🔄</span> Sync Now';
            }
        }
    }

    updateLastSynced(timestamp) {
        const el = document.getElementById('lastSynced');
        if (!el) return;
        
        if (timestamp) {
            const date = new Date(timestamp);
            el.textContent = `Last synced: ${date.toLocaleString()}`;
        } else {
            el.textContent = 'Last synced: Never';
        }
    }

    updateStatus(state, message) {
        const dot = document.getElementById('statusDot');
        const text = document.getElementById('statusText');
        
        if (dot) {
            dot.className = 'status-dot';
            if (state === 'online') dot.classList.add('online');
            else if (state === 'offline') dot.classList.add('offline');
            else if (state === 'syncing') dot.classList.add('syncing');
        }
        
        if (text) {
            text.textContent = message || 'System ready';
        }
    }

    startPolling(interval) {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
        
        this.pollInterval = setInterval(() => {
            this.loadPortfolio();
        }, interval);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PortfolioApp();
});

// Handle service worker and offline support
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => {
            console.log('Service Worker registered successfully');
        })
        .catch(error => {
            console.log('Service Worker registration failed:', error);
        });
}