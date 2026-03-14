document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    const body = document.body;
    
    function setActiveLink() {
        const currentPath = window.location.pathname;
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            link.classList.remove('active');
            
            if (href === currentPath) {
                link.classList.add('active');
            } else if (currentPath === '/' && href === '/') {
                link.classList.add('active');
            } else if (href !== '/' && currentPath.startsWith(href)) {
                link.classList.add('active');
            }
        });
    }
    
    function closeMenu() {
        navMenu.classList.remove('active');
        menuBtn.classList.remove('active');
        body.style.overflow = '';
    }
    
    function toggleMenu() {
        navMenu.classList.toggle('active');
        menuBtn.classList.toggle('active');
        
        if (navMenu.classList.contains('active')) {
            body.style.overflow = 'hidden';
        } else {
            body.style.overflow = '';
        }
    }
    
    if (menuBtn && navMenu) {
        menuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleMenu();
        });
    }
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            closeMenu();
        });
    });
    
    document.addEventListener('click', function(e) {
        if (navMenu.classList.contains('active') && 
            !navMenu.contains(e.target) && 
            !menuBtn.contains(e.target)) {
            closeMenu();
        }
    });
    
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMenu();
        }
    });
    
    setActiveLink();
    
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'A' && e.target.getAttribute('href') && !e.target.getAttribute('target')) {
            setTimeout(closeMenu, 100);
        }
    });
});