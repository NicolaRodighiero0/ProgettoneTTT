console.clear(); // Pulisce la console per evitare confusione nei log

// Ottiene i riferimenti agli elementi di titolo "login" e "signup"
const loginBtn = document.getElementById('login');
const signupBtn = document.getElementById('signup');

// Listener per il click sul bottone di login
loginBtn.addEventListener('click', (e) => {
    let parent = e.target.closest('.login');
    
    // Se il form di login è già visibile, lo nasconde e mostra signup
    if (!parent.classList.contains('slide-up')) {
        parent.classList.add('slide-up');
        signupBtn.closest('.signup').classList.remove('slide-up');
        document.querySelector('.signup-container').classList.remove('slide-up');
    } else {
        // Altrimenti, lo mostra e nasconde il signup
        signupBtn.closest('.signup').classList.add('slide-up');
        document.querySelector('.signup-container').classList.add('slide-up');
        parent.classList.remove('slide-up');
    }
});

// Listener per il click sul bottone di signup
signupBtn.addEventListener('click', (e) => {
    let parent = e.target.closest('.signup');
    
    // Se signup è già visibile, lo nasconde e mostra login
    if (!parent.classList.contains('slide-up')) {
        parent.classList.add('slide-up');
        document.querySelector('.signup-container').classList.add('slide-up');
        document.querySelector('.login').classList.remove('slide-up');
    } else {
        // Altrimenti, lo mostra e nasconde login
        document.querySelector('.login').classList.add('slide-up');
        parent.classList.remove('slide-up');
        document.querySelector('.signup-container').classList.remove('slide-up');
    }
});
  