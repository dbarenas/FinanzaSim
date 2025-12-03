document.addEventListener('DOMContentLoaded', () => {
    const QUARTER_DURATION_MS = 5 * 60 * 1000; // 5 minutes

    // --- Logic for index.html ---
    const createSessionBtn = document.getElementById('create-session');
    const companyNameInput = document.getElementById('company-name');

    if (createSessionBtn) {
        createSessionBtn.addEventListener('click', async () => {
            const companyName = companyNameInput.value.trim();
            if (!companyName) return alert('Please enter a company name.');

            try {
                const response = await fetch('/sessions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ company_names: [companyName] }),
                });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const session = await response.json();

                localStorage.setItem('session_id', session.id);
                localStorage.setItem('company_id', Object.keys(session.companies)[0]);
                window.location.href = '/static/dashboard.html';
            } catch (error) {
                console.error('Error creating session:', error);
                alert('Failed to create session.');
            }
        });
    }

    // --- Logic for dashboard.html ---
    if (window.location.pathname.endsWith('dashboard.html')) {
        const sessionId = localStorage.getItem('session_id');
        const companyId = localStorage.getItem('company_id');

        if (!sessionId || !companyId) {
            alert('No session found. Please create or join a session first.');
            return window.location.href = '/';
        }

        const sessionInfo = document.getElementById('session-info');
        const timerDisplay = document.getElementById('timer');
        const chatBox = document.getElementById('chat-box');
        const submitDecisionBtn = document.getElementById('submit-decision');
        const financialsChartCanvas = document.getElementById('financials-chart').getContext('2d');
        let financialsChart;
        let countdownInterval;

        const fetchSessionData = async () => {
            try {
                const response = await fetch(`/sessions/${sessionId}`);
                if (!response.ok) {
                    if(response.status === 404) {
                        alert('Session not found. It might have expired or is invalid.');
                        localStorage.clear();
                        window.location.href = '/';
                    }
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const session = await response.json();
                updateDashboard(session);
                startQuarterTimer(session);
            } catch (error) {
                console.error('Error fetching session data:', error);
            }
        };

        const updateDashboard = (session) => {
            const company = session.companies[companyId];
            if (!company) return alert('Your company was not found in this session.');

            sessionInfo.textContent = `Session: ${session.game_code} | Company: ${company.name} | Status: ${session.game_status}`;

            updateChart(company.financials);
            displayQuestion(company);
        };

        const updateChart = (financials) => {
            const labels = financials.map(f => `Q${f.quarter}`);
            const revenueData = financials.map(f => f.revenue);
            const netIncomeData = financials.map(f => f.net_income);
            const cashData = financials.map(f => f.cash);

            if (financialsChart) financialsChart.destroy();

            financialsChart = new Chart(financialsChartCanvas, {
                type: 'line',
                data: {
                    labels,
                    datasets: [
                        { label: 'Revenue', data: revenueData, borderColor: 'blue', fill: false },
                        { label: 'Net Income', data: netIncomeData, borderColor: 'green', fill: false },
                        { label: 'Cash', data: cashData, borderColor: 'orange', fill: false },
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        };

        const displayQuestion = (company) => {
            chatBox.innerHTML = '';
            if (company.active_question_id) {
                // This requires getting the question bank from the server,
                // or enhancing the session endpoint to include the question details.
                // For now, let's assume we can fetch it. We will add a new endpoint for that.
                fetch(`/questions/${company.active_question_id}`)
                    .then(res => res.json())
                    .then(question => {
                        let questionHTML = `<p><strong>${question.prompt}</strong></p>`;
                        question.options.forEach(opt => {
                            questionHTML += `
                                <div>
                                    <input type="radio" name="question_option" value="${opt.id}" id="opt_${opt.id}">
                                    <label for="opt_${opt.id}">${opt.text}</label>
                                </div>`;
                        });
                        chatBox.innerHTML = questionHTML;

                        document.querySelectorAll('input[name="question_option"]').forEach(radio => {
                            radio.addEventListener('change', handleOptionSelection);
                        });
                    });
            } else {
                chatBox.innerHTML = '<p>Waiting for the next quarter to start...</p>';
            }
        };

        const handleOptionSelection = async (event) => {
            const optionId = event.target.value;
            try {
                await fetch(`/sessions/${sessionId}/answer`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ company_id: companyId, option_id: optionId }),
                });
            } catch(error) {
                console.error('Failed to submit answer:', error);
            }
        };

        const startQuarterTimer = (session) => {
            if (countdownInterval) clearInterval(countdownInterval);
            const endTime = session.last_update_time * 1000 + QUARTER_DURATION_MS;

            countdownInterval = setInterval(() => {
                const remaining = endTime - Date.now();
                if (remaining <= 0) {
                    clearInterval(countdownInterval);
                    timerDisplay.textContent = 'Quarter closing...';
                    closeQuarter();
                } else {
                    const minutes = Math.floor(remaining / 60000);
                    const seconds = Math.floor((remaining % 60000) / 1000);
                    timerDisplay.textContent = `Time left: ${minutes}:${seconds.toString().padStart(2, '0')}`;
                }
            }, 1000);
        };

        const closeQuarter = async () => {
            try {
                const response = await fetch(`/sessions/${sessionId}/close_quarter`, { method: 'POST' });
                if (!response.ok) throw new Error('Failed to close quarter');
                fetchSessionData(); // Refresh data for the new quarter
            } catch (error) {
                console.error('Error closing quarter:', error);
            }
        };

        submitDecisionBtn.addEventListener('click', async () => {
            const production = document.getElementById('production-input').value;
            const price = document.getElementById('price-input').value;
            const marketing = document.getElementById('marketing-input').value;

            if (!production || !price || !marketing) return alert('All decision fields are required.');

            try {
                await fetch(`/sessions/${sessionId}/decisions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        company_id: companyId,
                        production: parseFloat(production),
                        price: parseFloat(price),
                        marketing: parseFloat(marketing),
                    }),
                });
                alert('Decision submitted successfully!');
            } catch (error) {
                console.error('Failed to submit decision:', error);
                alert('Error submitting decision.');
            }
        });

        fetchSessionData();
    }
});
