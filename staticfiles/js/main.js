// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (menuToggle && sidebar && overlay) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
        });

        overlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }

    // Auto-dismiss Django Messages after 5 seconds
    const messages = document.querySelectorAll('.messages li');
    if (messages.length > 0) {
        setTimeout(function() {
            messages.forEach(function(msg) {
                msg.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                setTimeout(function() {
                    msg.remove();
                }, 500);
            });
        }, 5000);
    }
});
