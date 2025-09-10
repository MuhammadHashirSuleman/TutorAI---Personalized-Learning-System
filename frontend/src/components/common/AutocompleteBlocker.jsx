import { useEffect } from 'react';
import { Box } from '@mui/material';

const AutocompleteBlocker = () => {
  useEffect(() => {
    // Add global CSS to block all autocomplete dropdowns
    const style = document.createElement('style');
    style.textContent = `
      /* Hide all autocomplete dropdowns */
      input:-webkit-autofill,
      input:-webkit-autofill:hover,
      input:-webkit-autofill:focus,
      input:-webkit-autofill:active {
        transition: background-color 5000s ease-in-out 0s !important;
        -webkit-box-shadow: 0 0 0px 1000px white inset !important;
        -webkit-text-fill-color: black !important;
      }

      /* Hide browser suggestions dropdown */
      input[type="email"]::-webkit-contacts-auto-fill-button,
      input[type="text"]::-webkit-contacts-auto-fill-button,
      input[type="password"]::-webkit-credentials-auto-fill-button {
        visibility: hidden;
        display: none !important;
        pointer-events: none;
        position: absolute;
        right: 0;
      }

      /* Hide password manager overlays */
      input[data-lpignore="true"],
      input[data-1p-ignore="true"],
      input[data-bitwarden-watching="1"] {
        background-image: none !important;
        background-attachment: scroll !important;
      }

      /* Hide browser suggestion dropdowns */
      .MuiTextField-root input::-webkit-list-button {
        display: none;
      }

      /* Hide autofill background */
      .MuiTextField-root input:-webkit-autofill {
        -webkit-box-shadow: 0 0 0 1000px white inset !important;
        box-shadow: 0 0 0 1000px white inset !important;
        -webkit-text-fill-color: black !important;
        background-color: white !important;
        background-image: none !important;
      }

      /* Hide suggestion containers */
      input::-webkit-outer-spin-button,
      input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
      }

      /* Force hide all browser autocomplete UI */
      input[autocomplete="off"] {
        background-image: none !important;
        background-attachment: scroll !important;
        background-repeat: no-repeat !important;
        background-size: 16px 18px !important;
        background-position: 98% 50% !important;
      }

      /* Hide specific browser autocomplete icons */
      input::-ms-clear,
      input::-ms-reveal {
        display: none;
        width: 0;
        height: 0;
      }

      /* Block all suggestions */
      .MuiAutocomplete-popper {
        display: none !important;
      }

      /* Prevent form recognition by password managers */
      form[autocomplete="off"] input {
        font-family: monospace !important;
      }

      form[autocomplete="off"] input:focus {
        font-family: inherit !important;
      }

      /* Hide Chrome's save password dropdown */
      .save-password-overlay,
      .__web-inspector-hide-shortcut__ {
        display: none !important;
        visibility: hidden !important;
      }
    `;
    
    document.head.appendChild(style);

    // Add additional JavaScript-based blocking
    const blockAutocomplete = (e) => {
      if (e.target.getAttribute('autocomplete') === 'off') {
        e.target.setAttribute('readonly', true);
        e.target.addEventListener('focus', () => {
          e.target.removeAttribute('readonly');
        }, { once: true });
      }
    };

    // Apply to existing inputs
    document.querySelectorAll('input').forEach(input => {
      if (input.getAttribute('autocomplete') === 'off') {
        input.setAttribute('readonly', true);
        input.addEventListener('focus', () => {
          input.removeAttribute('readonly');
        }, { once: true });
      }
    });

    // Apply to new inputs
    document.addEventListener('DOMContentLoaded', () => {
      document.querySelectorAll('input').forEach(blockAutocomplete);
    });

    // Cleanup
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return (
    <Box
      sx={{
        '& input[autocomplete="off"]': {
          '&:-webkit-autofill': {
            WebkitBoxShadow: '0 0 0 1000px white inset !important',
            WebkitTextFillColor: 'black !important',
          },
        },
      }}
    />
  );
};

export default AutocompleteBlocker;
