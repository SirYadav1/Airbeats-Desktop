// Airbeats Auth Configuration
window.isGuestMode = false;
let authMode = "LOGIN";

document.addEventListener("DOMContentLoaded", () => {
    const overlay = document.getElementById('auth-overlay');
    const btnGuest = document.getElementById('btn-guest-login');
    const btnEmail = document.getElementById('btn-email-login');
    const btnToggle = document.getElementById('btn-toggle-mode');
    
    const inputName = document.getElementById('auth-name');
    const inputEmail = document.getElementById('auth-email');
    const inputPassword = document.getElementById('auth-password');
    const errorDiv = document.getElementById('auth-error');

    const authState = localStorage.getItem('auth_state');
    if (authState === 'guest') {
        window.isGuestMode = true;
        overlay.style.display = 'none';
    } else if (authState === 'logged_in') {
        window.isGuestMode = false;
        overlay.style.display = 'none';
    } else {
        overlay.style.display = 'flex';
    }

    btnToggle.addEventListener('click', (e) => {
        e.preventDefault();
        errorDiv.style.display = 'none';
        if (authMode === "LOGIN") {
            authMode = "SIGNUP";
            document.getElementById('auth-title').innerText = "Create an Account";
            document.getElementById('auth-subtitle').innerText = "Sign up to create your Airbeats account.";
            inputName.style.display = "block";
            btnEmail.innerText = "Sign Up";
            document.getElementById('auth-toggle-text').innerText = "Already have an account?";
            btnToggle.innerText = "Sign In";
        } else {
            authMode = "LOGIN";
            document.getElementById('auth-title').innerText = "Welcome to Airbeats";
            document.getElementById('auth-subtitle').innerText = "Sign in to your account.";
            inputName.style.display = "none";
            btnEmail.innerText = "Sign In";
            document.getElementById('auth-toggle-text').innerText = "Don't have an account?";
            btnToggle.innerText = "Sign Up";
        }
    });

    function showError(msg) {
        errorDiv.innerText = msg;
        errorDiv.style.display = 'block';
        btnEmail.innerText = authMode === "LOGIN" ? "Sign In" : "Sign Up";
        btnEmail.disabled = false;
    }

    btnEmail.addEventListener('click', async () => {
        const email = inputEmail.value.trim();
        const password = inputPassword.value;
        const name = inputName.value.trim();
        window._auth_provided_name = name || email.split('@')[0];
        
        if (!email || !password) return showError("Please enter email and password.");
        if (authMode === "SIGNUP" && !name) return showError("Please enter your name.");
        
        errorDiv.style.display = 'none';
        btnEmail.innerText = "Please wait...";
        btnEmail.disabled = true;

        try {
            const endpoint = authMode === "LOGIN" ? "login" : "signup";
            const body = authMode === "LOGIN" ? { email, password } : { email, password, name };
            
            const res = await fetch(`/api/auth/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            const data = await res.json();
            if (data.success || data.user) {
                localStorage.setItem('auth_state', 'logged_in');
                localStorage.setItem('auth_email', email);
                window.isGuestMode = false;
                
                // Auto-onboard stats if missing
                if (!localStorage.getItem('airbeats_user_name') && window._auth_provided_name) {
                    try {
                        const onboardRes = await fetch('/api/stats/onboard', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ name: window._auth_provided_name })
                        });
                        const onboardData = await onboardRes.json();
                        if (onboardData.userId) {
                            localStorage.setItem('airbeats_user_id', onboardData.userId);
                            localStorage.setItem('airbeats_user_name', onboardData.name);
                            localStorage.setItem('airbeats_user_avatar', onboardData.profileUrl);
                        }
                    } catch (e) {
                        console.error('Auto-onboard failed', e);
                    }
                }
                overlay.style.display = 'none';
                window.location.reload();
            } else {
                showError(data.error || "Authentication failed.");
            }
        } catch (err) {
            showError("Network error. Please try again.");
        }
    });

    btnGuest.addEventListener('click', () => {
        localStorage.setItem('auth_state', 'guest');
        window.isGuestMode = true;
        overlay.style.display = 'none';
    });
});

window.logoutUser = function() {
    localStorage.removeItem('auth_state');
    localStorage.removeItem('auth_email');
    window.location.reload();
};
