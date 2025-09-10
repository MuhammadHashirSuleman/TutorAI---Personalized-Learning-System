import { useEffect } from 'react';

const FormSecurityHeaders = () => {
  useEffect(() => {
    // Prevent form data caching and persistence
    const preventFormCaching = () => {
      // Set cache control headers via meta tags
      const metaTags = [
        { name: 'Cache-Control', content: 'no-cache, no-store, must-revalidate' },
        { name: 'Pragma', content: 'no-cache' },
        { name: 'Expires', content: '0' },
        { 'http-equiv': 'Cache-Control', content: 'no-cache, no-store, must-revalidate' },
        { 'http-equiv': 'Pragma', content: 'no-cache' },
        { 'http-equiv': 'Expires', content: '0' },
      ];

      metaTags.forEach(tag => {
        const meta = document.createElement('meta');
        Object.entries(tag).forEach(([key, value]) => {
          meta.setAttribute(key, value);
        });
        document.head.appendChild(meta);
      });
    };

    // Clear form data on page unload
    const clearFormData = () => {
      document.querySelectorAll('form[autocomplete="off"]').forEach(form => {
        form.reset();
        form.querySelectorAll('input').forEach(input => {
          input.value = '';
          input.removeAttribute('value');
        });
      });
    };

    // Add event listeners to prevent form data persistence
    const preventPersistence = () => {
      // Clear on page unload
      window.addEventListener('beforeunload', clearFormData);
      window.addEventListener('unload', clearFormData);
      window.addEventListener('pagehide', clearFormData);

      // Clear on visibility change (tab switching)
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
          clearFormData();
        }
      });

      // Prevent right-click context menu on forms
      document.addEventListener('contextmenu', (e) => {
        if (e.target.closest('form[autocomplete="off"]')) {
          e.preventDefault();
        }
      });

      // Prevent copy/paste on sensitive fields
      document.addEventListener('copy', (e) => {
        if (e.target.closest('input[type="password"], input[name*="password"]')) {
          e.preventDefault();
        }
      });

      // Clear clipboard after form submission
      document.addEventListener('submit', () => {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText('').catch(() => {});
        }
      });
    };

    // Disable browser password saving prompts
    const disablePasswordSaving = () => {
      // Override form submission to prevent browser password saving
      document.addEventListener('submit', (e) => {
        if (e.target.getAttribute('autocomplete') === 'off') {
          // Add hidden fields to confuse password managers
          const hiddenEmail = document.createElement('input');
          hiddenEmail.type = 'email';
          hiddenEmail.name = 'fake_email_' + Math.random();
          hiddenEmail.style.display = 'none';
          hiddenEmail.tabIndex = -1;
          e.target.appendChild(hiddenEmail);

          const hiddenPassword = document.createElement('input');
          hiddenPassword.type = 'password';
          hiddenPassword.name = 'fake_password_' + Math.random();
          hiddenPassword.style.display = 'none';
          hiddenPassword.tabIndex = -1;
          e.target.appendChild(hiddenPassword);
        }
      });
    };

    // Initialize all security measures
    preventFormCaching();
    preventPersistence();
    disablePasswordSaving();

    // Cleanup function
    return () => {
      window.removeEventListener('beforeunload', clearFormData);
      window.removeEventListener('unload', clearFormData);
      window.removeEventListener('pagehide', clearFormData);
    };
  }, []);

  return null; // This component doesn't render anything
};

export default FormSecurityHeaders;
