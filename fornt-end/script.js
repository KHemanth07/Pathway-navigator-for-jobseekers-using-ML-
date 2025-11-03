document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const domainScreen = document.getElementById('domain-screen');
    const inputScreen = document.getElementById('input-screen');
    const resultsScreen = document.getElementById('results-screen');
    const loadingScreen = document.getElementById('loading-screen');
    const itDomainBtn = document.getElementById('it-domain');
    const nonitDomainBtn = document.getElementById('nonit-domain');
    const pathwayForm = document.getElementById('pathway-form');
    const backBtn = document.getElementById('back-btn');
    const newSearchBtn = document.getElementById('new-search-btn');
    const branchField = document.getElementById('branch-field');
    const resultsContainer = document.getElementById('pathway-results');
    const fetchRecruitmentBtn = document.getElementById('fetch-recruitment');
    const recruitmentProcessDiv = document.getElementById('recruitment-process');
    
    let currentDomain = '';
    
    // Event Listeners
    itDomainBtn.addEventListener('click', () => selectDomain('IT'));
    nonitDomainBtn.addEventListener('click', () => selectDomain('Non-IT'));
    pathwayForm.addEventListener('submit', handleFormSubmit);
    backBtn.addEventListener('click', goBack);
    newSearchBtn.addEventListener('click', startNewSearch);
    fetchRecruitmentBtn.addEventListener('click', fetchRecruitmentProcess);
    
    // Functions
    function selectDomain(domain) {
        currentDomain = domain;
        domainScreen.classList.remove('active');
        inputScreen.classList.add('active');
        backBtn.classList.remove('hidden');
        
        // Show branch field only for Non-IT
        if (domain === 'Non-IT') {
            branchField.classList.remove('hidden');
        } else {
            branchField.classList.add('hidden');
        }
        
        document.getElementById('form-title').textContent = `Provide Your ${domain} Career Details`;
    }
    
    function goBack() {
        inputScreen.classList.remove('active');
        resultsScreen.classList.remove('active');
        domainScreen.classList.add('active');
        backBtn.classList.add('hidden');
    }
    
    function startNewSearch() {
        resultsScreen.classList.remove('active');
        domainScreen.classList.add('active');
        pathwayForm.reset();
    }
    
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = {
            job_role: document.getElementById('job_role').value,
            skill: document.getElementById('skills').value,
            current_year: document.getElementById('academic_year').value,
            year: document.getElementById('academic_year').value
        };
        
        if (currentDomain === 'Non-IT') {
            formData.branch = document.getElementById('branch').value;
        }
        
        showLoading();
        
        try {
            let response;
            if (currentDomain === 'IT') {
                // First get recommendations
                response = await fetch('/recommend_it', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        job_role: formData.job_role,
                        skill: formData.skill
                    })
                });
                
                const recommendations = await response.json();
                
                // Then get learning path
                const learningPathResponse = await fetch('/learning_path', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        job_role: formData.job_role,
                        current_year: parseInt(formData.current_year)
                    })
                });
                
                const learningPath = await learningPathResponse.json();
                
                displayResults({
                    ...recommendations,
                    ...learningPath,
                    domain: currentDomain,
                    formData
                });
                
            } else {
                // Non-IT path
                response = await fetch('/recommend_nonit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const results = await response.json();
                displayResults({
                    ...results,
                    domain: currentDomain,
                    formData
                });
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        } finally {
            hideLoading();
        }
    }
    
    function showLoading() {
        inputScreen.classList.remove('active');
        loadingScreen.classList.add('active');
    }
    
    function hideLoading() {
        loadingScreen.classList.remove('active');
        resultsScreen.classList.add('active');
    }
    
    function displayResults(data) {
        resultsContainer.innerHTML = '';
        
        // Create domain-specific results
        if (data.domain === 'IT') {
            // IT Results
            const itResultsHTML = `
                <div class="recommendations">
                    <h3>Immediate Recommendations</h3>
                    
                    <div class="recommendation-card">
                        <h4>Certifications</h4>
                        <ul>
                            ${data.Certifications && data.Certifications.length > 0 ? 
                                data.Certifications.map(cert => `<li>${cert}</li>`).join('') : 
                                '<li>No certifications recommended</li>'}
                        </ul>
                    </div>
                    
                    <div class="recommendation-card">
                        <h4>Internships</h4>
                        <ul>
                            ${data.Internships && data.Internships.length > 0 ? 
                                data.Internships.map(intern => `<li>${intern}</li>`).join('') : 
                                '<li>No internships recommended</li>'}
                        </ul>
                    </div>
                    
                    <div class="recommendation-card">
                        <h4>Projects</h4>
                        <ul>
                            ${data.Projects && data.Projects.length > 0 ? 
                                data.Projects.map(project => `<li>${project}</li>`).join('') : 
                                '<li>No projects recommended</li>'}
                        </ul>
                    </div>
                </div>
                
                <div class="learning-path">
                    <h3>Learning Pathway</h3>
                    ${Object.entries(data).filter(([key]) => key.startsWith('Year ')).map(([year, skills]) => `
                        <div class="skill-year">
                            <h4>${year}</h4>
                            <ul>
                                ${skills.map(skill => `<li>${skill}</li>`).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
            `;
            
            resultsContainer.innerHTML = itResultsHTML;
            
        } else {
            // Non-IT Results
            const nonItResultsHTML = `
                <div class="recommendations">
                    <h3>Your Recommendations</h3>
                    
                    <div class="recommendation-card">
                        <h4>Certifications</h4>
                        <p>${data.certifications || 'No certifications recommended'}</p>
                    </div>
                    
                    <div class="recommendation-card">
                        <h4>Internships</h4>
                        <p>${data.internships || 'No internships recommended'}</p>
                    </div>
                    
                    <div class="recommendation-card">
                        <h4>Projects</h4>
                        <p>${data.projects || 'No projects recommended'}</p>
                    </div>
                </div>
                
                <div class="learning-path">
                    <h3>Skill Development Plan</h3>
                    ${Object.entries(data.skill_division).map(([year, skills]) => `
                        <div class="skill-year">
                            <h4>${year}</h4>
                            <ul>
                                ${skills.map(skill => `<li>${skill}</li>`).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
            `;
            
            resultsContainer.innerHTML = nonItResultsHTML;
        }
    }
    
    async function fetchRecruitmentProcess() {
        const companyName = document.getElementById('company-name').value;
        const jobRole = document.getElementById('job_role').value;
        
        if (!companyName || !jobRole) {
            alert('Please enter a company name and make sure you have a job role selected');
            return;
        }
        
        recruitmentProcessDiv.innerHTML = '<p>Loading...</p>';
        
        try {
            const response = await fetch('/get_recruitment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    company_name: companyName,
                    job_role: jobRole
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                recruitmentProcessDiv.innerHTML = `<p class="error">${data.error}</p>`;
            } else {
                // Format the process steps (assuming they come as paragraphs)
                const steps = data.recruitment_process.split('\n\n')
                    .filter(step => step.trim() !== '')
                    .map(step => `<div class="process-step">${step.replace(/\n/g, '<br>')}</div>`)
                    .join('');
                
                recruitmentProcessDiv.innerHTML = steps || '<p>No recruitment process information found.</p>';
            }
        } catch (error) {
            console.error('Error:', error);
            recruitmentProcessDiv.innerHTML = '<p class="error">Failed to fetch recruitment process</p>';
        }
    }
});